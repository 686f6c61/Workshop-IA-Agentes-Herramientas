#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def risk_score(call):
    risk = call.get("risk", {})
    try:
        return risk["impact"] * risk["probability"] * risk["irreversible"]
    except KeyError:
        return None


def schema_check(call, policy):
    reasons = []
    args = call.get("args", {})
    schema = policy["schema"]
    if call.get("tool") != policy["tool"]:
        reasons.append("tool inesperada")
    for key in schema["required_args"]:
        if key not in args:
            reasons.append(f"falta argumento {key}")
    amount = args.get("amount_eur")
    if not isinstance(args.get("order_id"), str):
        reasons.append("order_id debe ser texto")
    if not isinstance(args.get("reason"), str):
        reasons.append("reason debe ser texto")
    if not isinstance(amount, (int, float)):
        reasons.append("amount_eur debe ser numérico")
    elif not (schema["amount_min"] <= amount <= schema["amount_max"]):
        reasons.append("amount_eur fuera de rango")
    return not reasons, reasons


def permission_check(call, policy):
    role = call.get("user", {}).get("role")
    amount = call.get("args", {}).get("amount_eur")
    limit = policy["role_auto_limits"].get(role)
    if limit is None:
        return False, [f"rol sin permisos automáticos: {role}"]
    if not isinstance(amount, (int, float)):
        return False, ["importe no evaluable"]
    if amount <= limit:
        return True, []
    return False, [f"importe {amount} supera límite automático de rol {role}: {limit}"]


def business_policy_check(call, policy):
    status = call.get("state", {}).get("status")
    allowed = policy["business_policy"]["allowed_order_statuses"]
    if status in allowed:
        return True, []
    return False, [f"estado no permitido: {status}"]


def risk_check(call, policy):
    score = risk_score(call)
    if score is None:
        return False, ["riesgo no calculable"], score
    threshold = policy["hitl"]["risk_threshold"]
    if score <= threshold:
        return True, [], score
    return False, [f"riesgo {score} supera umbral {threshold}"], score


def invariant_check(call):
    state = call.get("state", {})
    amount = call.get("args", {}).get("amount_eur")
    reasons = []
    if state.get("already_refunded"):
        reasons.append("pedido ya reembolsado")
    if isinstance(amount, (int, float)) and amount > state.get("paid_amount_eur", 0):
        reasons.append("importe supera lo pagado")
    if not isinstance(amount, (int, float)):
        reasons.append("importe no evaluable para invariante")
    return not reasons, reasons


def can_escalate(call, policy, failed_controls):
    role = call.get("user", {}).get("role")
    amount = call.get("args", {}).get("amount_eur")
    review_roles = policy["hitl"]["allowed_roles_for_review"]
    if role not in review_roles:
        return False
    if not isinstance(amount, (int, float)):
        return False
    if "permission" in failed_controls or "risk" in failed_controls:
        return amount >= policy["hitl"]["amount_threshold"] or "risk" in failed_controls
    return False


def evaluate(call, policy):
    schema_ok, schema_reasons = schema_check(call, policy)
    permission_ok, permission_reasons = permission_check(call, policy) if schema_ok else (False, ["schema inválido"])
    business_ok, business_reasons = business_policy_check(call, policy) if schema_ok else (False, ["schema inválido"])
    risk_ok, risk_reasons, risk = risk_check(call, policy) if schema_ok else (False, ["schema inválido"], None)
    invariant_ok, invariant_reasons = invariant_check(call) if schema_ok else (False, ["schema inválido"])

    checks = {
        "schema": {"ok": schema_ok, "reasons": schema_reasons},
        "permission": {"ok": permission_ok, "reasons": permission_reasons},
        "business_policy": {"ok": business_ok, "reasons": business_reasons},
        "risk": {"ok": risk_ok, "reasons": risk_reasons},
        "invariant": {"ok": invariant_ok, "reasons": invariant_reasons},
    }
    failed_controls = [name for name, data in checks.items() if not data["ok"]]

    hard_deny_controls = {"schema", "business_policy", "invariant"}
    if not failed_controls:
        decision = "ALLOW"
    elif hard_deny_controls.intersection(failed_controls):
        decision = "DENY"
    elif can_escalate(call, policy, failed_controls):
        decision = "HITL"
    else:
        decision = "DENY"

    reasons = []
    for name in failed_controls:
        reasons.extend(f"{name}: {reason}" for reason in checks[name]["reasons"])

    return {
        "call_id": call["id"],
        "decision": decision,
        "risk_score": risk,
        "checks": checks,
        "reasons": reasons,
        "tool": call.get("tool"),
        "user_role": call.get("user", {}).get("role"),
        "amount_eur": call.get("args", {}).get("amount_eur"),
    }


def render_markdown(results):
    lines = [
        "# Decisión: guardrail gate",
        "",
        "| Pedido | Decisión | Importe | Rol | Riesgo | Motivos |",
        "|---|---|---:|---|---:|---|",
    ]
    for row in results:
        reasons = "; ".join(row["reasons"]) if row["reasons"] else "todos los controles pasan"
        risk = "" if row["risk_score"] is None else row["risk_score"]
        lines.append(
            f"| {row['call_id']} | {row['decision']} | {row['amount_eur']} | {row['user_role']} | {risk} | {reasons} |"
        )

    lines.extend(
        [
            "",
            "## Lectura técnica",
            "",
            "- `ALLOW` significa que schema, permisos, política, riesgo e invariante pasan.",
            "- `HITL` significa que la acción puede ser legítima, pero no debe ejecutarse automáticamente.",
            "- `DENY` se usa para schema inválido, estado incompatible o invariante roto.",
            "- El sistema falla cerrado: si no puede evaluar un control crítico, no ejecuta la tool.",
        ]
    )
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--fail-on-invalid", action="store_true")
    args = parser.parse_args()

    policy = load_json(ROOT / "contracts" / "guardrail_policy.json")
    data = load_json(ROOT / "data" / "refund_calls.json")
    results = [evaluate(call, policy) for call in data["calls"]]

    output_dir = ROOT / "output"
    if args.write:
        output_dir.mkdir(exist_ok=True)
        (output_dir / "guardrail_report.json").write_text(
            json.dumps(results, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (output_dir / "guardrail_audit_log.jsonl").write_text(
            "\n".join(json.dumps(row, ensure_ascii=False) for row in results) + "\n",
            encoding="utf-8",
        )
        (output_dir / "guardrail_decision.md").write_text(
            render_markdown(results) + "\n",
            encoding="utf-8",
        )

    by_id = {row["call_id"]: row["decision"] for row in results}
    errors = []
    for call_id, expected in policy["expected_decisions"].items():
        if by_id.get(call_id) != expected:
            errors.append(f"{call_id}: esperado {expected}, obtenido {by_id.get(call_id)}")

    counts = {}
    for row in results:
        counts[row["decision"]] = counts.get(row["decision"], 0) + 1
    for required in ["ALLOW", "DENY", "HITL"]:
        if counts.get(required, 0) == 0:
            errors.append(f"falta decisión {required}")

    print(f"calls: {len(results)}")
    print(f"allow: {counts.get('ALLOW', 0)}")
    print(f"deny: {counts.get('DENY', 0)}")
    print(f"hitl: {counts.get('HITL', 0)}")
    print(f"errores_gate: {len(errors)}")
    print(f"salida: {output_dir if args.write else 'no escrita'}")

    if args.fail_on_invalid and errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(2)


if __name__ == "__main__":
    main()
