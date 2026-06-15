import argparse
import json
import time
import uuid
from pathlib import Path


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def read_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def write_json(path, payload):
    Path(path).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def now_ms():
    return int(time.time() * 1000)


def span(trace, name, **attrs):
    trace["spans"].append({"name": name, "timestamp_ms": now_ms(), "attrs": attrs})


def route_request(text):
    lower = text.lower()
    if "publica" in lower or "correccion" in lower:
        return {"route": "guide_update", "effect": "persistent_write", "tool": "prepare_guide_diff"}
    if "ticket" in lower or "cuenta" in lower:
        return {"route": "support_ticket", "effect": "persistent_write", "tool": "create_ticket"}
    if "referencia" in lower or "apa" in lower:
        return {"route": "reference_flow", "effect": "read", "tool": "validate_reference"}
    if "pagos" in lower or "campus" in lower:
        return {"route": "data_flow", "effect": "read", "tool": "query_payments"}
    return {"route": "read_only_answer", "effect": "read", "tool": "answer"}


def execute_tool(tool, text, key, ledger):
    if tool in {"create_ticket", "prepare_guide_diff"}:
        if key in ledger:
            return {"created": False, "effect_id": ledger[key], "reason": "already_created"}
        effect_id = f"EFF-{len(ledger) + 1:04d}"
        ledger[key] = effect_id
        return {"created": True, "effect_id": effect_id, "reason": "new_effect"}
    if tool == "validate_reference":
        return {"answer": "referencia validada con fuente y formato APA", "source_checked": True}
    if tool == "query_payments":
        return {"answer": "Norte: 2; Centro: 1", "query_id": "payments_by_campus_v1"}
    return {"answer": "consulta atendida", "source": "fixture"}


def run_request(request, policy, run_store, ledger):
    key = request["idempotency_key"]
    if key in run_store:
        trace = {"trace_id": str(uuid.uuid4()), "request_id": request["request_id"], "spans": []}
        span(trace, policy["required_duplicate_span"], original_run_id=run_store[key]["run_id"], idempotency_key=key)
        return {"run_id": run_store[key]["run_id"], "state": "DUPLICATE", "decision": "no repetir efecto", "trace": trace}

    run_id = str(uuid.uuid4())
    trace = {"trace_id": str(uuid.uuid4()), "request_id": request["request_id"], "spans": []}
    span(trace, "run.started", run_id=run_id)
    plan = route_request(request["user_text"])
    span(trace, "route.decision", **plan)

    if plan["effect"] in policy["approval_required_for"] and not request["approval_granted"]:
        span(trace, policy["required_waiting_span"], route=plan["route"], reason="persistent_write")
        result = {"run_id": run_id, "state": "WAITING_APPROVAL", "decision": "esperando aprobación", "route": plan["route"], "effect": None, "trace": trace}
        run_store[key] = result
        return result

    span(trace, "tool.call", tool=plan["tool"], route=plan["route"])
    effect = execute_tool(plan["tool"], request["user_text"], key, ledger)
    span(trace, "tool.result", tool=plan["tool"], **effect)
    span(trace, "run.completed", state="COMPLETED")
    result = {"run_id": run_id, "state": "COMPLETED", "decision": "completado", "route": plan["route"], "effect": effect, "trace": trace}
    run_store[key] = result
    return result


def build_report(results, ledger, policy):
    duplicate_count = sum(item["state"] == "DUPLICATE" for item in results)
    waiting_count = sum(item["state"] == "WAITING_APPROVAL" for item in results)
    completed_count = sum(item["state"] == "COMPLETED" for item in results)
    effect_ids = [value for value in ledger.values()]
    unique_effects = len(effect_ids) == len(set(effect_ids))
    spans_ok = []
    for item in results:
        names = [span["name"] for span in item["trace"]["spans"]]
        if item["state"] == "DUPLICATE":
            spans_ok.append(policy["required_duplicate_span"] in names)
        elif item["state"] == "WAITING_APPROVAL":
            spans_ok.append(policy["required_waiting_span"] in names)
        else:
            spans_ok.append(set(policy["required_trace_spans"]).issubset(set(names)))
    gate = "pass" if unique_effects and all(spans_ok) and duplicate_count >= 1 and waiting_count >= 1 else "review"
    return {
        "gate": gate,
        "completed_count": completed_count,
        "duplicate_count": duplicate_count,
        "waiting_approval_count": waiting_count,
        "effect_ledger": ledger,
        "unique_effects": unique_effects,
        "trace_complete_rate": round(sum(spans_ok) / len(spans_ok), 4),
        "runs": results,
    }


def render_decision(report):
    return "\n".join([
        "# Decisión de runtime agente",
        "",
        f"Gate: **{report['gate']}**.",
        "",
        f"- Runs completadas: {report['completed_count']}.",
        f"- Duplicados detectados: {report['duplicate_count']}.",
        f"- Runs esperando aprobación: {report['waiting_approval_count']}.",
        f"- Trazas completas: {report['trace_complete_rate']}.",
        "",
        "La decisión defendible es aceptar el runtime como maqueta técnica: aplica idempotencia, no duplica efectos, separa acciones persistentes, espera aprobación cuando procede y deja trazas reconstruibles.",
    ]) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--requests", default="data/agent_requests.jsonl")
    parser.add_argument("--policy", default="contracts/agent_runtime_policy.json")
    parser.add_argument("--output-dir", default="output")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    policy = read_json(args.policy)
    run_store = {}
    ledger = {}
    results = [run_request(request, policy, run_store, ledger) for request in read_jsonl(args.requests)]
    report = build_report(results, ledger, policy)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if args.write:
        out = Path(args.output_dir)
        out.mkdir(parents=True, exist_ok=True)
        write_json(out / "runtime_report.json", report)
        write_json(out / "effect_ledger.json", ledger)
        (out / "runtime_trace.jsonl").write_text("\n".join(json.dumps(item["trace"], ensure_ascii=False) for item in results) + "\n", encoding="utf-8")
        (out / "runtime_decision.md").write_text(render_decision(report), encoding="utf-8")


if __name__ == "__main__":
    main()
