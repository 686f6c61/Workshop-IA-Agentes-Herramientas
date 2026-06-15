#!/usr/bin/env python3
import json
import math
from pathlib import Path


SCENARIO = {
    "prompt_tokens": 1800,
    "output_tokens": 450,
    "prefill_tokens_per_s": 9000,
    "decode_tokens_per_s": 55,
    "ttft_ms": 700,
    "target_rps": 3.0,
    "workers": 64,
}


def estimate(s):
    prefill_s = s["prompt_tokens"] / s["prefill_tokens_per_s"]
    decode_s = s["output_tokens"] / s["decode_tokens_per_s"]
    service_s = prefill_s + decode_s + s["ttft_ms"] / 1000
    capacity_rps = s["workers"] / service_s
    required_workers = math.ceil(s["target_rps"] * service_s * 2)
    return {
        "prefill_s": round(prefill_s, 3),
        "decode_s": round(decode_s, 3),
        "service_s": round(service_s, 3),
        "capacity_rps": round(capacity_rps, 3),
        "required_workers_for_2x_margin": required_workers,
        "decision": "capacity_ok" if capacity_rps >= s["target_rps"] * 2 else "add_workers_or_reduce_tokens",
    }


if __name__ == "__main__":
    report = {"scenario": SCENARIO, "estimate": estimate(SCENARIO)}
    out = Path("output/serving_capacity_report.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
