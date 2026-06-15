#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GATE = ROOT / "output" / "release_gate.json"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate", type=Path, default=DEFAULT_GATE)
    parser.add_argument("--allow-review", action="store_true")
    args = parser.parse_args()

    payload = json.loads(args.gate.read_text(encoding="utf-8"))
    gate = payload["gate"]

    if gate == "pass":
        print("data quality gate: pass")
        return

    if gate == "review" and args.allow_review:
        print("data quality gate: review allowed")
        return

    print(f"data quality gate: {gate}")
    print("blocking_failures:", ", ".join(payload.get("blocking_failures", [])) or "none")
    print("review_failures:", ", ".join(payload.get("review_failures", [])) or "none")
    raise SystemExit(1)


if __name__ == "__main__":
    main()
