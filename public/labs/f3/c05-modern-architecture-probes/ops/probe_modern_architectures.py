#!/usr/bin/env python3
import argparse
import json
import math
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load_json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

def softmax(scores):
    m = max(scores)
    exps = [math.exp(s - m) for s in scores]
    total = sum(exps)
    return [e / total for e in exps]

def route(experts, scores, k):
    probs = softmax(scores)
    chosen = sorted(range(len(probs)), key=lambda i: probs[i], reverse=True)[:k]
    total = sum(probs[i] for i in chosen)
    return [{"expert": experts[i], "weight": round(probs[i] / total, 6)} for i in chosen]

def cosine(a, b):
    num = sum(x * y for x, y in zip(a, b))
    da = math.sqrt(sum(x * x for x in a))
    db = math.sqrt(sum(y * y for y in b))
    return num / (da * db)

def build_report(case, policy):
    routing = route(case["experts"], case["routing_scores"], policy["top_k_experts"])
    answer, count = Counter(case["self_consistency_answers"]).most_common(1)[0]
    similarities = {text: round(cosine(case["image_vector"], vector), 6) for text, vector in case["text_vectors"].items()}
    top_text = max(similarities, key=similarities.get)
    return {
        "routing": routing,
        "self_consistency": {"answer": answer, "votes": count, "total": len(case["self_consistency_answers"])},
        "image_text_similarity": similarities,
        "top_text": top_text,
        "gate_valid": routing[0]["expert"] == policy["expected_top_expert"] and similarities[top_text] >= policy["min_top_image_text_similarity"]
    }

def write_markdown(report):
    lines = ["# Sondas de arquitecturas modernas", "", "## Routing MoE", ""]
    for item in report["routing"]:
        lines.append(f"- `{item['expert']}` con peso `{item['weight']}`.")
    lines.extend([
        "",
        f"Self-consistency elige `{report['self_consistency']['answer']}` con `{report['self_consistency']['votes']}/{report['self_consistency']['total']}` votos.",
        "",
        "## Alineación imagen-texto",
        "",
        "| Texto | Similitud |",
        "|---|---:|",
    ])
    for text, value in report["image_text_similarity"].items():
        lines.append(f"| {text} | {value} |")
    lines.append("\nEstas sondas no prueban calidad de modelo, pero sí hacen visible qué señal toma cada mecanismo.")
    return "\n".join(lines) + "\n"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--fail-on-invalid", action="store_true")
    args = parser.parse_args()
    report = build_report(load_json("data/modern_architecture_case.json"), load_json("contracts/modern_architecture_policy.json"))
    if args.write:
        (ROOT / "output").mkdir(exist_ok=True)
        (ROOT / "output/modern_architecture_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        (ROOT / "output/modern_architecture_decision.md").write_text(write_markdown(report), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if args.fail_on_invalid and not report["gate_valid"]:
        raise SystemExit(1)

if __name__ == "__main__":
    main()

