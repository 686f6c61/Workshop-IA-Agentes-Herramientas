#!/usr/bin/env python3
import json
from pathlib import Path


REQUIRED = ["run_id", "trace_id", "release_id", "model_id", "prompt_version", "route_id", "index_version"]


def main():
    text = Path("ops/ai/observability.yaml").read_text(encoding="utf-8")
    checks = {
        "has_sli_block": "slis:" in text,
        "has_slo_block": "slo:" in text,
        "all_trace_attributes": all(item in text for item in REQUIRED),
        "redacts_raw_prompt": "raw_prompt" in text,
    }
    report = {"checks": checks, "decision": "observability_contract_valid" if all(checks.values()) else "complete_observability_contract"}
    out = Path("output/observability_contract_report.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
