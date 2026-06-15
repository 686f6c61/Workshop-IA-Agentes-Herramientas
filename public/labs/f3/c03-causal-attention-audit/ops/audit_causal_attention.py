#!/usr/bin/env python3
import argparse
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load_json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

def matmul(a, b):
    columns = list(zip(*b))
    return [[sum(x * y for x, y in zip(row, col)) for col in columns] for row in a]

def softmax(row):
    m = max(row)
    exps = [math.exp(x - m) for x in row]
    total = sum(exps)
    return [x / total for x in exps]

def causal_attention(case):
    q = matmul(case["X"], case["Wq"])
    k = matmul(case["X"], case["Wk"])
    v = matmul(case["X"], case["Wv"])
    scale = math.sqrt(len(k[0]))
    weights, output = [], []
    for i, qi in enumerate(q):
        visible_scores = [sum(a * b for a, b in zip(qi, kj)) / scale for kj in k[: i + 1]]
        visible_weights = softmax(visible_scores)
        row = visible_weights + [0.0] * (len(k) - len(visible_weights))
        weights.append(row)
        output.append([sum(row[j] * v[j][col] for j in range(len(v))) for col in range(len(v[0]))])
    return q, k, v, weights, output

def build_report(case, policy):
    q, k, v, weights, output = causal_attention(case)
    future_ok = all(weights[i][j] <= policy["future_weight_tolerance"] for i in range(len(weights)) for j in range(i + 1, len(weights)))
    rows_ok = all(abs(sum(row) - 1.0) <= policy["row_sum_tolerance"] for row in weights)
    return {
        "tokens": case["tokens"],
        "Q": [[round(x, 6) for x in row] for row in q],
        "K": [[round(x, 6) for x in row] for row in k],
        "V": [[round(x, 6) for x in row] for row in v],
        "weights": [[round(x, 6) for x in row] for row in weights],
        "output": [[round(x, 6) for x in row] for row in output],
        "future_mask_ok": future_ok,
        "row_sums_ok": rows_ok,
        "gate_valid": future_ok and rows_ok
    }

def write_markdown(report):
    lines = ["# Auditoría QKV y máscara causal", "", "| Token | Pesos visibles |", "|---|---|"]
    for token, row in zip(report["tokens"], report["weights"]):
        lines.append(f"| {token} | `{row}` |")
    lines.extend(["", f"Máscara causal correcta: `{report['future_mask_ok']}`.", "Cada fila suma 1 y las posiciones futuras quedan con peso 0."])
    return "\n".join(lines) + "\n"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--fail-on-invalid", action="store_true")
    args = parser.parse_args()
    report = build_report(load_json("data/qkv_case.json"), load_json("contracts/causal_attention_policy.json"))
    if args.write:
        (ROOT / "output").mkdir(exist_ok=True)
        (ROOT / "output/causal_attention_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        (ROOT / "output/causal_attention_decision.md").write_text(write_markdown(report), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if args.fail_on_invalid and not report["gate_valid"]:
        raise SystemExit(1)

if __name__ == "__main__":
    main()

