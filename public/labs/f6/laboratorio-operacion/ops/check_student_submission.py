import argparse
import json
import sys
from pathlib import Path


REQUIRED = [
    "operational_readiness.json",
    "readiness_decision.md",
    "continuity_report.json",
    "ci_continuity_gate.json",
    "continuity_decision.md",
    "postmortem.md",
    "regression_case.json",
]


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def add(result, points, max_points, ok, message):
    result["score"] += points if ok else 0
    result["max_score"] += max_points
    result["checks"].append({
        "ok": ok,
        "points": points if ok else 0,
        "max_points": max_points,
        "message": message,
    })


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--submission-dir", default="solutions/reference")
    parser.add_argument("--output", default="output/student_submission_report.md")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--fail-on-missing", action="store_true")
    args = parser.parse_args()

    base = Path(args.submission_dir)
    result = {"score": 0, "max_score": 0, "checks": []}
    missing = [name for name in REQUIRED if not (base / name).exists()]
    for name in REQUIRED:
        add(result, 2, 2, (base / name).exists(), f"archivo requerido: {name}")

    if missing:
        gate_ok = False
    else:
        readiness = read_json(base / "operational_readiness.json")
        continuity = read_json(base / "continuity_report.json")
        ci = read_json(base / "ci_continuity_gate.json")
        regression = read_json(base / "regression_case.json")
        readiness_md = (base / "readiness_decision.md").read_text(encoding="utf-8").lower()
        continuity_md = (base / "continuity_decision.md").read_text(encoding="utf-8").lower()
        postmortem = (base / "postmortem.md").read_text(encoding="utf-8").lower()

        add(result, 10, 10, readiness.get("gate") in {"ready", "ready_with_conditions", "not_ready"} and len(readiness.get("checks", [])) >= 8, "readiness con gate y ocho secciones")
        add(result, 7, 7, readiness.get("gate") == "ready", "manifiesto completo alcanza ready")
        add(result, 8, 8, all(key in readiness_md for key in ["slo", "rollback", "evalops", "handoff"]), "decisión de readiness explica SLO, rollback, EvalOps y handoff")
        add(result, 8, 8, continuity.get("status") in {"degraded_controlled", "recovered", "not_reconstructable"} and len(continuity.get("findings", [])) >= 3, "continuidad con métricas y estado")
        add(result, 6, 6, ci.get("status") == continuity.get("status"), "gate de continuidad coherente")
        add(result, 6, 6, "must_pass" in regression and "observed_findings" in regression, "caso de regresión generado")
        add(result, 4, 4, all(key in continuity_md for key in ["canary", "fallback", "índice"]), "decisión de continuidad propone canary, fallback e índice")
        add(result, 4, 4, all(key in postmortem for key in ["evidencia", "acciones"]), "postmortem conserva evidencia y acciones")
        add(result, 3, 3, readiness.get("score", 0) >= 0.95 and continuity.get("trace_attrs_ok") is True, "trazabilidad suficiente")

        gate_ok = result["score"] >= 60

    result["gate_ok"] = gate_ok
    print(json.dumps({"score": result["score"], "max_score": result["max_score"], "gate_ok": gate_ok}, indent=2, ensure_ascii=False))

    if args.write:
        lines = [
            "# Corrección de entrega F6",
            "",
            f"Score: {result['score']} / {result['max_score']}.",
            f"Gate: {'ok' if gate_ok else 'revisar'}.",
            "",
            "| Check | Puntos |",
            "|---|---:|",
        ]
        for check in result["checks"]:
            lines.append(f"| {check['message']} | {check['points']} / {check['max_points']} |")
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text("\n".join(lines) + "\n", encoding="utf-8")

    if args.fail_on_missing and (missing or not gate_ok):
        sys.exit(2)


if __name__ == "__main__":
    main()
