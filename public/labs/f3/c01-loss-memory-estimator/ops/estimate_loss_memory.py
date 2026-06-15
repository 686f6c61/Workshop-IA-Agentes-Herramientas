#!/usr/bin/env python3
import argparse
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load_json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

def nll(probabilities):
    return -sum(math.log(p) for p in probabilities)

def perplexity(probabilities):
    return math.exp(nll(probabilities) / len(probabilities))

def weight_gb(parameters_b, bytes_per_param):
    return parameters_b * bytes_per_param

def build_report(case, policy):
    before = case["token_probabilities"]["before"]
    after = case["token_probabilities"]["after"]
    memory = []
    for model in case["models"]:
        for precision in case["precisions"]:
            memory.append({
                "model": model["name"],
                "precision": precision["name"],
                "weights_gb": round(weight_gb(model["parameters_b"], precision["bytes_per_param"]), 3)
            })
    before_loss = nll(before)
    after_loss = nll(after)
    report = {
        "loss": {
            "before": round(before_loss, 4),
            "after": round(after_loss, 4),
            "decrease": round(before_loss - after_loss, 4),
            "perplexity_before": round(perplexity(before), 4),
            "perplexity_after": round(perplexity(after), 4)
        },
        "memory": memory
    }
    fp16_7b = next(x["weights_gb"] for x in memory if x["model"] == "7B" and x["precision"] == "FP16")
    int4_7b = next(x["weights_gb"] for x in memory if x["model"] == "7B" and x["precision"] == "INT4")
    report["gate_valid"] = (
        (not policy["require_loss_decrease"] or report["loss"]["decrease"] > 0)
        and fp16_7b <= policy["max_fp16_7b_gb"]
        and int4_7b <= policy["max_int4_7b_gb"]
    )
    return report

def write_markdown(report):
    lines = [
        "# Pérdida y memoria de un LLM",
        "",
        f"Pérdida antes: `{report['loss']['before']}`. Pérdida después: `{report['loss']['after']}`.",
        f"Perplexity antes: `{report['loss']['perplexity_before']}`. Perplexity después: `{report['loss']['perplexity_after']}`.",
        "",
        "| Modelo | Precisión | Memoria de pesos |",
        "|---|---|---:|",
    ]
    for item in report["memory"]:
        lines.append(f"| {item['model']} | {item['precision']} | {item['weights_gb']} GB |")
    lines.extend([
        "",
        "La memoria de pesos no incluye KV cache, activaciones, runtime ni margen operativo. Es solo el primer cálculo para no hablar a ciegas.",
    ])
    return "\n".join(lines) + "\n"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--fail-on-invalid", action="store_true")
    args = parser.parse_args()
    report = build_report(load_json("data/loss_memory_case.json"), load_json("contracts/loss_memory_policy.json"))
    if args.write:
        (ROOT / "output").mkdir(exist_ok=True)
        (ROOT / "output/loss_memory_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        (ROOT / "output/loss_memory_decision.md").write_text(write_markdown(report), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if args.fail_on_invalid and not report["gate_valid"]:
        raise SystemExit(1)

if __name__ == "__main__":
    main()

