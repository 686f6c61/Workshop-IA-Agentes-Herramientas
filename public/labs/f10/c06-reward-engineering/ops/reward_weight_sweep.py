#!/usr/bin/env python3
import argparse
import csv
from pathlib import Path

from audit_reward_card import DEFAULT_CONTRACT, DEFAULT_OUTPUT, DEFAULT_SPEC, build_sensitivity_rows, read_json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", default=str(DEFAULT_SPEC))
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT / "sensitivity_report.csv"))
    args = parser.parse_args()

    rows = build_sensitivity_rows(read_json(Path(args.spec)), read_json(Path(args.contract)))
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote={output}")
    print(f"rows={len(rows)}")


if __name__ == "__main__":
    main()
