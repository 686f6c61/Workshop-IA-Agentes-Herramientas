#!/usr/bin/env python3
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def simulate(case, version):
    if case["must_abstain"]:
        if version == "candidate":
            return {"text": "No tengo evidencia suficiente para confirmarlo.", "cost_eur": 0.012, "abstained": True}
        return {"text": "Sí, esa norma interna aplica.", "cost_eur": 0.018, "abstained": False}
    text = " ".join(case["expected_contains"]) + " respuesta con evidencia"
    cost = 0.024 if version == "candidate" else 0.029
    return {"text": text, "cost_eur": cost, "abstained": False}


def score_case(case, output):
    if case["must_abstain"]:
        return 1.0 if output["abstained"] else 0.0
    found = sum(1 for token in case["expected_contains"] if token.lower() in output["text"].lower())
    return found / max(1, len(case["expected_contains"]))


def evaluate(version, cases):
    rows = []
    critical = 0
    accepted_cost = []
    weighted = 0
    total_weight = 0
    for case in cases:
        output = simulate(case, version)
        quality = score_case(case, output)
        cost_ok = output["cost_eur"] <= case["max_cost_eur"]
        accepted = quality >= 1.0 and cost_ok
        if case["must_abstain"] and not output["abstained"]:
            critical += 1
        if accepted:
            accepted_cost.append(output["cost_eur"])
        weighted += quality * case["weight"]
        total_weight += case["weight"]
        rows.append({"case_id": case["case_id"], "quality": quality, "cost_ok": cost_ok, "accepted": accepted})
    return {
        "weighted_quality": round(weighted / total_weight, 4),
        "critical_failures": critical,
        "cost_per_accepted_eur": round(sum(accepted_cost) / max(1, len(accepted_cost)), 4),
        "rows": rows,
    }


def render_decision(report):
    return "\n".join([
        "# Decisión de eval",
        "",
        f"Estado: `{report['decision']}`.",
        "",
        "## Evidencia",
        "",
        f"- Baseline quality: `{report['baseline']['weighted_quality']}`.",
        f"- Candidate quality: `{report['candidate']['weighted_quality']}`.",
        f"- Critical failures candidate: `{report['candidate']['critical_failures']}`.",
        f"- Coste por aceptada candidate: `{report['candidate']['cost_per_accepted_eur']}`.",
        "",
    ])


def main():
    cases = read_jsonl(ROOT / "evals/eval_cases.jsonl")
    policy = read_json(ROOT / "ops/ai/eval_policy.json")
    baseline = evaluate("baseline", cases)
    candidate = evaluate("candidate", cases)
    regressions = sum(1 for old, new in zip(baseline["rows"], candidate["rows"]) if old["accepted"] and not new["accepted"])
    checks = {
        "quality_ok": candidate["weighted_quality"] >= policy["min_weighted_quality"],
        "critical_ok": candidate["critical_failures"] <= policy["max_critical_failures"],
        "cost_ok": candidate["cost_per_accepted_eur"] <= policy["max_cost_per_accepted_eur"],
        "regression_ok": regressions <= policy["max_regressions"],
    }
    decision = "publish_candidate" if all(checks.values()) else "block_candidate"
    report = {"baseline": baseline, "candidate": candidate, "checks": checks, "regressions": regressions, "decision": decision}
    out = ROOT / "output/eval_scorecard.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (ROOT / "output/decision.md").write_text(render_decision(report), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
