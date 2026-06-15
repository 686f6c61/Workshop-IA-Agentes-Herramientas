#!/usr/bin/env python3
import argparse
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load_json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

def softmax(logits, temperature=1.0):
    adjusted = [z / temperature for z in logits]
    m = max(adjusted)
    exps = [math.exp(z - m) for z in adjusted]
    total = sum(exps)
    return [e / total for e in exps]

def kl(p, q):
    return sum(pi * math.log(pi / qi) for pi, qi in zip(p, q))

def build_report(case, policy):
    full = case["d_in"] * case["d_out"]
    lora = case["lora_rank"] * (case["d_in"] + case["d_out"])
    adapter = 2 * case["d_in"] * case["adapter_bottleneck"]
    probs = softmax(case["student_logits"])
    gradients = [p - (1 if i == case["target_index"] else 0) for i, p in enumerate(probs)]
    loss = -math.log(probs[case["target_index"]])
    teacher = softmax(case["teacher_logits"], case["distill_temperature"])
    student = softmax(case["distill_student_logits"], case["distill_temperature"])
    distill_kl = kl(teacher, student)
    memory = {str(bits): round(case["model_parameters"] * bits / 8 / 1_000_000_000, 4) for bits in case["bits"]}
    lora_percent = 100 * lora / full
    return {
        "full_params": full,
        "lora_params": lora,
        "adapter_params": adapter,
        "lora_trainable_percent": round(lora_percent, 6),
        "adapter_trainable_percent": round(100 * adapter / full, 6),
        "probabilities": {t: round(p, 6) for t, p in zip(case["tokens"], probs)},
        "gradients": {t: round(g, 6) for t, g in zip(case["tokens"], gradients)},
        "loss": round(loss, 6),
        "memory_gb": memory,
        "distillation_kl": round(distill_kl, 6),
        "gate_valid": lora_percent <= policy["max_lora_trainable_percent"] and memory["4"] <= policy["max_int4_7b_gb"] and distill_kl <= policy["max_distillation_kl"]
    }

def write_markdown(report):
    return "\n".join([
        "# Presupuesto de adaptación",
        "",
        f"LoRA entrena `{report['lora_trainable_percent']}` % de la matriz completa.",
        f"Adapter entrena `{report['adapter_trainable_percent']}` %.",
        f"Pérdida del ejemplo: `{report['loss']}`.",
        f"KL de destilación: `{report['distillation_kl']}`.",
        "",
        f"Memoria por bits: `{report['memory_gb']}`.",
        "",
        "La decisión no es solo técnica: adaptar pesos sirve para comportamiento estable; conocimiento vivo pide recuperación, herramientas o datos actualizados.",
    ]) + "\n"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--fail-on-invalid", action="store_true")
    args = parser.parse_args()
    report = build_report(load_json("data/adaptation_case.json"), load_json("contracts/adaptation_policy.json"))
    if args.write:
        (ROOT / "output").mkdir(exist_ok=True)
        (ROOT / "output/adaptation_budget_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        (ROOT / "output/adaptation_budget_decision.md").write_text(write_markdown(report), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if args.fail_on_invalid and not report["gate_valid"]:
        raise SystemExit(1)

if __name__ == "__main__":
    main()

