#!/usr/bin/env python3
import json
from pathlib import Path


CONTRACT = {
    "states": ["queued", "running", "needs_review", "completed", "failed", "cancelled"],
    "required_request_fields": ["run_id", "tenant_id", "input", "contract_version", "idempotency_key"],
    "required_response_fields": ["run_id", "status", "output", "error", "trace_id"],
    "retry_policy": {"strategy": "exponential_backoff", "max_attempts": 3},
    "dead_letter_queue": True,
}


def validate():
    checks = {
        "states_complete": {"queued", "running", "completed", "failed"}.issubset(CONTRACT["states"]),
        "idempotency_required": "idempotency_key" in CONTRACT["required_request_fields"],
        "trace_returned": "trace_id" in CONTRACT["required_response_fields"],
        "dlq_enabled": CONTRACT["dead_letter_queue"] is True,
    }
    return {"contract": CONTRACT, "checks": checks, "decision": "runtime_contract_valid" if all(checks.values()) else "review_contract"}


if __name__ == "__main__":
    report = validate()
    out = Path("output/runtime_contract_report.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
