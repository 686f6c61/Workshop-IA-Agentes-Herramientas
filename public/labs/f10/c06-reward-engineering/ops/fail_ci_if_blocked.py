#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", default="output/reward_card_audit_report.json")
    args = parser.parse_args()

    report = json.loads(Path(args.report).read_text(encoding="utf-8"))
    failing_checks = [
        name for name, passed in report.get("checks", {}).items()
        if not passed
    ]

    print(f"status={report['status']}")
    print(f"scenario_id={report['scenario_id']}")
    print(f"case_pass_rate={report['diagnostics']['case_pass_rate']}")
    print(f"failing_checks={','.join(failing_checks) if failing_checks else 'none'}")

    if report["status"] != "pass":
        sys.exit(1)


if __name__ == "__main__":
    main()
