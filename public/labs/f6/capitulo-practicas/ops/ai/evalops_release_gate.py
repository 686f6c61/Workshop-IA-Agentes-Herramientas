#!/usr/bin/env python3
import json
from pathlib import Path


SCORECARD = {
    "contract": 1.0,
    "evals": 0.96,
    "latency": 0.94,
    "cost": 0.98,
    "rollback": 1.0,
    "observability": 0.95,
}


def main():
    min_score = 0.93
    failed = [name for name, value in SCORECARD.items() if value < min_score]
    report = {
        "scorecard": SCORECARD,
        "min_score": min_score,
        "failed": failed,
        "decision": "promote_to_canary" if not failed else "block_release",
    }
    out = Path("output/evalops_release_gate.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
