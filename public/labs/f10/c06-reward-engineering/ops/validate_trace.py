#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

from audit_reward_card import DEFAULT_SPEC, read_json, score_candidate


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTRACT = ROOT / "contracts" / "reward_run_trace_contract.json"
DEFAULT_TRACE = ROOT / "data" / "reward_run_trace.json"
DEFAULT_OUTPUT = ROOT / "output" / "trace_validation_report.json"


def validate_trace(trace, contract, spec, tolerance=1e-6):
    errors = []
    warnings = []

    missing = [field for field in contract["required_fields"] if field not in trace]
    for field in missing:
        errors.append(f"missing field: {field}")

    if trace.get("reward_card_version") != spec.get("reward_card_version"):
        errors.append("reward_card_version does not match reward spec")

    term_names = [term["name"] for term in spec["reward_terms"]]
    component_scores = trace.get("component_scores", {})
    missing_terms = [name for name in term_names if name not in component_scores]
    extra_terms = sorted(set(component_scores) - set(term_names))
    for name in missing_terms:
        errors.append(f"missing component score: {name}")
    for name in extra_terms:
        warnings.append(f"extra component score: {name}")

    hard_gates = trace.get("hard_gates", {})
    required_gates = [
        gate["name"] for gate in spec.get("hard_gates", [])
        if gate.get("required")
    ]
    for name in required_gates:
        if name not in hard_gates:
            errors.append(f"missing hard gate: {name}")
        elif hard_gates[name] is not True:
            errors.append(f"hard gate failed: {name}")

    if not trace.get("grader_versions"):
        errors.append("grader_versions must not be empty")

    for numeric_field in ["latency_ms", "input_tokens", "output_tokens"]:
        if numeric_field in trace and float(trace[numeric_field]) < 0:
            errors.append(f"{numeric_field} must be non-negative")

    if not missing_terms and "reward" in trace:
        candidate = {"scores": component_scores}
        expected_reward, contributions = score_candidate(candidate, spec["reward_terms"])
        if abs(float(trace["reward"]) - expected_reward) > tolerance:
            errors.append(
                f"reward mismatch: trace={trace['reward']} computed={expected_reward}"
            )
    else:
        contributions = {}
        expected_reward = None

    return {
        "trace_id": trace.get("trace_id"),
        "status": "pass" if not errors else "block",
        "errors": errors,
        "warnings": warnings,
        "computed_reward": expected_reward,
        "contributions": contributions,
        "required_fields": contract["required_fields"],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--trace", default=str(DEFAULT_TRACE))
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT))
    parser.add_argument("--spec", default=str(DEFAULT_SPEC))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    trace = read_json(Path(args.trace))
    contract = read_json(Path(args.contract))
    spec = read_json(Path(args.spec))
    report = validate_trace(trace, contract, spec)

    if args.write:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    print(f"status={report['status']}")
    print(f"trace_id={report['trace_id']}")
    print(f"errors={len(report['errors'])}")
    for error in report["errors"]:
        print(f"- {error}")


if __name__ == "__main__":
    main()
