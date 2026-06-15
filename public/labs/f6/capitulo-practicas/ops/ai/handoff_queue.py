#!/usr/bin/env python3
import json
from pathlib import Path


def read_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def reasons(row):
    out = []
    if row["confidence"] < 0.78:
        out.append("low_confidence")
    if row["cost_eur"] > 0.03:
        out.append("cost_over_budget")
    if row["effect"] in {"external_message", "db_update", "publish"}:
        out.append("effect_requires_review")
    if row["missing_evidence"]:
        out.append("missing_evidence")
    if row["schema_valid"] is not True:
        out.append("contract_failed")
    return out


if __name__ == "__main__":
    rows = read_jsonl("data/handoff_examples.jsonl")
    queue = [{"request_id": row["request_id"], "trace_id": row["trace_id"], "reasons": reasons(row)} for row in rows if reasons(row)]
    report = {
        "queue_size": len(queue),
        "auto_continue": [row["request_id"] for row in rows if not reasons(row)],
        "next_card": queue[0],
        "decision": "needs_review",
    }
    out = Path("output/handoff_queue_result.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
