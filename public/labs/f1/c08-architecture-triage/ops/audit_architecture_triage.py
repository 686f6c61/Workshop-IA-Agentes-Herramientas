#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def conv_params(channels, filters, kernel):
    return filters * (kernel * kernel * channels + 1)


def lstm_params(input_dim, hidden_size):
    return 4 * hidden_size * (input_dim + hidden_size + 1)


def transformer_block_params(d_model):
    # Q, K, V, output projection and a two-layer FFN around 4*d_model.
    attention = 4 * d_model * d_model
    feed_forward = 8 * d_model * d_model
    return attention + feed_forward


def estimate_case(case, policy):
    risks = []
    candidates = []
    examples = case["examples"]
    if examples < policy["min_examples_for_deep_learning"]:
        risks.append("pocos_ejemplos_para_deep_learning")

    if case["input_type"] == "image_grid":
        cnn = policy["cnn"]
        params = conv_params(case["channels"], cnn["filters"], cnn["kernel"])
        activation_cells = case["height"] * case["width"] * cnn["filters"]
        candidates.append({
            "name": "CNN",
            "why": "la entrada tiene estructura de rejilla y patrones locales",
            "rough_params_first_conv": params,
            "activation_cells_first_map": activation_cells
        })
        candidates.append({
            "name": "Vision Transformer",
            "why": "posible si hay muchos datos y GPU, pero suele ser más caro al inicio",
            "rough_attention_cells_if_196_patches": 196 * 196
        })
        recommendation = "CNN"

    elif case["input_type"] == "time_series":
        seq = policy["sequence"]
        params = lstm_params(case["features"], seq["hidden_size"])
        candidates.append({
            "name": "LSTM/GRU",
            "why": "la secuencia es corta y el despliegue edge penaliza atención cuadrática",
            "rough_lstm_params": params
        })
        candidates.append({
            "name": "1D CNN temporal",
            "why": "buena alternativa si importan patrones locales y latencia baja"
        })
        recommendation = "LSTM/GRU o 1D CNN temporal"

    else:
        tokens = case["tokens"]
        attention_cells = tokens * tokens
        block_params = transformer_block_params(policy["transformer"]["d_model"]) * policy["transformer"]["layers"]
        if attention_cells > policy["max_attention_cells_for_simple_transformer"]:
            risks.append("atencion_cuadratica_cara")
        if case["input_type"] == "long_text":
            candidates.append({
                "name": "Transformer con RAG/chunking",
                "why": "el texto largo exige recuperar o trocear antes de pasar todo al contexto",
                "attention_cells_full_context": attention_cells,
                "rough_small_transformer_params": block_params
            })
            candidates.append({
                "name": "Clasificador por recuperación de fragmentos",
                "why": "si hay pocos ejemplos, conviene recuperar pasajes relevantes y clasificar sobre evidencias antes de entrenar"
            })
            recommendation = "Transformer con RAG o chunking"
        else:
            candidates.append({
                "name": "Embedding + clasificador lineal",
                "why": "para texto corto y pocas clases puede bastar antes de usar un LLM",
                "tokens": tokens
            })
            candidates.append({
                "name": "Transformer pequeño",
                "why": "útil si el orden y el contexto completo cambian la etiqueta",
                "attention_cells": attention_cells,
                "rough_small_transformer_params": block_params
            })
            recommendation = "Embedding + clasificador, comparado contra Transformer pequeño"

    latency_limit = policy["edge_latency_ms"] if case["deployment"].startswith("edge") else policy["cloud_latency_ms"]
    if case["latency_ms"] > latency_limit:
        risks.append("latencia_objetivo_revisar")

    valid = len(candidates) >= 2
    return {
        "id": case["id"],
        "title": case["title"],
        "input_type": case["input_type"],
        "deployment": case["deployment"],
        "recommendation": recommendation,
        "candidates": candidates,
        "risks": risks,
        "valid_for_first_experiment": valid
    }


def write_markdown(results):
    lines = [
        "# Decisión de arquitectura",
        "",
        "Este informe no elige modelo por moda. Elige una primera arquitectura por forma de datos, restricciones y coste aproximado.",
        "",
    ]
    for item in results:
        lines.extend([
            f"## {item['id']}: {item['title']}",
            "",
            f"- Entrada: `{item['input_type']}`.",
            f"- Despliegue: `{item['deployment']}`.",
            f"- Recomendación: **{item['recommendation']}**.",
            f"- Riesgos: {', '.join(item['risks']) if item['risks'] else 'sin bloqueos iniciales'}."
        ])
        lines.append("- Candidatos revisados:")
        for candidate in item["candidates"]:
            lines.append(f"  - `{candidate['name']}`: {candidate['why']}.")
        lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--fail-on-invalid", action="store_true")
    args = parser.parse_args()

    cases = load_json("data/problem_cases.json")
    policy = load_json("contracts/architecture_policy.json")
    results = [estimate_case(case, policy) for case in cases]
    report = {"results": results, "invalid": [r["id"] for r in results if not r["valid_for_first_experiment"]]}

    if args.write:
        (ROOT / "output").mkdir(exist_ok=True)
        (ROOT / "output/architecture_triage_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        (ROOT / "output/architecture_triage_decision.md").write_text(write_markdown(results), encoding="utf-8")

    print(json.dumps(report, indent=2, ensure_ascii=False))
    if args.fail_on_invalid and report["invalid"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
