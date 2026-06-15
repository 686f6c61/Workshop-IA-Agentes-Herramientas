#!/usr/bin/env python3
import json
from pathlib import Path


def read_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def status(event):
    if event["metric"] in {"latency_p95_ms", "review_queue_age_p95_minutes"}:
        return "breach" if event["value"] > event["slo"] else "pass"
    return "breach" if event["value"] < event["slo"] else "pass"


if __name__ == "__main__":
    rows = read_jsonl("data/incident_events.jsonl")
    metrics = [row for row in rows if row["type"] == "metric"]
    traces = [row for row in rows if row["type"] == "trace"]
    findings = [{**row, "status": status(row)} for row in metrics]
    report = {
        "severity": "SEV-2",
        "status": "degraded_controlled",
        "findings": findings,
        "trace_attrs_ok": all(all(key in trace for key in ["trace_id", "run_id", "model_id", "prompt_version", "route_id", "index_version", "release_id"]) for trace in traces),
        "mitigations": ["rollback_to_baseline", "restore_stable_index", "add_regression_case"],
    }
    out = Path("output/incident_report.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
