import argparse
import json
import re
import sqlite3
import time
import uuid
from pathlib import Path


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, payload):
    Path(path).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def span(trace, name, **attrs):
    trace["spans"].append({"name": name, "timestamp_ms": int(time.time() * 1000), "attrs": attrs})


def route(text):
    lower = text.lower()
    if "suma" in lower or re.search(r"\d+\s+y\s+\d+", lower):
        return "code", "cálculo exacto"
    if "cuantos" in lower or "cuántos" in lower or "pagos pendientes" in lower:
        return "sql", "dato tabular"
    if "clasifica" in lower:
        return "classifier", "etiqueta estructurada"
    return "rag", "pregunta documental"


def tool_rag(text):
    lower = text.lower()
    if "matricula" in lower or "matrícula" in lower:
        return "La matrícula ordinaria se puede modificar hasta el 15 de septiembre."
    return "No tengo evidencia suficiente."


def tool_sql(_text):
    con = sqlite3.connect(":memory:")
    con.execute("CREATE TABLE pagos (campus TEXT, estado TEXT)")
    con.executemany("INSERT INTO pagos VALUES (?, ?)", [("Norte", "pendiente"), ("Norte", "pendiente"), ("Sur", "pagado"), ("Centro", "pendiente")])
    rows = con.execute("SELECT campus, COUNT(*) FROM pagos WHERE estado='pendiente' GROUP BY campus ORDER BY COUNT(*) DESC, campus ASC").fetchall()
    return "; ".join(f"{campus}: {count}" for campus, count in rows)


def tool_classifier(text):
    return "acceso" if "cuenta" in text.lower() or "entrar" in text.lower() else "general"


def tool_code(text):
    nums = [int(value) for value in re.findall(r"\d+", text)]
    return str(sum(nums))


def execute(case):
    trace = {"trace_id": str(uuid.uuid4()), "case_id": case["case_id"], "spans": []}
    span(trace, "input", text=case["input"])
    selected, reason = route(case["input"])
    span(trace, "route", route=selected, reason=reason)
    tools = {"rag": tool_rag, "sql": tool_sql, "classifier": tool_classifier, "code": tool_code}
    output = tools[selected](case["input"])
    span(trace, "tool", tool=selected, output=output)
    route_ok = selected == case["expected_route"]
    task_ok = case["expected_contains"].lower() in output.lower()
    span(trace, "evaluate", route_ok=route_ok, task_ok=task_ok)
    return {"case_id": case["case_id"], "route": selected, "output": output, "route_ok": route_ok, "task_ok": task_ok, "trace": trace}


def evaluate(results, contract):
    route_accuracy = sum(item["route_ok"] for item in results) / len(results)
    task_pass_rate = sum(item["task_ok"] for item in results) / len(results)
    trace_complete_rate = sum(len(item["trace"]["spans"]) >= 4 for item in results) / len(results)
    tool_error_count = sum(not item["task_ok"] for item in results)
    metrics = {"route_accuracy": round(route_accuracy, 4), "task_pass_rate": round(task_pass_rate, 4), "trace_complete_rate": round(trace_complete_rate, 4), "tool_error_count": tool_error_count}
    must = contract["router_must_pass"]
    blocks = []
    if metrics["route_accuracy"] < must["route_accuracy_min"]:
        blocks.append("route_accuracy")
    if metrics["task_pass_rate"] < must["task_pass_rate_min"]:
        blocks.append("task_pass_rate")
    if metrics["trace_complete_rate"] < must["trace_complete_rate_min"]:
        blocks.append("trace_complete_rate")
    if metrics["tool_error_count"] > must["tool_error_count_max"]:
        blocks.append("tool_error_count")
    return {"status": "bloquear" if blocks else "publicar", "metrics": metrics, "blocks": blocks, "results": results}


def render_decision(report):
    lines = ["# Decisión router tools", "", f"Estado: **{report['status']}**.", ""]
    for key, value in report["metrics"].items():
        lines.append(f"- `{key}`: `{value}`.")
    lines.extend(["", "La decisión comprueba que cada pregunta use la ruta adecuada: RAG para documentos, SQL para datos, clasificador para etiquetas y código para cálculo exacto."])
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", default="data/router_cases.json")
    parser.add_argument("--contract", default="contracts/lab_eval_contract.json")
    parser.add_argument("--output-dir", default="output")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    results = [execute(case) for case in read_json(args.cases)]
    report = evaluate(results, read_json(args.contract))
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if args.write:
        out = Path(args.output_dir)
        out.mkdir(parents=True, exist_ok=True)
        write_json(out / "router_eval_report.json", report)
        write_json(out / "ci_router_gate.json", {"status": report["status"], "blocks": report["blocks"]})
        (out / "router_traces.jsonl").write_text("\n".join(json.dumps(item["trace"], ensure_ascii=False) for item in results) + "\n", encoding="utf-8")
        (out / "router_decision.md").write_text(render_decision(report), encoding="utf-8")


if __name__ == "__main__":
    main()
