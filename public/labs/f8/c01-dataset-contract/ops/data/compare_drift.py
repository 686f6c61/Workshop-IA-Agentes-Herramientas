#!/usr/bin/env python3
import argparse
import csv
import json
import math
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REFERENCE = ROOT / "data" / "support_cases.csv"
DEFAULT_CURRENT = ROOT / "data" / "production_sample.csv"
DEFAULT_OUTPUT = ROOT / "output"


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def distribution(rows, column):
    counts = Counter(row[column] for row in rows if row.get(column))
    total = sum(counts.values()) or 1
    return {key: count / total for key, count in sorted(counts.items())}


def smooth_distribution(left, right, epsilon=1e-9):
    keys = sorted(set(left) | set(right))
    return keys, [left.get(key, 0.0) + epsilon for key in keys], [right.get(key, 0.0) + epsilon for key in keys]


def total_variation(left, right):
    keys, p, q = smooth_distribution(left, right)
    return round(0.5 * sum(abs(a - b) for a, b in zip(p, q)), 6), keys


def kl_divergence(left, right):
    _, p, q = smooth_distribution(left, right)
    return round(sum(a * math.log(a / b) for a, b in zip(p, q)), 6)


def jensen_shannon(left, right):
    keys, p, q = smooth_distribution(left, right)
    midpoint = [(a + b) / 2 for a, b in zip(p, q)]
    js = 0.5 * sum(a * math.log(a / m) for a, m in zip(p, midpoint))
    js += 0.5 * sum(b * math.log(b / m) for b, m in zip(q, midpoint))
    return round(js, 6), keys


def psi(left, right):
    keys, p, q = smooth_distribution(left, right, epsilon=1e-6)
    value = sum((b - a) * math.log(b / a) for a, b in zip(p, q))
    return round(value, 6), keys


def compare_column(reference_rows, current_rows, column):
    ref = distribution(reference_rows, column)
    cur = distribution(current_rows, column)
    tv, keys = total_variation(ref, cur)
    js, _ = jensen_shannon(ref, cur)
    psi_value, _ = psi(ref, cur)
    return {
        "column": column,
        "reference_distribution": {key: round(ref.get(key, 0.0), 6) for key in keys},
        "current_distribution": {key: round(cur.get(key, 0.0), 6) for key in keys},
        "total_variation": tv,
        "jensen_shannon": js,
        "psi": psi_value,
        "status": drift_status(tv, js, psi_value),
    }


def drift_status(tv, js, psi_value):
    if tv >= 0.35 or js >= 0.08 or psi_value >= 0.25:
        return "review"
    return "pass"


def build_report(reference_rows, current_rows, columns):
    comparisons = [compare_column(reference_rows, current_rows, column) for column in columns]
    gate = "review" if any(item["status"] == "review" for item in comparisons) else "pass"
    return {
        "reference_rows": len(reference_rows),
        "current_rows": len(current_rows),
        "columns": columns,
        "comparisons": comparisons,
        "gate": gate,
        "recommendation": "revisar distribuciones con drift alto antes de reutilizar la eval" if gate == "review" else "sin drift relevante en columnas revisadas",
    }


def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_markdown(path, report):
    rows = [
        "| Columna | TV | JS | PSI | Estado |",
        "|---|---:|---:|---:|---|",
    ]
    for item in report["comparisons"]:
        rows.append(
            f"| `{item['column']}` | {item['total_variation']} | {item['jensen_shannon']} | {item['psi']} | `{item['status']}` |"
        )
    text = "\n".join(
        [
            "# Decisión de drift",
            "",
            f"Estado: **{report['gate']}**.",
            "",
            "## Comparación",
            "",
            *rows,
            "",
            "## Lectura",
            "",
            report["recommendation"] + ".",
            "",
        ]
    )
    path.write_text(text, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference", type=Path, default=DEFAULT_REFERENCE)
    parser.add_argument("--current", type=Path, default=DEFAULT_CURRENT)
    parser.add_argument("--columns", nargs="+", default=["product", "label", "channel", "pii_risk"])
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    reference_rows = read_csv(args.reference)
    current_rows = read_csv(args.current)
    report = build_report(reference_rows, current_rows, args.columns)
    if args.write:
        write_json(args.output_dir / "drift_report.json", report)
        write_markdown(args.output_dir / "drift_decision.md", report)
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
