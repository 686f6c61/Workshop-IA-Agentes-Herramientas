#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = ROOT / "data" / "support_graph.json"
DEFAULT_CONTRACT = ROOT / "contracts" / "ia_clasica_lab_contract.json"
DEFAULT_OUTPUT_DIR = ROOT / "output"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def objects(triples, subject, predicate):
    return sorted(obj for subj, pred, obj in triples if subj == subject and pred == predicate)


def has(triples, subject, predicate, obj):
    return [subject, predicate, obj] in triples


def evaluate(data):
    triples = data["triples"]
    ticket = data["ticket_id"]
    trace = []

    user = objects(triples, ticket, "paraPersona")[0]
    resource = objects(triples, ticket, "solicitaAccesoA")[0]
    approver = objects(triples, ticket, "tieneAprobacion")[0]
    trace.append({"step": "resolver_entidades", "ticket": ticket, "user": user, "resource": resource, "approver": approver})

    required_role = objects(triples, resource, "requiereRol")[0]
    user_team = objects(triples, user, "perteneceA")[0]
    trace.append({"step": "consultar_grafo", "required_role": required_role, "user_team": user_team})

    checks = {
        "rol_requerido": has(triples, user, "tieneRol", required_role),
        "aprobacion_del_equipo": has(triples, approver, "responsableDe", user_team),
        "acceso_temporal_permitido": has(triples, resource, "permiteAcceso", "temporal")
    }
    for name, ok in checks.items():
        trace.append({"step": "validar_precondicion", "check": name, "ok": ok})

    action = "conceder_acceso_temporal" if all(checks.values()) else "pedir_revision_humana"
    trace.append({"step": "decidir_accion", "action": action})
    trace.append({"step": "registrar_traza", "ticket": ticket, "action": action})

    plan = [
        f"resolver_entidades({ticket})",
        f"consultar_grafo({user}, {resource})",
        f"validar_rol({required_role})",
        f"validar_aprobacion({approver})",
        f"{action}({user}, {resource})",
        f"registrar_traza({ticket})"
    ]
    return {
        "status": "precondiciones_cumplidas" if all(checks.values()) else "revision_necesaria",
        "action": action,
        "checks": checks,
        "plan": plan,
        "trace": trace
    }


def render_decision(report):
    def si_no(value):
        return "sí" if value else "no"

    lines = [
        "# Decisión simbólica",
        "",
        f"Decisión: `{report['action']}`.",
        "",
        "| Comprobación | Resultado |",
        "|---|---|",
    ]
    for name, ok in report["checks"].items():
        lines.append(f"| `{name}` | {si_no(ok)} |")
    lines.extend([
        "",
        "## Plan trazable",
        "",
    ])
    for step in report["plan"]:
        lines.append(f"- `{step}`")
    lines.extend([
        "",
        "## Lectura técnica",
        "",
        "El modelo podría ayudar a leer el ticket, pero la acción se decide con hechos y precondiciones. Esa separación permite explicar y depurar el resultado.",
        "",
    ])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--fail-on-review", action="store_true")
    args = parser.parse_args()

    data = read_json(args.data)
    contract = read_json(args.contract)
    report = evaluate(data)
    expected = contract["symbolic_gate"]["expected_action"]
    report["gate_ok"] = report["action"] == expected and len(report["trace"]) >= contract["symbolic_gate"]["min_trace_steps"]

    if args.write:
        write_json(args.output_dir / "symbolic_plan_report.json", {k: v for k, v in report.items() if k != "trace"})
        (args.output_dir / "symbolic_plan_trace.jsonl").write_text(
            "\n".join(json.dumps(row, ensure_ascii=False) for row in report["trace"]) + "\n",
            encoding="utf-8"
        )
        (args.output_dir / "symbolic_plan_decision.md").write_text(render_decision(report), encoding="utf-8")
    print(json.dumps({"action": report["action"], "gate_ok": report["gate_ok"]}, ensure_ascii=False, indent=2))
    if args.fail_on_review and not report["gate_ok"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
