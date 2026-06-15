#!/usr/bin/env python3
import argparse
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load_json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

def layer_norm(x, eps=1e-5):
    mean = sum(x) / len(x)
    variance = sum((v - mean) ** 2 for v in x) / len(x)
    sigma = math.sqrt(variance + eps)
    return [(v - mean) / sigma for v in x]

def softmax(logits, temperature=1.0):
    adjusted = [z / temperature for z in logits]
    m = max(adjusted)
    exps = [math.exp(z - m) for z in adjusted]
    total = sum(exps)
    return [e / total for e in exps]

def top_k(probs, k):
    indexes = sorted(range(len(probs)), key=lambda i: probs[i], reverse=True)[:k]
    total = sum(probs[i] for i in indexes)
    return [probs[i] / total if i in indexes else 0.0 for i in range(len(probs))]

def top_p(probs, p):
    order = sorted(range(len(probs)), key=lambda i: probs[i], reverse=True)
    chosen, acc = [], 0.0
    for i in order:
        chosen.append(i)
        acc += probs[i]
        if acc >= p:
            break
    total = sum(probs[i] for i in chosen)
    return [probs[i] / total if i in chosen else 0.0 for i in range(len(probs))]

def entropy(probs):
    return -sum(p * math.log(p) for p in probs if p > 0)

def build_report(case, policy):
    distributions = []
    for temperature in case["temperatures"]:
        probs = softmax(case["logits"], temperature)
        distributions.append({
            "temperature": temperature,
            "probs": {t: round(p, 6) for t, p in zip(case["tokens"], probs)},
            "entropy": round(entropy(probs), 6)
        })
    base = softmax(case["logits"])
    topk = top_k(base, policy["top_k"])
    topp = top_p(base, policy["top_p"])
    valid = all(abs(sum(list(item["probs"].values())) - 1.0) <= policy["prob_sum_tolerance"] for item in distributions)
    valid = valid and abs(sum(topk) - 1.0) <= policy["prob_sum_tolerance"] and abs(sum(topp) - 1.0) <= policy["prob_sum_tolerance"]
    return {
        "layer_norm": [round(v, 6) for v in layer_norm(case["vector"])],
        "temperature_distributions": distributions,
        "top_k": {t: round(p, 6) for t, p in zip(case["tokens"], topk)},
        "top_p": {t: round(p, 6) for t, p in zip(case["tokens"], topp)},
        "gate_valid": valid
    }

def write_markdown(report):
    lines = ["# LayerNorm y sampling", "", f"LayerNorm: `{report['layer_norm']}`.", "", "| Temperatura | Entropía |", "|---:|---:|"]
    for item in report["temperature_distributions"]:
        lines.append(f"| {item['temperature']} | {item['entropy']} |")
    lines.extend(["", f"Top-k: `{report['top_k']}`.", f"Top-p: `{report['top_p']}`.", "Temperatura controla concentración; top-k y top-p recortan el conjunto candidato."])
    return "\n".join(lines) + "\n"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--fail-on-invalid", action="store_true")
    args = parser.parse_args()
    report = build_report(load_json("data/sampling_case.json"), load_json("contracts/sampling_policy.json"))
    if args.write:
        (ROOT / "output").mkdir(exist_ok=True)
        (ROOT / "output/sampling_controls_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        (ROOT / "output/sampling_controls_decision.md").write_text(write_markdown(report), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if args.fail_on_invalid and not report["gate_valid"]:
        raise SystemExit(1)

if __name__ == "__main__":
    main()

