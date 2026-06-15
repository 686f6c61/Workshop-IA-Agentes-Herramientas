#!/usr/bin/env python3
import argparse
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load_json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

def softmax(scores):
    m = max(scores)
    exps = [math.exp(score - m) for score in scores]
    total = sum(exps)
    return [value / total for value in exps]

def mix(weights, values):
    return [
        sum(weight * value[column] for weight, value in zip(weights, values))
        for column in range(len(values[0]))
    ]

def build_report(case, policy):
    weights = softmax(case["scores_for_target"])
    top_token = case["tokens"][max(range(len(weights)), key=lambda index: weights[index])]
    vector = mix(weights, case["values"])
    return {
        "target_token": policy["target_token"],
        "weights": {token: round(weight, 6) for token, weight in zip(case["tokens"], weights)},
        "weight_sum": round(sum(weights), 8),
        "top_token": top_token,
        "contextual_vector": [round(value, 6) for value in vector],
        "gate_valid": abs(sum(weights) - 1.0) <= policy["weight_sum_tolerance"] and top_token == policy["expected_top_token"]
    }

def write_markdown(report):
    lines = [
        "# Mezcla de atención",
        "",
        f"Token observado: `{report['target_token']}`.",
        f"Token con mayor peso: `{report['top_token']}`.",
        f"Vector contextual: `{report['contextual_vector']}`.",
        "",
        "| Token | Peso |",
        "|---|---:|",
    ]
    for token, weight in report["weights"].items():
        lines.append(f"| {token} | {weight} |")
    lines.append("\nLa atención no copia un token: mezcla vectores de valor según pesos normalizados.")
    return "\n".join(lines) + "\n"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--fail-on-invalid", action="store_true")
    args = parser.parse_args()
    report = build_report(load_json("data/attention_case.json"), load_json("contracts/attention_policy.json"))
    if args.write:
        (ROOT / "output").mkdir(exist_ok=True)
        (ROOT / "output/attention_mixer_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        (ROOT / "output/attention_mixer_decision.md").write_text(write_markdown(report), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if args.fail_on_invalid and not report["gate_valid"]:
        raise SystemExit(1)

if __name__ == "__main__":
    main()

