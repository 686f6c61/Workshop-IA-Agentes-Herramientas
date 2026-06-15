#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCENARIO = ROOT / "data" / "inference_scenario.json"
DEFAULT_CONTRACT = ROOT / "contracts" / "arquitecturas_lab_contract.json"
DEFAULT_OUTPUT_DIR = ROOT / "output"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def gb(bytes_value):
    return bytes_value / 1_000_000_000


def estimate(scenario, contract):
    model = scenario["model"]
    serving = scenario["serving"]
    weights_gb = gb(model["parameters"] * model["weight_bits"] / 8)
    kv_gb = gb(
        2
        * model["layers"]
        * serving["batch"]
        * serving["context_tokens"]
        * model["kv_heads"]
        * model["head_dim"]
        * model["kv_bytes"]
    )
    total_memory_gb = weights_gb + kv_gb + serving["runtime_margin_gb"]
    tokens_per_user = serving["aggregate_decode_tokens_per_second"] / serving["batch"]
    decode_seconds = serving["output_tokens_per_user"] / tokens_per_user
    status = (
        "redisenar_serving"
        if decode_seconds > contract["inference_gate"]["max_decode_seconds_interactive"]
        else "prototipo_interactivo"
    )
    return {
        "scenario_id": scenario["scenario_id"],
        "weights_gb": round(weights_gb, 3),
        "kv_cache_gb": round(kv_gb, 3),
        "runtime_margin_gb": serving["runtime_margin_gb"],
        "estimated_total_memory_gb": round(total_memory_gb, 3),
        "tokens_per_second_per_user": round(tokens_per_user, 3),
        "decode_seconds_per_user": round(decode_seconds, 3),
        "status": status,
        "why": "La memoria parece tratable, pero la latencia de decode no sirve para una experiencia interactiva." if status == "redisenar_serving" else "La estimación entra en el objetivo interactivo inicial."
    }


def render_memo(report):
    lines = [
        "# Memo de inferencia",
        "",
        f"Decisión: `{report['status']}`.",
        "",
        "| Magnitud | Valor |",
        "|---|---:|",
        f"| Pesos | {report['weights_gb']} GB |",
        f"| KV cache | {report['kv_cache_gb']} GB |",
        f"| Margen runtime | {report['runtime_margin_gb']} GB |",
        f"| Memoria total estimada | {report['estimated_total_memory_gb']} GB |",
        f"| Decode por usuario | {report['tokens_per_second_per_user']} tokens/s |",
        f"| Tiempo de decode por usuario | {report['decode_seconds_per_user']} s |",
        "",
        "## Lectura",
        "",
        report["why"],
        "",
        "## Acciones técnicas",
        "",
        "- Reducir salida esperada o generar por secciones.",
        "- Medir prefill y decode por separado.",
        "- Probar batching continuo en un servidor de inferencia real.",
        "- Comparar un modelo menor, cuantización distinta o más capacidad de serving.",
        "- No comprar hardware solo porque los pesos quepan en memoria.",
        "",
    ]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", type=Path, default=DEFAULT_SCENARIO)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--fail-on-review", action="store_true")
    args = parser.parse_args()

    report = estimate(read_json(args.scenario), read_json(args.contract))
    if args.write:
        write_json(args.output_dir / "inference_budget.json", report)
        (args.output_dir / "deployment_memo.md").write_text(render_memo(report), encoding="utf-8")
    print(json.dumps({"status": report["status"], "decode_seconds_per_user": report["decode_seconds_per_user"]}, ensure_ascii=False, indent=2))
    if args.fail_on_review and report["status"] != "redisenar_serving":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
