#!/usr/bin/env python3
import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = ROOT / "data" / "rag_experiment_events.csv"
DEFAULT_OUTPUT = ROOT / "output"


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def as_float(row, field):
    return float(str(row[field]).replace(",", "."))


def mean(values):
    values = list(values)
    return sum(values) / len(values) if values else 0.0


def variance(values):
    values = list(values)
    if len(values) < 2:
        return 0.0
    m = mean(values)
    return sum((v - m) ** 2 for v in values) / (len(values) - 1)


def pct(value):
    return round(value, 6)


def group_by(rows, field):
    result = defaultdict(list)
    for row in rows:
        result[row[field]].append(row)
    return dict(result)


def effect(rows, metric):
    groups = group_by(rows, "variant")
    control = [as_float(row, metric) for row in groups.get("control", [])]
    treatment = [as_float(row, metric) for row in groups.get("treatment", [])]
    diff = mean(treatment) - mean(control)
    se = math.sqrt((variance(treatment) / len(treatment)) + (variance(control) / len(control))) if treatment and control else 0
    return {
        "metric": metric,
        "control_mean": pct(mean(control)),
        "treatment_mean": pct(mean(treatment)),
        "delta": pct(diff),
        "standard_error": pct(se),
        "ci95_low": pct(diff - 1.96 * se),
        "ci95_high": pct(diff + 1.96 * se),
    }


def build_report(rows):
    metrics = [
        effect(rows, "answer_accepted"),
        effect(rows, "citation_valid"),
        effect(rows, "retrieval_precision"),
        effect(rows, "latency_ms"),
        effect(rows, "cost_eur"),
    ]
    slices = []
    for query_type, subset in sorted(group_by(rows, "query_type").items()):
        item = effect(subset, "answer_accepted")
        item["query_type"] = query_type
        item["n"] = len(subset)
        slices.append(item)
    status = "review"
    reasons = [
        "el reranker mejora aceptacion y precision, pero aumenta coste y latencia",
        "la metrica citation_valid no mejora de forma perfecta y debe ser guardrail",
        "hay pocos ejemplos por tipo de consulta",
    ]
    return {
        "status": status,
        "metrics": metrics,
        "slice_effects": slices,
        "reasons": reasons,
    }


def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def render(report):
    lines = [
        "# Decisión experimento RAG",
        "",
        f"Estado: **{report['status']}**.",
        "",
        "| Métrica | Control | Treatment | Delta |",
        "|---|---:|---:|---:|",
    ]
    for item in report["metrics"]:
        lines.append(f"| `{item['metric']}` | `{item['control_mean']}` | `{item['treatment_mean']}` | `{item['delta']}` |")
    lines.extend(["", "## Motivos", ""])
    for reason in report["reasons"]:
        lines.append(f"- {reason}.")
    lines.extend([
        "",
        "## Decisión",
        "",
        "No se publica globalmente. Se amplia muestra y se mantiene citation_valid como guardrail antes de probar rollout.",
    ])
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    rows = read_csv(args.data)
    report = build_report(rows)
    if args.write:
        write_json(args.output_dir / "rag_experiment_report.json", report)
        write_csv(args.output_dir / "rag_metric_effects.csv", report["metrics"])
        write_csv(args.output_dir / "rag_slice_effects.csv", report["slice_effects"])
        (args.output_dir / "rag_experiment_decision.md").write_text(render(report), encoding="utf-8")
    else:
        print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
