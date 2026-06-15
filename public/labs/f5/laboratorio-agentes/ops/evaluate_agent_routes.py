import argparse
import json
import statistics
import sys
from pathlib import Path


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, payload):
    Path(path).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def percentile(values, q):
    ordered = sorted(values)
    index = min(len(ordered) - 1, round((len(ordered) - 1) * q))
    return ordered[index]


def evaluate(cases, runs, contract):
    runs_by_case = {run["case_id"]: run for run in runs}
    case_results = []
    for case in cases:
        run = runs_by_case.get(case["case_id"], {})
        tools = set(run.get("tools", []))
        required = set(case["required_tools"])
        forbidden = set(case["forbidden_tools"])
        route_ok = run.get("route") == case["expected_route"]
        required_ok = required.issubset(tools)
        forbidden_ok = not bool(forbidden & tools)
        approval_ok = (not case["requires_approval"]) or run.get("approval_requested") is True
        cost_ok = run.get("cost", 999) <= case["max_cost"]
        latency_ok = run.get("latency_ms", 999999) <= case["max_latency_ms"]
        trace_ok = set(["route", "tool", "final"]).issubset(set(run.get("trace_spans", [])))
        pass_case = all([route_ok, required_ok, forbidden_ok, approval_ok, cost_ok, latency_ok, trace_ok])
        case_results.append({
            "case_id": case["case_id"],
            "route_ok": route_ok,
            "required_tools_ok": required_ok,
            "forbidden_tools_ok": forbidden_ok,
            "approval_ok": approval_ok,
            "cost_ok": cost_ok,
            "latency_ok": latency_ok,
            "trace_ok": trace_ok,
            "pass": pass_case,
        })

    costs = [run["cost"] for run in runs]
    latencies = [run["latency_ms"] for run in runs]
    metrics = {
        "route_accuracy": round(sum(item["route_ok"] for item in case_results) / len(case_results), 4),
        "task_pass_rate": round(sum(item["pass"] for item in case_results) / len(case_results), 4),
        "trace_complete_rate": round(sum(item["trace_ok"] for item in case_results) / len(case_results), 4),
        "tool_violation_count": sum(not item["forbidden_tools_ok"] for item in case_results),
        "approval_violation_count": sum(not item["approval_ok"] for item in case_results),
        "mean_cost": round(statistics.mean(costs), 4),
        "latency_p95_ms": percentile(latencies, 0.95),
        "tool_call_mean": round(statistics.mean(len(run["tools"]) for run in runs), 4),
        "human_review_rate": round(sum(run.get("approval_requested") for run in runs) / len(runs), 4),
    }

    must = contract["must_pass"]
    review = contract["review_triggers"]
    blocks = []
    if metrics["route_accuracy"] < must["route_accuracy_min"]:
        blocks.append("route_accuracy")
    if metrics["task_pass_rate"] < must["task_pass_rate_min"]:
        blocks.append("task_pass_rate")
    if metrics["trace_complete_rate"] < must["trace_complete_rate_min"]:
        blocks.append("trace_complete_rate")
    if metrics["tool_violation_count"] > must["tool_violation_count_max"]:
        blocks.append("tool_violation_count")
    if metrics["approval_violation_count"] > must["approval_violation_count_max"]:
        blocks.append("approval_violation_count")
    if metrics["mean_cost"] > must["mean_cost_max"]:
        blocks.append("mean_cost")
    if metrics["latency_p95_ms"] > must["latency_p95_ms_max"]:
        blocks.append("latency_p95_ms")

    reviews = []
    if metrics["tool_call_mean"] > review["tool_call_mean_over"]:
        reviews.append("tool_call_mean")
    if metrics["human_review_rate"] > review["human_review_rate_over"]:
        reviews.append("human_review_rate")

    status = "bloquear" if blocks else "publicar_con_condiciones" if reviews else "publicar"
    return {"status": status, "metrics": metrics, "blocks": blocks, "reviews": reviews, "cases": case_results}


def render_decision(report):
    lines = [
        "# Decisión de evaluación de agente",
        "",
        f"Estado: **{report['status']}**.",
        "",
        "## Metricas",
        "",
    ]
    for key, value in report["metrics"].items():
        lines.append(f"- `{key}`: `{value}`.")
    lines.extend([
        "",
        "## Lectura",
        "",
    ])
    if report["status"] == "bloquear":
        lines.append("No avanzaría la versión: hay fallos de ruta, tools, aprobación, coste, latencia o trazas que afectan al contrato.")
    elif report["status"] == "publicar_con_condiciones":
        lines.append("Avanzaría solo con condiciones, porque no hay bloqueos pero sí señales de coste o revisión que conviene vigilar.")
    else:
        lines.append("Avanzaría la versión en canary normal: las trayectorias pasan ruta, tools, aprobación, coste, latencia y trazas.")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", default="data/agent_eval_cases.json")
    parser.add_argument("--runs", default="data/agent_runs_reference.json")
    parser.add_argument("--contract", default="contracts/agent_eval_contract.json")
    parser.add_argument("--output-dir", default="output")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--fail-on-blocker", action="store_true")
    args = parser.parse_args()

    report = evaluate(read_json(args.cases), read_json(args.runs), read_json(args.contract))
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if args.write:
        out = Path(args.output_dir)
        out.mkdir(parents=True, exist_ok=True)
        write_json(out / "agent_eval_report.json", report)
        write_json(out / "ci_agent_gate.json", {"status": report["status"], "blocks": report["blocks"], "reviews": report["reviews"]})
        (out / "agent_eval_decision.md").write_text(render_decision(report), encoding="utf-8")
    if args.fail_on_blocker and report["status"] == "bloquear":
        sys.exit(2)


if __name__ == "__main__":
    main()
