#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path


STEPS = [
    {"stage": "shadow", "traffic": 0, "contract_fail_rate": 0.0, "cost_p95_eur": 0.024},
    {"stage": "canary-1", "traffic": 1, "contract_fail_rate": 0.004, "cost_p95_eur": 0.025},
    {"stage": "canary-5", "traffic": 5, "contract_fail_rate": 0.005, "cost_p95_eur": 0.027},
    {"stage": "canary-25", "traffic": 25, "contract_fail_rate": 0.009, "cost_p95_eur": 0.036},
]


def bucket(flag, key):
    digest = hashlib.sha256(f"{flag}:{key}".encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % 100


def evaluate(step):
    checks = {
        "contract_ok": step["contract_fail_rate"] <= 0.006,
        "cost_ok": step["cost_p95_eur"] <= 0.033,
    }
    decision = "advance" if all(checks.values()) else "rollback_to_baseline"
    return {**step, "checks": checks, "decision": decision}


if __name__ == "__main__":
    decisions = [evaluate(step) for step in STEPS]
    first_block = next((item for item in decisions if item["decision"] != "advance"), decisions[-1])
    report = {
        "release": "support-rag@1.9.0-rc1",
        "assignment_sample": {"tenant_042": "candidate" if bucket("support_rag_v19", "tenant_042") < 5 else "baseline"},
        "decisions": decisions,
        "final_decision": first_block["decision"],
    }
    out = Path("output/progressive_rollout.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
