import argparse
import json
import sys
from pathlib import Path


REQUIRED = [
    "runtime_report.json",
    "runtime_trace.jsonl",
    "effect_ledger.json",
    "runtime_decision.md",
    "agent_eval_report.json",
    "ci_agent_gate.json",
    "agent_eval_decision.md",
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
        runtime = read_json(base / "runtime_report.json")
        eval_report = read_json(base / "agent_eval_report.json")
        ci = read_json(base / "ci_agent_gate.json")
        runtime_md = (base / "runtime_decision.md").read_text(encoding="utf-8").lower()
        eval_md = (base / "agent_eval_decision.md").read_text(encoding="utf-8").lower()
        trace_lines = [line for line in (base / "runtime_trace.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]

        add(result, 8, 8, runtime.get("gate") == "pass", "runtime pasa gate")
        add(result, 8, 8, runtime.get("duplicate_count", 0) >= 1 and runtime.get("waiting_approval_count", 0) >= 1, "runtime detecta duplicado y espera aprobación")
        add(result, 6, 6, runtime.get("unique_effects") is True, "ledger no duplica efectos")
        add(result, 6, 6, runtime.get("trace_complete_rate", 0) >= 1 and len(trace_lines) >= 5, "trazas completas")
        metrics = eval_report.get("metrics", {})
        add(result, 6, 6, eval_report.get("status") in {"publicar", "publicar_con_condiciones"}, "evaluación de agente sin bloqueos")
        add(result, 8, 8, metrics.get("route_accuracy", 0) >= 0.9 and metrics.get("task_pass_rate", 0) >= 0.85, "route accuracy y task pass rate suficientes")
        add(result, 6, 6, metrics.get("tool_violation_count", 1) == 0 and metrics.get("approval_violation_count", 1) == 0, "sin violaciones de tools ni aprobación")
        add(result, 4, 4, ci.get("status") == eval_report.get("status"), "gate CI coherente")
        add(result, 4, 4, all(term in runtime_md for term in ["idempotencia", "aprobación", "trazas"]) and all(term in eval_md for term in ["ruta", "tools", "latencia"]), "decisiones explican runtime y evaluación")

        gate_ok = result["score"] >= 60

    result["gate_ok"] = gate_ok
    print(json.dumps({"score": result["score"], "max_score": result["max_score"], "gate_ok": gate_ok}, indent=2, ensure_ascii=False))

    if args.write:
        lines = [
            "# Correccion de entrega F5",
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
