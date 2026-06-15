#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load_json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

def score(option, weights):
    return sum(option[key] * weight for key, weight in weights.items())

def build_report(case, policy):
    weights = case["weights"]
    scores = {
        name: {
            "score": round(score(values, weights), 6),
            "criteria": values
        }
        for name, values in case["options"].items()
    }
    ranking = sorted(scores, key=lambda name: scores[name]["score"], reverse=True)
    winner = ranking[0]
    return {
        "weights_sum": round(sum(weights.values()), 8),
        "ranking": ranking,
        "scores": scores,
        "winner": winner,
        "gate_valid": (
            abs(sum(weights.values()) - 1.0) <= policy["weights_sum_tolerance"]
            and winner == policy["expected_winner"]
            and case["options"][winner]["contexto_externo"] >= policy["min_context_score"]
        )
    }

def write_markdown(report):
    lines = ["# Matriz de estrategia de modelo", "", f"Ganador: `{report['winner']}`.", "", "| Opción | Score |", "|---|---:|"]
    for name in report["ranking"]:
        lines.append(f"| {name} | {report['scores'][name]['score']} |")
    lines.extend(["", "La matriz no decide sola: fuerza a escribir qué pesa más en este caso y deja una decisión revisable."])
    return "\n".join(lines) + "\n"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--fail-on-invalid", action="store_true")
    args = parser.parse_args()
    report = build_report(load_json("data/model_strategy_case.json"), load_json("contracts/model_strategy_policy.json"))
    if args.write:
        (ROOT / "output").mkdir(exist_ok=True)
        (ROOT / "output/model_strategy_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        (ROOT / "output/model_strategy_decision.md").write_text(write_markdown(report), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if args.fail_on_invalid and not report["gate_valid"]:
        raise SystemExit(1)

if __name__ == "__main__":
    main()

