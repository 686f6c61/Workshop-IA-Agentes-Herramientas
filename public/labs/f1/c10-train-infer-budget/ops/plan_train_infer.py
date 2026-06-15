#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def weights_gb(params_b, precision, policy):
    if precision == "api":
        return 0.0
    return params_b * 1_000_000_000 * policy["bytes_per_precision"][precision] / 1_000_000_000


def kv_cache_gb(scenario, policy):
    if scenario["layers"] == 0:
        return 0.0
    bytes_per_value = policy["bytes_per_precision"][policy["kv_cache_precision"]]
    values = 2 * scenario["layers"] * scenario["context_tokens"] * scenario["hidden_size"] * scenario["batch_size"]
    return values * bytes_per_value / 1_000_000_000


def training_memory_gb(params_b, policy):
    return params_b * 1_000_000_000 * policy["adam_training_bytes_per_param"] / 1_000_000_000


def evaluate(scenario, policy):
    mode = scenario["mode"]
    risks = []
    train_mem = None
    weight_mem = weights_gb(scenario["model_params_b"], scenario["precision"], policy)
    kv_mem = kv_cache_gb(scenario, policy)
    total_infer = weight_mem + kv_mem
    safe_vram = scenario["gpu_vram_gb"] * policy["safe_vram_utilization"]

    if mode == "api_rag":
        recommendation = "API + RAG antes que fine-tuning"
        valid = True
    elif mode == "pretraining":
        train_mem = training_memory_gb(scenario["model_params_b"], policy)
        if scenario.get("training_tokens_b", 0) < policy["min_tokens_for_pretraining_b"]:
            risks.append("tokens_insuficientes_para_preentrenamiento")
        recommendation = "no entrenar desde cero sin corpus, presupuesto y evaluación mucho más sólidos"
        valid = True
    elif mode == "lora_finetune":
        train_mem = training_memory_gb(scenario["model_params_b"], policy) * 0.25
        if scenario["dataset_examples"] < policy["min_dataset_examples_for_finetune"]:
            risks.append("dataset_pequeno_para_ajuste")
        if total_infer > safe_vram:
            risks.append("inferencia_sin_margen_de_vram")
        recommendation = "LoRA/QLoRA si el problema es formato o tono estable, no conocimiento vivo"
        valid = True
    else:
        train_mem = None
        if total_infer > safe_vram:
            risks.append("no_cabe_con_margen_seguro")
        recommendation = "inferencia local viable con medición de latencia y calidad" if not risks else "probar modelo menor, menos contexto o API"
        valid = True

    return {
        "id": scenario["id"],
        "goal": scenario["goal"],
        "mode": mode,
        "weights_gb": round(weight_mem, 2),
        "kv_cache_gb": round(kv_mem, 2),
        "total_inference_memory_gb": round(total_infer, 2),
        "safe_vram_gb": round(safe_vram, 2),
        "rough_training_memory_gb": round(train_mem, 2) if isinstance(train_mem, (int, float)) else None,
        "recommendation": recommendation,
        "risks": risks,
        "valid_first_step": valid
    }


def write_markdown(results):
    lines = [
        "# Presupuesto de entrenamiento e inferencia",
        "",
        "Este informe separa pesos, KV cache y memoria aproximada de entrenamiento. Los números son de orden de magnitud: sirven para decidir si una idea merece prueba real.",
        "",
    ]
    for item in results:
        lines.extend([
            f"## {item['id']}",
            "",
            f"- Objetivo: {item['goal']}.",
            f"- Modo: `{item['mode']}`.",
            f"- Pesos: `{item['weights_gb']}` GB.",
            f"- KV cache: `{item['kv_cache_gb']}` GB.",
            f"- Memoria total de inferencia: `{item['total_inference_memory_gb']}` GB frente a `{item['safe_vram_gb']}` GB seguros.",
            f"- Memoria aproximada de entrenamiento: `{item['rough_training_memory_gb']}` GB.",
            f"- Recomendación: **{item['recommendation']}**.",
            f"- Riesgos: {', '.join(item['risks']) if item['risks'] else 'sin bloqueo inicial'}."
        ])
        lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--fail-on-invalid", action="store_true")
    args = parser.parse_args()

    policy = load_json("contracts/deployment_policy.json")
    scenarios = load_json("data/model_scenarios.json")
    results = [evaluate(scenario, policy) for scenario in scenarios]
    report = {"results": results, "invalid": [r["id"] for r in results if not r["valid_first_step"]]}

    if args.write:
        (ROOT / "output").mkdir(exist_ok=True)
        (ROOT / "output/train_infer_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        (ROOT / "output/train_infer_decision.md").write_text(write_markdown(results), encoding="utf-8")

    print(json.dumps(report, indent=2, ensure_ascii=False))
    if args.fail_on_invalid and report["invalid"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
