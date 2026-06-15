#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "output"
DATA_DIR = ROOT / "data"
CONTRACT_DIR = ROOT / "contracts"


def load_json(path):
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


CASES = load_json(DATA_DIR / "practice_cases.json")
POLICY = load_json(CONTRACT_DIR / "practice_policy.json")


def case_for(chapter_id):
    return CASES.get(chapter_id, {})


def policy_for(chapter_id):
    return POLICY.get("chapter_expectations", {}).get(chapter_id, {})


def check(name, passed, detail):
    return {"name": name, "passed": bool(passed), "detail": detail}


def status(checks):
    return "valid" if all(item["passed"] for item in checks) else "invalid"


def write_outputs(chapter_id, report):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = OUTPUT_DIR / f"{chapter_id}_report.json"
    decision_path = OUTPUT_DIR / f"{chapter_id}_decision.md"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    lines = [
        f"# Decisión {chapter_id.upper()}: {report['title']}",
        "",
        f"Estado: `{report['status']}`.",
        "",
        "## Evidencias",
        "",
    ]
    for item in report["checks"]:
        mark = "OK" if item["passed"] else "FALLO"
        lines.append(f"- {mark}: {item['name']}. {item['detail']}")
    if report.get("what_you_take"):
        lines.extend(["", "## Qué te llevas", "", report["what_you_take"]])
    lines.extend(["", "## Decisión", "", report["decision"], ""])
    decision_path.write_text("\n".join(lines), encoding="utf-8")


def c01_manifest():
    data = case_for("c01")
    chapter_policy = policy_for("c01")
    manifest = data.get("manifest", {
        "name": "matricula-support-agent",
        "goal": "Resolver consultas de matrícula sin ejecutar acciones persistentes sin aprobación.",
        "budget": {"max_steps": 6, "max_tool_calls": 4, "max_cost_eur": 0.08},
        "memory": {
            "prompt_context": ["instrucciones", "petición_usuario", "evidencia_recuperada"],
            "session_state": ["case_id", "steps", "observations", "approvals"],
            "persistent_memory": ["policy_version", "preferred_tone"],
        },
        "tools": {
            "buscar_politica": {"permission": "allow", "side_effect": "none", "timeout_ms": 900},
            "consultar_saldo": {"permission": "authenticated_read", "side_effect": "none", "timeout_ms": 1200},
            "crear_ticket": {"permission": "approval_required", "side_effect": "persistent_write", "timeout_ms": 1500},
        },
        "stop_rules": ["done", "approval_required", "blocked", "budget_exhausted"],
    })
    checks = [
        check("manifest declara objetivo", bool(manifest["goal"]), "El objetivo se puede revisar sin leer código."),
        check("tools tienen permisos", all("permission" in tool for tool in manifest["tools"].values()), "Cada herramienta declara su permiso."),
        check("acciones persistentes requieren aprobación", manifest["tools"]["crear_ticket"]["permission"] == "approval_required", "La escritura no queda en manos del modelo."),
        check("hay presupuesto operativo", manifest["budget"]["max_steps"] <= chapter_policy.get("max_steps", 8) and 0 < manifest["budget"]["max_cost_eur"] <= chapter_policy.get("max_cost_eur", 0.1), "La autonomía tiene límite medible."),
        check("memoria separa contexto, sesión y persistencia", set(manifest["memory"]) == {"prompt_context", "session_state", "persistent_memory"}, "La memoria no se confunde con prompt largo."),
    ]
    return {
        "title": "Manifest operativo de agente",
        "artifact": manifest,
        "checks": checks,
        "status": status(checks),
        "what_you_take": chapter_policy.get("what_you_take"),
        "decision": "El agente puede pasar de idea a diseño: tiene objetivo, tools, permisos, memoria y presupuesto antes de escribir una integración real.",
    }


def c02_loop():
    data = case_for("c02")
    chapter_policy = policy_for("c02")
    transitions = data.get("transitions", [
        {"state": "CREATED", "action": "classify_intent", "observation": "needs_policy", "next_state": "PLANNING"},
        {"state": "PLANNING", "action": "buscar_politica", "observation": "policy_found", "next_state": "TOOL_CALLING"},
        {"state": "TOOL_CALLING", "action": "preparar_respuesta", "observation": "draft_ready", "next_state": "WAITING_APPROVAL"},
        {"state": "WAITING_APPROVAL", "action": "human_approve", "observation": "approved", "next_state": "COMPLETED"},
    ])
    budget = data.get("budget", {"max_steps": 6, "max_tool_calls": 3})
    budget = {**budget, "used_steps": len(transitions), "used_tool_calls": sum(1 for item in transitions if item["action"].startswith(("buscar_", "consultar_", "crear_")))}
    checks = [
        check("hay trayectoria", len(transitions) >= chapter_policy.get("minimum_transitions", 3), "La práctica no evalúa solo respuesta final."),
        check("cada paso tiene acción y observación", all(t["action"] and t["observation"] for t in transitions), "El bucle agente es observable."),
        check("la parada es explícita", transitions[-1]["next_state"] == chapter_policy.get("terminal_state", "COMPLETED"), "La run no queda abierta por inercia."),
        check("presupuesto respetado", budget["used_steps"] <= budget["max_steps"] and budget["used_tool_calls"] <= budget["max_tool_calls"], "El agente no tiene autonomía infinita."),
    ]
    return {
        "title": "Bucle estado-acción-observación",
        "artifact": {"transitions": transitions, "budget": budget},
        "checks": checks,
        "status": status(checks),
        "what_you_take": chapter_policy.get("what_you_take"),
        "decision": "El bucle es apto para enseñar agentes: cada acción produce una observación, consume presupuesto y termina por regla.",
    }


def c03_tool_contract():
    data = case_for("c03")
    chapter_policy = policy_for("c03")
    tool = data.get("tool", {
        "name": "consultar_saldo",
        "input_schema": {"required": ["case_id"], "types": {"case_id": "string"}},
        "output_schema": {"required": ["pending_eur", "currency"], "types": {"pending_eur": "number", "currency": "string"}},
        "permission": "authenticated_read",
        "side_effect": "none",
        "timeouts_ms": {"connect": 250, "read": 1000},
        "errors": ["not_found", "forbidden", "timeout", "schema_invalid"],
        "trace_events": ["tool.call", "tool.result", "tool.error"],
    })
    checks = [
        check("schema de entrada completo", "case_id" in tool["input_schema"]["required"], "La tool no acepta texto libre como contrato."),
        check("schema de salida completo", "pending_eur" in tool["output_schema"]["required"], "La observación vuelve estructurada."),
        check("permiso explícito", tool["permission"] == "authenticated_read", "La tool declara su frontera de acceso."),
        check("errores nombrados", len(tool["errors"]) >= chapter_policy.get("required_errors", 4), "El agente puede distinguir fallo de negocio y fallo técnico."),
        check("trazas nombradas", {"tool.call", "tool.result"}.issubset(tool["trace_events"]), "La ejecución se puede reconstruir."),
    ]
    return {
        "title": "Contrato operativo de tool",
        "artifact": tool,
        "checks": checks,
        "status": status(checks),
        "what_you_take": chapter_policy.get("what_you_take"),
        "decision": "La tool puede integrarse en un agente: no depende de una descripción bonita, sino de schema, permisos, errores y trazas.",
    }


def c04_handoff():
    data = case_for("c04")
    chapter_policy = policy_for("c04")
    handoff = data.get("handoff", {
        "handoff_id": "hf-2026-06-10-001",
        "objective": "Continuar revisión de capítulo con mismas normas editoriales.",
        "must_keep": ["criterios editoriales", "rutas tocadas", "decisiones pendientes"],
        "must_not_keep": ["logs completos", "secretos", "capturas no usadas"],
        "artifacts": [
            {"path": "fasciculo-05-agentes-orquestacion/04-contexto-memoria-compaction-handoff.md", "hash": "demo"},
            {"path": "labs/f5/capitulo-practicas/output/c04_report.json", "hash": "demo"},
        ],
        "token_budget": {"raw_tokens": 4200, "handoff_tokens": 780},
    })
    compression_ratio = round(handoff["token_budget"]["handoff_tokens"] / handoff["token_budget"]["raw_tokens"], 3)
    checks = [
        check("objetivo presente", bool(handoff["objective"]), "Otra persona sabría qué continuar."),
        check("separa conservar y descartar", bool(handoff["must_keep"]) and bool(handoff["must_not_keep"]), "Compaction no es copiar todo."),
        check("artefactos referenciados", len(handoff["artifacts"]) >= 2, "El handoff apunta a objetos verificables."),
        check("reduce tokens", compression_ratio < chapter_policy.get("max_compression_ratio", 0.25), f"Compresión estimada: {compression_ratio}."),
    ]
    return {
        "title": "Handoff operativo con compaction",
        "artifact": {"handoff": handoff, "compression_ratio": compression_ratio},
        "checks": checks,
        "status": status(checks),
        "what_you_take": chapter_policy.get("what_you_take"),
        "decision": "El handoff es usable: conserva intención, evidencia y límites, no una transcripción enorme imposible de auditar.",
    }


def c05_architecture_decision():
    data = case_for("c05")
    chapter_policy = policy_for("c05")
    options = data.get("options", {
        "workflow": {"predictability": 5, "flexibility": 2, "auditability": 5, "latency": 4},
        "react": {"predictability": 3, "flexibility": 4, "auditability": 3, "latency": 3},
        "planner_executor": {"predictability": 4, "flexibility": 4, "auditability": 4, "latency": 2},
        "multiagent": {"predictability": 2, "flexibility": 5, "auditability": 2, "latency": 1},
    })
    weights = data.get("weights", {"predictability": 0.35, "flexibility": 0.2, "auditability": 0.3, "latency": 0.15})
    scores = {
        name: round(sum(values[k] * weights[k] for k in weights), 2)
        for name, values in options.items()
    }
    choice = max(scores, key=scores.get)
    checks = [
        check("opciones comparadas", len(scores) >= 4, "No se elige arquitectura por nombre de moda."),
        check("pesos explícitos", round(sum(weights.values()), 2) == 1.0, "La decisión declara qué importa."),
        check("workflow gana para caso regulado", choice == chapter_policy.get("expected_choice", "workflow"), "La trazabilidad pesa más que la flexibilidad."),
        check("queda alternativa", scores["planner_executor"] >= chapter_policy.get("minimum_alternative_score", 3.5), "Hay plan si aumenta complejidad multi-paso."),
    ]
    return {
        "title": "Decision record de arquitectura agentic",
        "artifact": {"weights": weights, "scores": scores, "choice": choice},
        "checks": checks,
        "status": status(checks),
        "what_you_take": chapter_policy.get("what_you_take"),
        "decision": "Para un proceso académico con permisos y trazas, la recomendación inicial es workflow; si aparecen tareas abiertas, se reevalúa planner-executor.",
    }


def c06_harness():
    data = case_for("c06")
    chapter_policy = policy_for("c06")
    run = data.get("run", {
        "limits": {"max_steps": 8, "max_tool_calls": 6, "max_seconds": 20},
        "sensors": ["tokens_in", "tokens_out", "tool_count", "latency_ms", "policy_decision", "trace_complete"],
        "trace": ["run.started", "model.request", "tool.call", "tool.result", "gate.checked", "run.completed"],
        "redactions": ["email", "student_id", "free_text_secret"],
    })
    checks = [
        check("límites presentes", all(v > 0 for v in run["limits"].values()), "El harness corta bucles caros."),
        check("sensores operativos", len(run["sensors"]) >= chapter_policy.get("minimum_sensors", 6), "No mide solo tokens."),
        check("traza completa", {"tool.call", "tool.result", "gate.checked", "run.completed"}.issubset(run["trace"]), "La ejecución es depurable."),
        check("redacción de datos", "student_id" in run["redactions"], "La observabilidad no debe filtrar datos sensibles."),
    ]
    return {
        "title": "Harness reproducible",
        "artifact": run,
        "checks": checks,
        "status": status(checks),
        "what_you_take": chapter_policy.get("what_you_take"),
        "decision": "El harness permite ejecutar un agente con límites, sensores y trazas sin convertir los logs en otra fuente de riesgo.",
    }


def c07_sdk_contract():
    data = case_for("c07")
    chapter_policy = policy_for("c07")
    portable_contract = data.get("portable_contract", {
        "request": ["task", "context_refs", "tools_allowed", "output_schema", "budget"],
        "events": ["model.delta", "tool.call", "tool.result", "handoff", "approval.requested", "run.completed"],
        "providers": {
            "openai_agents": ["agent", "runner", "tools", "handoffs", "tracing"],
            "anthropic": ["messages", "tool_use", "tool_result", "permissions", "subagents"],
            "google_adk": ["agent", "tools", "sessions", "artifacts", "a2a"],
        },
    })
    required_providers = set(chapter_policy.get("required_providers", ["openai_agents", "anthropic", "google_adk"]))
    checks = [
        check("contrato portable", "output_schema" in portable_contract["request"], "La app habla su idioma antes del SDK."),
        check("eventos normalizados", "tool.call" in portable_contract["events"] and "run.completed" in portable_contract["events"], "Las trazas se comparan entre proveedores."),
        check("tres familias cubiertas", required_providers.issubset(portable_contract["providers"]), "OpenAI, Anthropic y ADK se tratan como adaptadores."),
        check("no delega permisos al SDK", "tools_allowed" in portable_contract["request"], "La política vive fuera del proveedor."),
    ]
    return {
        "title": "Contrato antes del SDK",
        "artifact": portable_contract,
        "checks": checks,
        "status": status(checks),
        "what_you_take": chapter_policy.get("what_you_take"),
        "decision": "La integración es portable: se puede cambiar proveedor sin reescribir política, salida esperada ni evaluación de eventos.",
    }


def c08_permission_engine():
    data = case_for("c08")
    chapter_policy = policy_for("c08")
    actions = data.get("actions", [
        {"action": "read_policy", "risk": "low", "decision": "allow"},
        {"action": "read_balance", "risk": "private_read", "decision": "allow_if_authenticated"},
        {"action": "create_ticket", "risk": "persistent_write", "decision": "approval_required"},
        {"action": "send_email", "risk": "external_effect", "decision": "approval_required"},
    ])
    approval_queue = [a for a in actions if a["decision"] == "approval_required"]
    checks = [
        check("acciones clasificadas", all("risk" in a for a in actions), "No todas las tools tienen el mismo riesgo."),
        check("escrituras con aprobación", all(a["decision"] == "approval_required" for a in actions if "write" in a["risk"] or a["risk"] == "external_effect"), "El modelo no ejecuta efectos externos sin revisión."),
        check("cola de aprobación no vacía", len(approval_queue) == 2, "El sistema separa decisión y ejecución."),
        check("lectura privada exige autenticación", actions[1]["decision"] == "allow_if_authenticated", "Privacidad no es un comentario, es una regla."),
    ]
    return {
        "title": "Motor de permisos",
        "artifact": {"actions": actions, "approval_queue": approval_queue},
        "checks": checks,
        "status": status(checks),
        "what_you_take": chapter_policy.get("what_you_take"),
        "decision": "La autonomía queda graduada: leer, escribir y enviar no comparten permisos ni la misma ruta de aprobación.",
    }


def c09_router():
    data = case_for("c09")
    chapter_policy = policy_for("c09")
    requests = data.get("requests", [
        {"text": "resume política de matrícula", "route": "local_tool"},
        {"text": "consulta expediente autenticado", "route": "mcp_tool"},
        {"text": "coordina revisión con agente de citas", "route": "a2a"},
        {"text": "publica cambio en producción", "route": "human_review"},
        {"text": "ejecuta flujo de admisiones", "route": "workflow_graph"},
    ])
    allowed_routes = set(data.get("allowed_routes", ["local_tool", "mcp_tool", "a2a", "human_review", "workflow_graph"]))
    checks = [
        check("rutas válidas", all(r["route"] in allowed_routes for r in requests), "Cada decisión cae en una interfaz conocida."),
        check("efectos externos revisados", next(r for r in requests if "producción" in r["text"])["route"] == "human_review", "Publicar no se enruta a autonomía directa."),
        check("A2A solo cuando coordina agente", next(r for r in requests if "agente" in r["text"])["route"] == "a2a", "A2A no sustituye una tool simple."),
        check("workflow para proceso estable", requests[-1]["route"] == "workflow_graph", "Lo repetible se modela como grafo, no improvisación."),
    ]
    return {
        "title": "Router interoperable",
        "artifact": {"requests": requests, "allowed_routes": sorted(allowed_routes)},
        "checks": checks,
        "status": status(checks),
        "what_you_take": chapter_policy.get("what_you_take"),
        "decision": "El router no elige por marca: elige por contrato, riesgo, necesidad de coordinación y estabilidad del proceso.",
    }


def c10_eval_gate():
    data = case_for("c10")
    chapter_policy = policy_for("c10")
    runs = data.get("runs", [
        {"id": "r1", "route_ok": True, "tools_ok": True, "approval_ok": True, "trace_ok": True, "cost_eur": 0.03, "latency_ms": 1800},
        {"id": "r2", "route_ok": True, "tools_ok": True, "approval_ok": True, "trace_ok": True, "cost_eur": 0.05, "latency_ms": 2400},
        {"id": "r3", "route_ok": True, "tools_ok": True, "approval_ok": True, "trace_ok": True, "cost_eur": 0.04, "latency_ms": 2100},
    ])
    metrics = {
        "route_accuracy": sum(r["route_ok"] for r in runs) / len(runs),
        "tool_pass_rate": sum(r["tools_ok"] for r in runs) / len(runs),
        "approval_pass_rate": sum(r["approval_ok"] for r in runs) / len(runs),
        "trace_complete_rate": sum(r["trace_ok"] for r in runs) / len(runs),
        "p95_latency_ms": max(r["latency_ms"] for r in runs),
        "max_cost_eur": max(r["cost_eur"] for r in runs),
    }
    gates = {
        "route_accuracy": metrics["route_accuracy"] >= chapter_policy.get("min_route_accuracy", 0.95),
        "tool_pass_rate": metrics["tool_pass_rate"] >= 0.95,
        "approval_pass_rate": metrics["approval_pass_rate"] == 1.0,
        "trace_complete_rate": metrics["trace_complete_rate"] == 1.0,
        "latency": metrics["p95_latency_ms"] <= chapter_policy.get("max_latency_ms", 3000),
        "cost": metrics["max_cost_eur"] <= chapter_policy.get("max_cost_eur", 0.08),
    }
    checks = [
        check("métricas de trayectoria", all(k in metrics for k in ["route_accuracy", "tool_pass_rate", "trace_complete_rate"]), "No se mira solo la respuesta final."),
        check("gates pasan", all(gates.values()), "La versión puede avanzar a canary."),
        check("coste limitado", metrics["max_cost_eur"] <= 0.08, "El gate incluye presupuesto."),
        check("latencia limitada", metrics["p95_latency_ms"] <= 3000, "El gate incluye experiencia de usuario."),
    ]
    return {
        "title": "Evaluación de agentes y gates",
        "artifact": {"runs": runs, "metrics": metrics, "gates": gates},
        "checks": checks,
        "status": status(checks),
        "what_you_take": chapter_policy.get("what_you_take"),
        "decision": "La versión puede pasar a canary: ruta, tools, aprobación, trazas, coste y latencia cumplen el contrato mínimo.",
    }


BUILDERS = {
    "c01": c01_manifest,
    "c02": c02_loop,
    "c03": c03_tool_contract,
    "c04": c04_handoff,
    "c05": c05_architecture_decision,
    "c06": c06_harness,
    "c07": c07_sdk_contract,
    "c08": c08_permission_engine,
    "c09": c09_router,
    "c10": c10_eval_gate,
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--chapter", choices=sorted(BUILDERS), help="Capítulo a ejecutar, por ejemplo c03.")
    parser.add_argument("--all", action="store_true", help="Ejecuta todos los capítulos.")
    parser.add_argument("--write", action="store_true", help="Escribe outputs en disco.")
    parser.add_argument("--fail-on-invalid", action="store_true", help="Termina con error si alguna práctica no valida.")
    args = parser.parse_args()

    selected = sorted(BUILDERS) if args.all or not args.chapter else [args.chapter]
    summary = {}
    invalid = []
    for chapter_id in selected:
        report = BUILDERS[chapter_id]()
        report["chapter"] = chapter_id
        summary[chapter_id] = report["status"]
        if report["status"] != "valid":
            invalid.append(chapter_id)
        if args.write:
            write_outputs(chapter_id, report)

    if args.write:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        (OUTPUT_DIR / "all_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    if invalid and args.fail_on_invalid:
        raise SystemExit(f"Prácticas inválidas: {', '.join(invalid)}")


if __name__ == "__main__":
    main()
