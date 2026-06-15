#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output"

COMMANDS = {
    "c01": ["python3", "ops/ai/eval_runner.py"],
    "c02": ["python3", "ops/ai/threshold_eval.py"],
    "c03": ["python3", "ops/ai/rag_eval.py"],
    "c04": ["python3", "ops/ai/evaluator_audit.py"],
}


EXPECTED = {
    "c01": ["output/eval_scorecard.json", "output/decision.md"],
    "c02": ["output/threshold_scorecard.json", "output/threshold_decision.md"],
    "c03": ["output/rag_scorecard.json", "output/rag_decision.md"],
    "c04": ["output/evaluator_audit_report.json", "output/evaluator_audit_decision.md"],
}


def run(chapter):
    result = subprocess.run(COMMANDS[chapter], cwd=ROOT, text=True, capture_output=True)
    checks = [
        {"name": "script_exit_zero", "passed": result.returncode == 0, "detail": result.stderr.strip()},
    ]
    for path in EXPECTED[chapter]:
        checks.append({"name": f"artifact:{path}", "passed": (ROOT / path).exists(), "detail": path})
    status = "valid" if all(item["passed"] for item in checks) else "invalid"
    report = {"chapter": chapter, "status": status, "checks": checks}
    (OUTPUT / f"{chapter}_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (OUTPUT / f"{chapter}_decision.md").write_text(f"# Decisión {chapter.upper()}\n\nEstado: `{status}`.\n", encoding="utf-8")
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--chapter", choices=sorted(COMMANDS))
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--fail-on-invalid", action="store_true")
    args = parser.parse_args()
    selected = sorted(COMMANDS) if args.all or not args.chapter else [args.chapter]
    OUTPUT.mkdir(parents=True, exist_ok=True)
    summary = {}
    invalid = []
    for chapter in selected:
        report = run(chapter)
        summary[chapter] = report["status"]
        if report["status"] != "valid":
            invalid.append(chapter)
    if args.write:
        (OUTPUT / "all_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    if invalid and args.fail_on_invalid:
        sys.exit(2)


if __name__ == "__main__":
    main()
