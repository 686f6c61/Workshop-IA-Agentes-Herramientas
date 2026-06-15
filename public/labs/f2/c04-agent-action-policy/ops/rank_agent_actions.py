#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def eligibility(action, state, policy):
    reasons = []
    hard_rules = policy["hard_rules"]
    budgets = policy["budgets"]

    if action["estimated_tokens"] > budgets["max_estimated_tokens"]:
        reasons.append("supera presupuesto de tokens")
    if action["estimated_latency_seconds"] > budgets["max_latency_seconds"]:
        reasons.append("supera presupuesto de latencia")
    if action["risk"] > hard_rules["max_risk_without_approval"] and not state["has_approval_for_destructive_changes"]:
        reasons.append("riesgo alto sin aprobación")
    if (
        hard_rules["require_evidence_before_destructive_action"]
        and action["destructive"]
        and state["evidence_count"] == 0
    ):
        reasons.append("acción destructiva sin evidencia previa")
    if (
        hard_rules["require_permission_for_sensitive_data"]
        and action["sensitive_data"]
        and not state["has_user_permission_for_sensitive_data"]
    ):
        reasons.append("requiere permiso para datos sensibles")

    return {
        "eligible": not reasons,
        "blocked_reasons": reasons,
    }


def score(action, policy):
    weights = policy["weights"]
    return (
        weights["operational_cost"] * action["operational_cost"]
        + weights["remaining_uncertainty"] * action["remaining_uncertainty"]
        + weights["risk"] * action["risk"]
    )


def rank_actions(case, policy):
    state = case["state"]
    rows = []
    for action in case["actions"]:
        gate = eligibility(action, state, policy)
        row = {
            "id": action["id"],
            "label": action["label"],
            "description": action["description"],
            "expected_observation": action["expected_observation"],
            "operational_cost": action["operational_cost"],
            "remaining_uncertainty": action["remaining_uncertainty"],
            "risk": action["risk"],
            "estimated_tokens": action["estimated_tokens"],
            "estimated_latency_seconds": action["estimated_latency_seconds"],
            "destructive": action["destructive"],
            "sensitive_data": action["sensitive_data"],
            "eligible": gate["eligible"],
            "blocked_reasons": gate["blocked_reasons"],
            "score": round(score(action, policy), 4),
        }
        rows.append(row)

    eligible = sorted([row for row in rows if row["eligible"]], key=lambda row: (row["score"], row["id"]))
    blocked = sorted([row for row in rows if not row["eligible"]], key=lambda row: row["id"])
    return eligible, blocked, rows


def render_markdown(case, policy, eligible, blocked):
    first = eligible[0] if eligible else None
    weights = policy["weights"]
    lines = [
        "# Decisión: primera acción del agente",
        "",
        f"Caso: `{case['case_id']}`.",
        "",
        f"Objetivo: {case['goal']}",
        "",
        "## Estado inicial",
        "",
    ]
    for observation in case["state"]["known_observations"]:
        lines.append(f"- {observation}")

    lines.extend(
        [
            "",
            "## Contrato de ranking",
            "",
            f"- Coste operativo: peso {weights['operational_cost']}.",
            f"- Incertidumbre restante: peso {weights['remaining_uncertainty']}.",
            f"- Riesgo: peso {weights['risk']}.",
            "- Primero se aplican bloqueos duros; después se rankean solo acciones elegibles.",
            "",
            "## Acción recomendada",
            "",
        ]
    )

    if first:
        lines.append(f"**{first['label']}** (`{first['id']}`) con score {first['score']}.")
        lines.append("")
        lines.append(f"Por qué: {first['description']}")
        lines.append("")
        lines.append(f"Observación esperada: {first['expected_observation']}")
    else:
        lines.append("No hay acciones elegibles. El agente debería pedir ayuda o ampliar permisos.")

    lines.extend(
        [
            "",
            "## Ranking de acciones elegibles",
            "",
            "| Acción | G | H | R | Score | Tokens | Latencia | Observación esperada |",
            "|---|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in eligible:
        lines.append(
            f"| {row['label']} | {row['operational_cost']} | {row['remaining_uncertainty']} | "
            f"{row['risk']} | {row['score']} | {row['estimated_tokens']} | "
            f"{row['estimated_latency_seconds']}s | {row['expected_observation']} |"
        )

    lines.extend(
        [
            "",
            "## Acciones bloqueadas",
            "",
            "| Acción | Motivo |",
            "|---|---|",
        ]
    )
    for row in blocked:
        reasons = "; ".join(row["blocked_reasons"])
        lines.append(f"| {row['label']} | {reasons} |")

    lines.extend(["", "## Criterios de parada", ""])
    for condition in policy["stop_conditions"]:
        lines.append(f"- {condition}")

    lines.extend(
        [
            "",
            "## Lectura técnica",
            "",
            "- Esta política no intenta reemplazar al LLM: acota su comportamiento operativo.",
            "- Una acción destructiva no compite en el ranking si no cumple precondiciones.",
            "- El score bajo no convierte una acción sensible en segura; para eso están los bloqueos duros.",
            "- La traza permite revisar si el agente investigó con evidencia o si actuó por impulso.",
        ]
    )
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--fail-on-invalid", action="store_true")
    args = parser.parse_args()

    case = load_json(ROOT / "data" / "agent_case.json")
    policy = load_json(ROOT / "contracts" / "action_policy.json")
    eligible, blocked, rows = rank_actions(case, policy)
    first_action = eligible[0]["id"] if eligible else None

    report = {
        "case_id": case["case_id"],
        "first_action": first_action,
        "eligible": eligible,
        "blocked": blocked,
        "all_actions": rows,
        "policy": policy,
    }

    output_dir = ROOT / "output"
    if args.write:
        output_dir.mkdir(exist_ok=True)
        (output_dir / "agent_action_report.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (output_dir / "agent_action_decision.md").write_text(
            render_markdown(case, policy, eligible, blocked) + "\n",
            encoding="utf-8",
        )

    errors = []
    if not eligible:
        errors.append("no hay acciones elegibles")
    if first_action != policy["expected_first_action"]:
        errors.append(f"primera acción inesperada: {first_action}")

    blocked_ids = {row["id"] for row in blocked}
    for expected in policy["expected_blocked_actions"]:
        if expected not in blocked_ids:
            errors.append(f"acción esperada como bloqueada no bloqueada: {expected}")

    destructive_eligible = [row["id"] for row in eligible if row["destructive"]]
    if destructive_eligible:
        errors.append(f"acciones destructivas elegibles sin evidencia: {destructive_eligible}")

    print(f"acciones: {len(rows)}")
    print(f"elegibles: {len(eligible)}")
    print(f"bloqueadas: {len(blocked)}")
    print(f"primera_accion: {first_action}")
    print(f"errores_gate: {len(errors)}")
    print(f"salida: {output_dir if args.write else 'no escrita'}")

    if args.fail_on_invalid and errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(2)


if __name__ == "__main__":
    main()
