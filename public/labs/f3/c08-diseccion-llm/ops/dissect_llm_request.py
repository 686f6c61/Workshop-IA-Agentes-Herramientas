#!/usr/bin/env python3
import argparse
import hashlib
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_json(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def rough_tokenize(text):
    return re.findall(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9_]+|[{}\[\]():,.;¿?¡!\"'`-]", text)


def token_id(token):
    digest = hashlib.sha1(token.encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % 100_000


def toy_embedding(token, width=8):
    digest = hashlib.sha256(token.encode("utf-8")).digest()
    values = []
    for index in range(width):
        raw = digest[index] / 255
        values.append(round((raw * 2) - 1, 4))
    return values


def softmax(logits, temperature):
    if temperature <= 0:
        raise ValueError("temperature debe ser > 0 para softmax")
    scaled = {token: value / temperature for token, value in logits.items()}
    max_logit = max(scaled.values())
    exp_values = {token: math.exp(value - max_logit) for token, value in scaled.items()}
    total = sum(exp_values.values())
    return {token: value / total for token, value in exp_values.items()}


def apply_top_k(probs, top_k):
    if not top_k:
        return probs
    keep = dict(sorted(probs.items(), key=lambda item: item[1], reverse=True)[:top_k])
    total = sum(keep.values())
    return {token: value / total for token, value in keep.items()}


def apply_top_p(probs, top_p):
    if not top_p or top_p >= 1:
        return probs
    selected = {}
    cumulative = 0.0
    for token, value in sorted(probs.items(), key=lambda item: item[1], reverse=True):
        selected[token] = value
        cumulative += value
        if cumulative >= top_p:
            break
    total = sum(selected.values())
    return {token: value / total for token, value in selected.items()}


def apply_min_p(probs, min_p):
    if not min_p:
        return probs
    max_prob = max(probs.values())
    selected = {token: value for token, value in probs.items() if value >= max_prob * min_p}
    total = sum(selected.values())
    return {token: value / total for token, value in selected.items()}


def entropy(probs):
    return -sum(value * math.log(value, 2) for value in probs.values() if value > 0)


def gb(value):
    return value / 1_000_000_000


def build_prompt(case):
    doc_block = "\n".join(
        f"[{doc['id']}] {doc['title']}: {doc['text']}" for doc in case["context_documents"]
    )
    fields = ", ".join(case["output_contract"]["required_fields"])
    return (
        f"SYSTEM:\n{case['system']}\n\n"
        f"DOCUMENTOS:\n{doc_block}\n\n"
        f"USUARIO:\n{case['user']}\n\n"
        f"CONTRATO:\nDevuelve JSON con campos obligatorios: {fields}."
    )


def runtime_estimate(case, prompt_token_count):
    shape = case["model_shape"]
    output_tokens = case["output_contract"]["max_output_tokens"]
    weights_gb = gb(shape["parameters_b"] * 1_000_000_000 * shape["weight_bits"] / 8)
    kv_values = (
        2
        * shape["layers"]
        * shape["batch_size"]
        * shape["num_ctx"]
        * shape["kv_heads"]
        * shape["head_dim"]
        * shape["bytes_per_kv_value"]
    )
    kv_full_mha_values = (
        2
        * shape["layers"]
        * shape["batch_size"]
        * shape["num_ctx"]
        * shape["attention_heads"]
        * shape["head_dim"]
        * shape["bytes_per_kv_value"]
    )
    kv_gb = gb(kv_values)
    kv_full_mha_gb = gb(kv_full_mha_values)
    prefill_seconds = prompt_token_count / shape["prefill_tokens_per_second"]
    decode_seconds = output_tokens / (shape["decode_tokens_per_second_total"] / shape["batch_size"])
    speculative = case["generation"].get("speculative_decoding", {})
    if speculative.get("enabled"):
        draft_tokens = max(speculative.get("draft_tokens_per_step", 1), 1)
        acceptance = min(max(speculative.get("expected_acceptance_rate", 0), 0), 1)
        # Toy estimate: useful for comparing scenarios, not for capacity planning.
        speedup = 1 + acceptance * (draft_tokens - 1) * 0.35
        speculative_decode_seconds = decode_seconds / speedup
    else:
        speedup = 1.0
        speculative_decode_seconds = decode_seconds
    return {
        "weights_gb": round(weights_gb, 3),
        "kv_cache_gb": round(kv_gb, 3),
        "kv_cache_full_mha_gb": round(kv_full_mha_gb, 3),
        "gqa_kv_cache_saving_percent": round((1 - kv_gb / kv_full_mha_gb) * 100, 1) if kv_full_mha_gb else 0,
        "prefill_seconds": round(prefill_seconds, 4),
        "decode_seconds_if_max_tokens": round(decode_seconds, 3),
        "speculative_decode_seconds_toy": round(speculative_decode_seconds, 3),
        "speculative_speedup_toy": round(speedup, 2),
        "estimated_ttft_seconds": round(prefill_seconds + 0.08, 4),
        "tokens_per_second_per_user": round(shape["decode_tokens_per_second_total"] / shape["batch_size"], 2)
    }


def build_report(case, vocab, policy):
    prompt = build_prompt(case)
    tokens = rough_tokenize(prompt)
    token_rows = [
        {"token": token, "id": token_id(token), "embedding_preview": toy_embedding(token, width=6)}
        for token in tokens[:18]
    ]
    generation = case["generation"]
    raw_probs = softmax(vocab["candidate_logits"], generation["temperature"])
    after_top_k = apply_top_k(raw_probs, generation["top_k"])
    after_top_p = apply_top_p(after_top_k, generation["top_p"])
    final_probs = apply_min_p(after_top_p, generation["min_p"])
    first_token = max(final_probs, key=final_probs.get)
    shape = case["model_shape"]
    tensor_shapes = {
        "token_ids": [1, len(tokens)],
        "embeddings": [1, len(tokens), shape["d_model"]],
        "q": [1, shape["attention_heads"], len(tokens), shape["head_dim"]],
        "k_cache": [shape["batch_size"], shape["kv_heads"], shape["num_ctx"], shape["head_dim"]],
        "v_cache": [shape["batch_size"], shape["kv_heads"], shape["num_ctx"], shape["head_dim"]],
        "logits": [1, len(vocab["candidate_logits"])]
    }
    runtime = runtime_estimate(case, len(tokens))
    architecture_signals = {
        "position_encoding": shape.get("position_encoding", "unknown"),
        "normalization": shape.get("normalization", "unknown"),
        "ffn_variant": shape.get("ffn_variant", "unknown"),
        "attention_heads": shape["attention_heads"],
        "kv_heads": shape["kv_heads"],
        "gqa_ratio": f"{shape['kv_heads']} KV heads / {shape['attention_heads']} attention heads",
        "lost_middle_risk": "moderado: los documentos quedan entre instrucciones y contrato; mide si la evidencia intermedia se recupera",
        "speculative_decoding": case["generation"].get("speculative_decoding", {"enabled": False}),
    }
    report_entropy = round(entropy(final_probs), 4)
    issues = []
    if first_token != policy["expected_first_token"]:
        issues.append("unexpected_first_token")
    if not (policy["min_prompt_tokens"] <= len(tokens) <= policy["max_prompt_tokens"]):
        issues.append("prompt_token_count_out_of_range")
    if report_entropy > policy["max_entropy_for_json"]:
        issues.append("entropy_too_high_for_json_contract")
    if runtime["estimated_ttft_seconds"] > policy["max_ttft_seconds"]:
        issues.append("ttft_too_high")
    if runtime["kv_cache_gb"] > policy["max_kv_cache_gb"]:
        issues.append("kv_cache_too_high")
    return {
        "case_id": case["case_id"],
        "goal": case["goal"],
        "prompt_token_count": len(tokens),
        "chars_per_token": round(len(prompt) / max(len(tokens), 1), 2),
        "token_preview": token_rows,
        "tensor_shapes": tensor_shapes,
        "architecture_signals": architecture_signals,
        "sampling": {
            "temperature": generation["temperature"],
            "top_k": generation["top_k"],
            "top_p": generation["top_p"],
            "min_p": generation["min_p"],
            "raw_probabilities": {k: round(v, 6) for k, v in raw_probs.items()},
            "final_probabilities": {k: round(v, 6) for k, v in final_probs.items()},
            "entropy_bits": report_entropy,
            "selected_first_token": first_token
        },
        "runtime": runtime,
        "engineering_decision": {
            "recommended_profile": "json_contract_low_variance",
            "why": "La tarea exige salida JSON verificable y cita; conviene bajar variabilidad, fijar contrato y medir tasa de parseo antes que creatividad.",
            "measure": ["json_parse_rate", "schema_pass_rate", "citation_supported_rate", "ttft_seconds", "kv_cache_gb"]
        },
        "gate_valid": not issues,
        "issues": issues
    }


def markdown(report):
    speculative = report["architecture_signals"]["speculative_decoding"]
    if speculative.get("enabled"):
        speculative_label = (
            f"draft_tokens={speculative['draft_tokens_per_step']}, "
            f"acceptance={speculative['expected_acceptance_rate']}"
        )
    else:
        speculative_label = "desactivado"
    lines = [
        "# Diseccion de una llamada a un LLM",
        "",
        f"Caso: `{report['case_id']}`.",
        "",
        "## Tokenizacion",
        "",
        f"El prompt ensamblado queda en `{report['prompt_token_count']}` tokens aproximados, con `{report['chars_per_token']}` caracteres por token. Esta cifra no sustituye a un tokenizer real, pero entrena la idea clave: coste, contexto y truncamiento empiezan antes de llamar al modelo.",
        "",
        "| Token | ID simulado | Embedding preview |",
        "|---|---:|---|",
    ]
    for row in report["token_preview"][:10]:
        lines.append(f"| `{row['token']}` | {row['id']} | `{row['embedding_preview']}` |")
    lines.extend([
        "",
        "## Formas de tensores",
        "",
        "| Pieza | Shape | Lectura de ingenieria |",
        "|---|---|---|",
        f"| `token_ids` | `{report['tensor_shapes']['token_ids']}` | Secuencia discreta que entra al modelo. |",
        f"| `embeddings` | `{report['tensor_shapes']['embeddings']}` | Cada token ya es un vector de anchura `d_model`. |",
        f"| `q` | `{report['tensor_shapes']['q']}` | Consultas de atencion por cabeza. |",
        f"| `k_cache` | `{report['tensor_shapes']['k_cache']}` | Claves cacheadas para evitar recomputar contexto. |",
        f"| `v_cache` | `{report['tensor_shapes']['v_cache']}` | Valores cacheados que se mezclan durante decode. |",
        f"| `logits` | `{report['tensor_shapes']['logits']}` | Una puntuacion por token candidato del vocabulario simulado. |",
        "",
        "## Arquitectura y runtime moderno",
        "",
        "| Señal | Valor | Lectura de ingenieria |",
        "|---|---|---|",
        f"| Posicion | `{report['architecture_signals']['position_encoding']}` | La posicion afecta a la atencion; contexto largo no garantiza recuperar bien lo que queda en medio. |",
        f"| Normalizacion | `{report['architecture_signals']['normalization']}` | Estabiliza activaciones; importa al cuantizar o comparar runtimes. |",
        f"| FFN | `{report['architecture_signals']['ffn_variant']}` | No es relleno: transforma cada posicion entre rondas de atencion. |",
        f"| GQA | `{report['architecture_signals']['gqa_ratio']}` | Menos cabezas KV reducen memoria de cache frente a MHA completa. |",
        f"| Ahorro KV por GQA | `{report['runtime']['gqa_kv_cache_saving_percent']}%` | En este caso toy, la cache seria `{report['runtime']['kv_cache_full_mha_gb']}` GB con MHA completa. |",
        f"| Lost in the middle | `{report['architecture_signals']['lost_middle_risk']}` | No metas documentos sin medir posicion, orden y recuperacion real. |",
        f"| Speculative decoding | `{speculative_label}` | Acelera si el modelo draft propone tokens que el modelo grande acepta. |",
        "",
        "## Logits y sampling",
        "",
        f"Perfil usado: `temperature={report['sampling']['temperature']}`, `top_k={report['sampling']['top_k']}`, `top_p={report['sampling']['top_p']}`, `min_p={report['sampling']['min_p']}`.",
        "",
        "| Token candidato | Probabilidad final |",
        "|---|---:|",
    ])
    for token, prob in sorted(report["sampling"]["final_probabilities"].items(), key=lambda item: item[1], reverse=True):
        lines.append(f"| `{token}` | {prob} |")
    lines.extend([
        "",
        f"Token seleccionado: `{report['sampling']['selected_first_token']}`. Entropia final: `{report['sampling']['entropy_bits']}` bits.",
        "",
        "## KV cache y runtime",
        "",
        "| Medida | Valor | Por que importa |",
        "|---|---:|---|",
        f"| Pesos | {report['runtime']['weights_gb']} GB | Memoria del modelo cuantizado. |",
        f"| KV cache | {report['runtime']['kv_cache_gb']} GB | Memoria temporal que crece con contexto, batch y `num_ctx`. |",
        f"| TTFT estimado | {report['runtime']['estimated_ttft_seconds']} s | Tiempo hasta empezar a ver respuesta. |",
        f"| Decode max | {report['runtime']['decode_seconds_if_max_tokens']} s | Tiempo si se consume todo `max_output_tokens`. |",
        f"| Decode con speculative toy | {report['runtime']['speculative_decode_seconds_toy']} s | Estimacion pedagogica; en un runtime real se mide con ratio de aceptacion. |",
        f"| Tokens/s por usuario | {report['runtime']['tokens_per_second_per_user']} | Throughput repartido por batch. |",
        "",
        "## Decision de ingenieria",
        "",
        report["engineering_decision"]["why"],
        "",
        "Mide como minimo: " + ", ".join(f"`{item}`" for item in report["engineering_decision"]["measure"]) + ".",
        "",
        f"Gate valido: `{report['gate_valid']}`.",
    ])
    if report["issues"]:
        lines.append("")
        lines.append("Issues: " + ", ".join(report["issues"]))
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--fail-on-invalid", action="store_true")
    args = parser.parse_args()
    report = build_report(
        load_json("data/request_case.json"),
        load_json("data/toy_vocab.json"),
        load_json("contracts/dissection_policy.json"),
    )
    if args.write:
        (ROOT / "output").mkdir(exist_ok=True)
        (ROOT / "output/dissection_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        (ROOT / "output/dissection_report.md").write_text(markdown(report), encoding="utf-8")
    print(json.dumps({
        "case_id": report["case_id"],
        "prompt_token_count": report["prompt_token_count"],
        "selected_first_token": report["sampling"]["selected_first_token"],
        "kv_cache_gb": report["runtime"]["kv_cache_gb"],
        "gate_valid": report["gate_valid"],
        "issues": report["issues"]
    }, indent=2, ensure_ascii=False))
    if args.fail_on_invalid and not report["gate_valid"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
