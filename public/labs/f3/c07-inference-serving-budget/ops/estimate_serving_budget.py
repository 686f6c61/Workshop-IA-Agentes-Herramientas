#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load_json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

def gb_bytes(value):
    return value / 1_000_000_000

def weights_gb(params, bits):
    return gb_bytes(params * bits / 8)

def kv_cache_gb(layers, batch, sequence, kv_heads, head_dim, bytes_per_value):
    values = 2 * layers * batch * sequence * kv_heads * head_dim
    return gb_bytes(values * bytes_per_value)

def latency(ttft_ms, output_tokens, tps):
    return ttft_ms / 1000 + output_tokens / tps

def build_report(case, policy):
    weights = {str(bits): round(weights_gb(case["parameters"], bits), 4) for bits in case["bits"]}
    kv = {
        name: round(kv_cache_gb(case["layers"], case["batch"], case["sequence"], heads, case["head_dim"], case["bytes_per_value"]), 4)
        for name, heads in case["kv_heads"].items()
    }
    isolated = latency(case["ttft_ms"], case["output_tokens"], case["tokens_per_second_single_user"])
    shared_tps = case["total_capacity_tokens_per_second"] / case["concurrent_users"]
    shared = latency(case["ttft_ms"], case["output_tokens"], shared_tps)
    return {
        "weights_gb": weights,
        "kv_cache_gb": kv,
        "latency_single_user_s": round(isolated, 4),
        "latency_shared_s": round(shared, 4),
        "shared_tokens_per_second_per_user": round(shared_tps, 4),
        "gate_valid": kv["GQA"] <= policy["max_gqa_kv_cache_gb"] and shared <= policy["max_shared_latency_s"]
    }

def write_markdown(report):
    lines = ["# Presupuesto de inferencia y serving", "", f"Memoria de pesos: `{report['weights_gb']}`.", f"KV cache: `{report['kv_cache_gb']}`.", f"Latencia usuario aislado: `{report['latency_single_user_s']}` s.", f"Latencia compartida: `{report['latency_shared_s']}` s.", "", "Si solo miras pesos, ignoras una parte grande del serving: KV cache, concurrencia y throughput."]
    return "\n".join(lines) + "\n"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--fail-on-invalid", action="store_true")
    args = parser.parse_args()
    report = build_report(load_json("data/serving_scenario.json"), load_json("contracts/serving_policy.json"))
    if args.write:
        (ROOT / "output").mkdir(exist_ok=True)
        (ROOT / "output/serving_budget_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        (ROOT / "output/serving_budget_decision.md").write_text(write_markdown(report), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if args.fail_on_invalid and not report["gate_valid"]:
        raise SystemExit(1)

if __name__ == "__main__":
    main()

