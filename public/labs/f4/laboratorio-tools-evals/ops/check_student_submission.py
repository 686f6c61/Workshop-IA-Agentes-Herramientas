import argparse
import json
import sys
from pathlib import Path


REQUIRED = [
    "rag_eval_report.json",
    "ci_rag_gate.json",
    "rag_traces.jsonl",
    "rag_decision.md",
    "router_eval_report.json",
    "ci_router_gate.json",
    "router_traces.jsonl",
    "router_decision.md"
]


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def add(result, points, max_points, ok, message):
    result["score"] += points if ok else 0
    result["max_score"] += max_points
    result["checks"].append({"ok": ok, "points": points if ok else 0, "max_points": max_points, "message": message})


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
        add(result, 1, 1, (base / name).exists(), f"archivo requerido: {name}")

    if missing:
        gate_ok = False
    else:
        rag = read_json(base / "rag_eval_report.json")
        router = read_json(base / "router_eval_report.json")
        rag_gate = read_json(base / "ci_rag_gate.json")
        router_gate = read_json(base / "ci_router_gate.json")
        rag_trace_lines = [line for line in (base / "rag_traces.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
        router_trace_lines = [line for line in (base / "router_traces.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
        rag_decision = (base / "rag_decision.md").read_text(encoding="utf-8").lower()
        router_decision = (base / "router_decision.md").read_text(encoding="utf-8").lower()

        add(result, 10, 10, rag.get("status") == "publicar", "RAG sin bloqueos")
        add(result, 8, 8, rag.get("metrics", {}).get("hit_at_1", 0) >= 0.9 and rag.get("metrics", {}).get("abstention_ok", 0) >= 0.9, "RAG recupera y se abstiene")
        add(result, 6, 6, rag_gate.get("status") == rag.get("status"), "gate RAG coherente")
        add(result, 6, 6, len(rag_trace_lines) >= 4, "trazas RAG")
        add(result, 10, 10, router.get("status") == "publicar", "router sin bloqueos")
        add(result, 8, 8, router.get("metrics", {}).get("route_accuracy", 0) >= 0.95 and router.get("metrics", {}).get("task_pass_rate", 0) >= 0.9, "router enruta y resuelve")
        add(result, 6, 6, router_gate.get("status") == router.get("status"), "gate router coherente")
        add(result, 6, 6, len(router_trace_lines) >= 4, "trazas router")
        router_terms_ok = all(term in router_decision for term in ["rag", "sql", "clasificador"]) and ("codigo" in router_decision or "código" in router_decision)
        add(result, 2, 2, "evidencia" in rag_decision and router_terms_ok, "decisiones explican evidencia y rutas")

        gate_ok = result["score"] >= 60

    result["gate_ok"] = gate_ok
    print(json.dumps({"score": result["score"], "max_score": result["max_score"], "gate_ok": gate_ok}, indent=2, ensure_ascii=False))

    if args.write:
        lines = ["# Corrección de entrega F4", "", f"Score: {result['score']} / {result['max_score']}.", f"Gate: {'ok' if gate_ok else 'revisar'}.", "", "| Check | Puntos |", "|---|---:|"]
        for check in result["checks"]:
            lines.append(f"| {check['message']} | {check['points']} / {check['max_points']} |")
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text("\n".join(lines) + "\n", encoding="utf-8")

    if args.fail_on_missing and (missing or not gate_ok):
        sys.exit(2)


if __name__ == "__main__":
    main()
