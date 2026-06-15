#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def build_gate(readiness_path, continuity_path):
    readiness = read_json(readiness_path)
    continuity = read_json(continuity_path)

    checks = {
        "readiness_ready": readiness.get("gate") == "ready",
        "readiness_score_ok": readiness.get("score", 0) >= 0.95,
        "continuity_recovered": continuity.get("status") == "recovered",
        "trace_attrs_ok": continuity.get("trace_attrs_ok") is True,
        "no_breaches": continuity.get("breach_count", 1) == 0
    }
    failed = [name for name, ok in checks.items() if not ok]

    if failed:
        decision = "do_not_release"
    else:
        decision = "release_candidate_operable"

    return {
        "gate_id": "f6_release_gate",
        "readiness_path": str(readiness_path),
        "continuity_path": str(continuity_path),
        "checks": checks,
        "failed_checks": failed,
        "decision": decision
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--readiness", default="output/complete/operational_readiness.json")
    parser.add_argument("--continuity", default="output/recovered/continuity_report.json")
    parser.add_argument("--output", default="output/f6_release_gate.json")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--fail-on-block", action="store_true")
    args = parser.parse_args()

    report = build_gate(args.readiness, args.continuity)
    print(json.dumps(report, indent=2, ensure_ascii=False))

    if args.write:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    if args.fail_on_block and report["decision"] != "release_candidate_operable":
        sys.exit(2)


if __name__ == "__main__":
    main()
