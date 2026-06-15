#!/usr/bin/env python3
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def main():
    rubric = json.loads((ROOT / "evals/evaluator_rubric.json").read_text(encoding="utf-8"))
    cases = {row["case_id"]: row for row in json.loads((ROOT / "evals/evaluator_calibration_cases.json").read_text(encoding="utf-8"))}
    outputs = json.loads((ROOT / "evals/evaluator_outputs.json").read_text(encoding="utf-8"))
    matches = 0
    false_passes = 0
    parse_errors = 0
    costs = []
    for out in outputs:
        human = cases[out["case_id"]]["human"]["pass"]
        pred = out["evaluator_pass"]
        matches += pred == human
        false_passes += pred == 1 and human == 0
        parse_errors += not out["parse_ok"]
        costs.append(out["cost_eur"])
    agreement = matches / len(outputs)
    cost = sum(costs) / len(costs)
    checks = {
        "agreement_ok": agreement >= rubric["min_agreement"],
        "false_passes_ok": false_passes <= rubric["max_false_passes"],
        "parse_ok": parse_errors <= rubric["max_parse_errors"],
        "cost_ok": cost <= rubric["max_cost_per_valid_evaluation"],
    }
    report = {"agreement": round(agreement, 4), "false_passes": false_passes, "parse_errors": parse_errors, "cost_per_eval": round(cost, 4), "checks": checks, "decision": "use_evaluator_with_monitoring" if all(checks.values()) else "do_not_use_evaluator"}
    (ROOT / "output/evaluator_audit_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (ROOT / "output/evaluator_audit_decision.md").write_text(f"# Decisión del evaluador\n\nEstado: `{report['decision']}`.\n\nAcuerdo: `{report['agreement']}`.\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
