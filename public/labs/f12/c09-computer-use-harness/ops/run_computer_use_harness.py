from __future__ import annotations

import csv
import json
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "contracts/computer_use_policy.json"
STATES_PATH = ROOT / "data/ui_states.json"
TASKS_PATH = ROOT / "data/computer_use_tasks.json"
OUTPUT = ROOT / "output"
TRACE_CARDS = OUTPUT / "trace_cards"

SIGNATURE = "IA para gente curiosa / Facsímil 12 / Capítulo 09 / 686f6c61"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def state_observation(state_id: str, states: dict) -> dict:
    state = states[state_id]
    return {
        "state_id": state_id,
        "url": state["url"],
        "domain": state["domain"],
        "title": state["title"],
        "visible_nodes": [
            {
                "node_id": node["node_id"],
                "role": node["role"],
                "name": node["name"],
                "text": node["text"],
                "enabled": node["enabled"],
                "risk_tags": node.get("risk_tags", []),
            }
            for node in state["nodes"]
            if node.get("visible", True)
        ],
        "untrusted_texts": state.get("untrusted_texts", []),
    }


def has_untrusted_instruction(state: dict, policy: dict) -> bool:
    blob = " ".join(state.get("untrusted_texts", []) + [node.get("text", "") for node in state.get("nodes", [])]).lower()
    return any(needle.lower() in blob for needle in policy["untrusted_instruction_needles"])


def resolve_target(action: dict, state: dict, policy: dict) -> tuple[dict | None, list[str]]:
    flags = []
    target = action.get("target", {})

    if "x" in target or "y" in target:
        if not policy["quality_gates"]["allow_coordinate_clicks"]:
            return None, ["coordinate_click_blocked"]
        return {"node_id": "coordinate", "role": "coordinate", "name": f"{target.get('x')},{target.get('y')}", "risk_tags": ["coordinate"]}, flags

    if policy["quality_gates"]["require_accessibility_target"] and ("role" not in target or "name" not in target):
        return None, ["missing_accessibility_target"]

    matches = [
        node
        for node in state["nodes"]
        if node.get("visible", True)
        and node.get("enabled", True)
        and node["role"] == target.get("role")
        and node["name"] == target.get("name")
    ]
    if len(matches) == 0:
        return None, ["target_not_found"]
    if len(matches) > 1 and policy["quality_gates"]["require_unique_target"]:
        return None, ["target_ambiguous"]
    return matches[0], flags


def execute_action(action: dict, node: dict | None, state_id: str, memory: dict) -> tuple[str, dict]:
    action_type = action["type"]
    evidence = {"before_state": state_id, "after_state": state_id}

    if action_type == "type" and node:
        memory[node["node_id"]] = action.get("text", "")
        evidence["typed_into"] = node["node_id"]
        evidence["text_length"] = len(action.get("text", ""))
        return state_id, evidence

    if action_type != "click" or not node:
        evidence["noop"] = True
        return state_id, evidence

    next_state = state_id
    if state_id == "support_home" and node["node_id"] == "search":
        query = memory.get("q", "").lower()
        next_state = "support_results_beca" if "beca" in query else "support_home"
    elif state_id == "support_results_beca" and node["node_id"] == "ticket_101":
        next_state = "ticket_t101"
    elif state_id == "ticket_t101" and node["node_id"] == "draft":
        next_state = "ticket_t101_draft"

    evidence["clicked_node_id"] = node["node_id"]
    evidence["after_state"] = next_state
    return next_state, evidence


def evaluate_task(task: dict, states: dict, policy: dict) -> dict:
    current_state_id = task["initial_state"]
    steps = []
    flags = []
    memory = {}
    decision = None

    for step_number, action in enumerate(task["proposed_actions"], start=1):
        if step_number > policy["quality_gates"]["max_steps"]:
            flags.append("max_steps_exceeded")
            decision = "review"
            break

        state = states[current_state_id]
        observation = state_observation(current_state_id, states)

        if state["domain"] not in policy["environment"]["allowed_domains"]:
            flags.append("domain_not_allowed")
            decision = "block"
            break

        target_node, target_flags = resolve_target(action, state, policy)
        flags.extend(target_flags)
        if target_flags:
            steps.append(
                {
                    "step": step_number,
                    "state": current_state_id,
                    "action": action,
                    "target": None,
                    "decision": "review",
                    "flags": target_flags,
                    "observation": observation,
                }
            )
            decision = "review"
            break

        risk_tags = set(target_node.get("risk_tags", []))
        injection_seen = has_untrusted_instruction(state, policy)
        if injection_seen and policy["quality_gates"]["block_untrusted_page_instructions"] and risk_tags:
            step_flags = ["untrusted_instruction_seen", "sensitive_action_from_untrusted_context"]
            flags.extend(step_flags)
            steps.append(
                {
                    "step": step_number,
                    "state": current_state_id,
                    "action": action,
                    "target": target_node,
                    "decision": "block",
                    "flags": step_flags,
                    "observation": observation,
                }
            )
            decision = "block"
            break

        approval_tags = risk_tags & set(policy["approval_required_tags"])
        if approval_tags and not action.get("approved_by"):
            step_flags = [f"approval_required:{tag}" for tag in sorted(approval_tags)]
            flags.extend(step_flags)
            steps.append(
                {
                    "step": step_number,
                    "state": current_state_id,
                    "action": action,
                    "target": target_node,
                    "decision": "needs_approval",
                    "flags": step_flags,
                    "observation": observation,
                }
            )
            decision = "needs_approval"
            break

        next_state_id, evidence = execute_action(action, target_node, current_state_id, memory)
        steps.append(
            {
                "step": step_number,
                "state": current_state_id,
                "action": action,
                "target": target_node,
                "decision": "executed",
                "flags": [],
                "evidence": evidence,
                "observation": observation,
            }
        )
        current_state_id = next_state_id

    if decision is None:
        decision = "success" if current_state_id == task["expected_final_state"] else "review"
        if decision == "review":
            flags.append("goal_not_reached")

    metrics = {
        "steps_executed": sum(1 for step in steps if step["decision"] == "executed"),
        "steps_total": len(steps),
        "approval_count": sum(1 for step in steps if step["decision"] == "needs_approval"),
        "approval_tag_count": sum(1 for flag in flags if flag.startswith("approval_required")),
        "blocked_count": sum(1 for step in steps if step["decision"] == "block"),
        "review_count": sum(1 for step in steps if step["decision"] == "review"),
        "coordinate_action_count": sum(1 for step in steps if "coordinate_click_blocked" in step.get("flags", [])),
        "final_state": current_state_id,
        "expected_final_state": task["expected_final_state"],
        "matches_expected_decision": decision == task["expected_decision"],
    }

    return {
        "task_id": task["task_id"],
        "title": task["title"],
        "goal": task["goal"],
        "decision": decision,
        "expected_decision": task["expected_decision"],
        "steps": steps,
        "metrics": metrics,
        "flags": sorted(set(flags)),
        "limits": limits_for(decision, flags),
        "next_action": next_action(decision),
    }


def limits_for(decision: str, flags: list[str]) -> list[str]:
    limits = [
        "El laboratorio simula la interfaz; en producción debe ejecutarse en navegador, VM o contenedor aislado.",
        "Cada acción debe conservar observación, target, política y resultado.",
    ]
    if decision == "needs_approval":
        limits.append("La acción tiene consecuencia real y necesita aprobación humana antes de ejecutarse.")
    if decision == "block":
        limits.append("La página contiene contenido no confiable o pide una acción sensible.")
    if any(flag == "coordinate_click_blocked" for flag in flags):
        limits.append("El click por coordenadas no explica qué elemento se pretendía activar.")
    return limits


def next_action(decision: str) -> str:
    if decision == "success":
        return "Guardar traza y comparar con baseline en regresión."
    if decision == "needs_approval":
        return "Mostrar tarjeta de aprobación con acción, target, riesgo y evidencia."
    if decision == "block":
        return "Bloquear ejecución, registrar evidencia y revisar la fuente no confiable."
    return "Pedir revisión o mejorar el target antes de ejecutar."


def write_reports(results: list[dict], policy: dict) -> None:
    report = {
        "schema_version": "1.0",
        "project": "IA para gente curiosa",
        "fasciculo": 12,
        "capitulo": 9,
        "policy": policy,
        "summary": {
            "task_count": len(results),
            "all_expected": all(item["decision"] == item["expected_decision"] for item in results),
            "needs_approval_count": sum(item["decision"] == "needs_approval" for item in results),
            "block_count": sum(item["decision"] == "block" for item in results),
            "review_count": sum(item["decision"] == "review" for item in results),
        },
        "results": results,
    }
    (OUTPUT / "computer_use_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# Informe de computer use harness",
        "",
        "Este informe evalúa si una acción de interfaz puede ejecutarse, necesita aprobación, se revisa o se bloquea.",
        "",
        "| Tarea | Decisión | Esperada | Pasos | Flags |",
        "|---|---:|---:|---:|---|",
    ]
    for item in results:
        lines.append(
            f"| `{item['task_id']}` | `{item['decision']}` | `{item['expected_decision']}` | "
            f"{item['metrics']['steps_total']} | {', '.join(item['flags']) or 'sin flags'} |"
        )
    lines.extend(
        [
            "",
            "## Lectura de ingeniería",
            "",
            "- Un target por rol y nombre es más auditable que un click por coordenadas.",
            "- Las acciones financieras, destructivas, autenticadas o de envío externo piden aprobación.",
            "- El contenido visible en una página es dato no confiable: no debe ampliar permisos.",
            "- La traza debe registrar observación, acción, target, riesgo, decisión y estado posterior.",
        ]
    )
    (OUTPUT / "computer_use_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    with (OUTPUT / "action_eval_matrix.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "task_id",
                "decision",
                "expected_decision",
                "steps_total",
                "steps_executed",
                "approval_count",
                "approval_tag_count",
                "blocked_count",
                "review_count",
                "coordinate_action_count",
                "final_state",
                "flags",
            ],
        )
        writer.writeheader()
        for item in results:
            metrics = item["metrics"]
            writer.writerow(
                {
                    "task_id": item["task_id"],
                    "decision": item["decision"],
                    "expected_decision": item["expected_decision"],
                    "steps_total": metrics["steps_total"],
                    "steps_executed": metrics["steps_executed"],
                    "approval_count": metrics["approval_count"],
                    "approval_tag_count": metrics["approval_tag_count"],
                    "blocked_count": metrics["blocked_count"],
                    "review_count": metrics["review_count"],
                    "coordinate_action_count": metrics["coordinate_action_count"],
                    "final_state": metrics["final_state"],
                    "flags": "|".join(item["flags"]),
                }
            )


def write_svg(path: Path) -> None:
    svg = f'''<svg viewBox="0 0 1180 760" role="img" aria-labelledby="f12c09-title f12c09-desc" xmlns="http://www.w3.org/2000/svg">
  <title id="f12c09-title">Arnés de computer use con permisos</title>
  <desc id="f12c09-desc">Loop de observación, propuesta de acción, policy gate, ejecución, nueva observación y evaluación.</desc>
  <defs>
    <marker id="f12c09-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L0,6 L9,3 z" fill="#111111"/>
    </marker>
  </defs>
  <rect width="1180" height="760" fill="#FFFFFF"/>
  <text x="62" y="58" font-size="28" font-weight="700" fill="#111111">Computer use: ver, decidir, pedir permiso, actuar</text>
  <text x="62" y="88" font-size="15" fill="#555555">El modelo no toca el mundo directamente: propone acciones que pasan por un arnés auditable.</text>

  <rect x="58" y="142" width="204" height="330" fill="#FFFFFF" stroke="#111111" stroke-width="1.5"/>
  <text x="160" y="174" text-anchor="middle" font-size="15" font-weight="700" fill="#111111">Observación</text>
  <line x1="84" y1="196" x2="236" y2="196" stroke="#111111"/>
  <text x="90" y="234" font-size="12" fill="#111111">screenshot</text>
  <text x="90" y="264" font-size="12" fill="#111111">DOM / accessibility tree</text>
  <text x="90" y="294" font-size="12" fill="#111111">URL · título · foco</text>
  <text x="90" y="324" font-size="12" fill="#111111">texto no confiable</text>

  <rect x="326" y="142" width="204" height="330" fill="#F7F7F7" stroke="#111111" stroke-width="1.5"/>
  <text x="428" y="174" text-anchor="middle" font-size="15" font-weight="700" fill="#111111">Propuesta</text>
  <line x1="352" y1="196" x2="504" y2="196" stroke="#111111"/>
  <text x="358" y="234" font-size="12" fill="#111111">click · type · scroll</text>
  <text x="358" y="264" font-size="12" fill="#111111">target role/name</text>
  <text x="358" y="294" font-size="12" fill="#111111">argumentos</text>
  <text x="358" y="324" font-size="12" fill="#111111">razón de acción</text>

  <rect x="594" y="142" width="224" height="330" fill="#FFFFFF" stroke="#111111" stroke-width="1.5"/>
  <text x="706" y="174" text-anchor="middle" font-size="15" font-weight="700" fill="#111111">Policy gate</text>
  <line x1="620" y1="196" x2="792" y2="196" stroke="#111111"/>
  <text x="626" y="234" font-size="12" fill="#111111">dominio permitido</text>
  <text x="626" y="264" font-size="12" fill="#111111">target único</text>
  <text x="626" y="294" font-size="12" fill="#111111">riesgo y aprobación</text>
  <text x="626" y="324" font-size="12" fill="#111111">inyección visual/web</text>
  <rect x="626" y="360" width="158" height="54" fill="#111111" stroke="#111111"/>
  <text x="705" y="383" text-anchor="middle" font-size="11" font-weight="700" fill="#FFFFFF">Decisión</text>
  <text x="705" y="402" text-anchor="middle" font-size="10" fill="#FFFFFF">execute · approve · block</text>

  <rect x="884" y="142" width="220" height="330" fill="#F7F7F7" stroke="#111111" stroke-width="1.5"/>
  <text x="994" y="174" text-anchor="middle" font-size="15" font-weight="700" fill="#111111">Ejecución</text>
  <line x1="910" y1="196" x2="1078" y2="196" stroke="#111111"/>
  <text x="916" y="234" font-size="12" fill="#111111">browser / VM / app</text>
  <text x="916" y="264" font-size="12" fill="#111111">nueva observación</text>
  <text x="916" y="294" font-size="12" fill="#111111">traza y replay</text>
  <text x="916" y="324" font-size="12" fill="#111111">métricas de tarea</text>

  <line x1="262" y1="310" x2="324" y2="310" stroke="#111111" stroke-width="1.7" marker-end="url(#f12c09-arrow)"/>
  <line x1="530" y1="310" x2="592" y2="310" stroke="#111111" stroke-width="1.7" marker-end="url(#f12c09-arrow)"/>
  <line x1="818" y1="310" x2="882" y2="310" stroke="#111111" stroke-width="1.7" marker-end="url(#f12c09-arrow)"/>
  <path d="M994 472 C994 560 160 560 160 474" fill="none" stroke="#111111" stroke-width="1.5" marker-end="url(#f12c09-arrow)"/>

  <rect x="138" y="620" width="904" height="72" fill="#FFFFFF" stroke="#111111" stroke-width="1.2"/>
  <text x="164" y="650" font-size="13" font-weight="700" fill="#111111">Regla práctica</text>
  <text x="164" y="674" font-size="13" fill="#111111">La página puede proponer, el modelo puede pedir, pero el arnés decide qué se ejecuta.</text>
  <text x="1092" y="724" text-anchor="end" font-size="11" fill="#999999">{SIGNATURE}</text>
</svg>
'''
    path.write_text(svg, encoding="utf-8")


def main() -> None:
    policy = load_json(POLICY_PATH)
    states = load_json(STATES_PATH)
    tasks = load_json(TASKS_PATH)
    OUTPUT.mkdir(exist_ok=True)
    TRACE_CARDS.mkdir(exist_ok=True)

    results = []
    for task in tasks:
        result = evaluate_task(task, states, policy)
        results.append(result)
        (TRACE_CARDS / f"{task['task_id']}.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    write_reports(results, policy)
    write_svg(OUTPUT / "computer_use_harness.svg")
    print(f"OK: {len(results)} tareas de computer use evaluadas en {OUTPUT}")


if __name__ == "__main__":
    main()
