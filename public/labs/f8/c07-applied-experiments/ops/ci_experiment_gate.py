#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POLICY = ROOT / "contracts" / "ci_gate_policy.json"
DEFAULT_OUTPUT = ROOT / "output"


def read_json(path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def check_required_files(policy):
    missing = []
    for item in policy["required_files"]:
        if not (ROOT / item).exists():
            missing.append(item)
    return missing


def build_report(policy):
    missing_files = check_required_files(policy)
    report_path = ROOT / "output" / "experiment_report.json"
    result = {
        "status": "pass",
        "missing_files": missing_files,
        "missing_report_fields": [],
        "reasons": [],
    }
    if missing_files:
        result["status"] = "block"
        result["reasons"].append("faltan archivos obligatorios")
        return result
    report = read_json(report_path)
    missing_fields = [field for field in policy["required_report_fields"] if field not in report]
    result["missing_report_fields"] = missing_fields
    if missing_fields:
        result["status"] = "block"
        result["reasons"].append("faltan campos obligatorios en experiment_report.json")
    if report.get("schema_errors"):
        result["status"] = "block"
        result["reasons"].append("schema_errors no está vacio")
    if report.get("srm", {}).get("status") == policy["block_if"]["srm_status"]:
        result["status"] = "block"
        result["reasons"].append("SRM bloquea")
    if any(item.get("status") == policy["block_if"]["any_guardrail_status"] for item in report.get("guardrails", [])):
        result["status"] = "block"
        result["reasons"].append("un guardrail bloquea")
    if result["status"] != "block" and report.get("readiness", {}).get("status") == policy["review_if"]["readiness_status"]:
        result["status"] = "review"
        result["reasons"].append("readiness queda en revisión")
    if result["status"] != "block" and report.get("status") == policy["review_if"]["decision_status"]:
        result["status"] = "review"
        result["reasons"].append("decision queda en revisión")
    if not result["reasons"]:
        result["reasons"].append("gate cumplido")
    return result


def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def render(result):
    lines = [
        "# CI gate del experimento",
        "",
        f"Estado: **{result['status']}**.",
        "",
        "## Motivos",
        "",
    ]
    for reason in result["reasons"]:
        lines.append(f"- {reason}.")
    if result["missing_files"]:
        lines.extend(["", "## Archivos faltantes", ""])
        for item in result["missing_files"]:
            lines.append(f"- `{item}`")
    if result["missing_report_fields"]:
        lines.extend(["", "## Campos faltantes", ""])
        for item in result["missing_report_fields"]:
            lines.append(f"- `{item}`")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    policy = read_json(args.policy)
    result = build_report(policy)
    if args.write:
        write_json(args.output_dir / "ci_gate_report.json", result)
        (args.output_dir / "ci_gate_decision.md").write_text(render(result), encoding="utf-8")
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    if args.strict and result["status"] == "block":
        sys.exit(1)


if __name__ == "__main__":
    main()
