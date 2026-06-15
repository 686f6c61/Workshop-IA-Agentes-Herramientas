#!/usr/bin/env python3
import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET = ROOT / "data" / "support_split_cases.csv"
DEFAULT_PREDICTIONS = ROOT / "data" / "model_predictions.csv"
DEFAULT_MANIFEST = ROOT / "output" / "split_manifest.json"
DEFAULT_OUTPUT = ROOT / "output"


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def read_json(path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def accuracy(rows):
    if not rows:
        return None
    correct = sum(1 for row in rows if row["label"] == row["predicted_label"])
    return correct / len(rows)


def normal_ci_95(proportion, count):
    if count == 0 or proportion is None:
        return None
    se = math.sqrt((proportion * (1 - proportion)) / count)
    low = max(0.0, proportion - 1.96 * se)
    high = min(1.0, proportion + 1.96 * se)
    return {
        "low": round(low, 4),
        "high": round(high, 4),
        "standard_error": round(se, 4),
    }


def merge_test_rows(dataset, predictions, manifest):
    test_ids = set(manifest["assignments_by_split"]["test"])
    predictions_by_id = {row["case_id"]: row for row in predictions}
    rows = []
    missing_predictions = []

    for row in dataset:
        if row["case_id"] not in test_ids:
            continue
        prediction = predictions_by_id.get(row["case_id"])
        if not prediction:
            missing_predictions.append(row["case_id"])
            continue
        rows.append(
            {
                **row,
                "predicted_label": prediction["predicted_label"],
                "confidence": float(prediction["confidence"]),
                "latency_ms": int(prediction["latency_ms"]),
                "correct": row["label"] == prediction["predicted_label"],
            }
        )
    return rows, sorted(missing_predictions)


def slice_metrics(rows, field):
    grouped = defaultdict(list)
    for row in rows:
        grouped[row[field]].append(row)
    result = {}
    for value, items in sorted(grouped.items()):
        score = accuracy(items)
        result[value] = {
            "n": len(items),
            "accuracy": round(score, 4) if score is not None else None,
            "correct": sum(1 for item in items if item["correct"]),
            "needs_more_evidence": len(items) < 30,
        }
    return result


def build_report(dataset, predictions, manifest):
    rows, missing_predictions = merge_test_rows(dataset, predictions, manifest)
    score = accuracy(rows)
    failures = [
        {
            "case_id": row["case_id"],
            "product": row["product"],
            "channel": row["channel"],
            "expected": row["label"],
            "predicted": row["predicted_label"],
            "confidence": row["confidence"],
        }
        for row in rows
        if not row["correct"]
    ]
    latency_values = [row["latency_ms"] for row in rows]

    return {
        "manifest_policy_id": manifest["policy_id"],
        "selected_strategy": manifest["split_contract"]["selected_strategy"],
        "split": "test",
        "n": len(rows),
        "missing_predictions": missing_predictions,
        "accuracy": round(score, 4) if score is not None else None,
        "accuracy_ci_95_normal_approx": normal_ci_95(score, len(rows)),
        "latency_ms": {
            "avg": round(sum(latency_values) / len(latency_values), 2) if latency_values else None,
            "max": max(latency_values) if latency_values else None,
        },
        "slices": {
            "product": slice_metrics(rows, "product"),
            "channel": slice_metrics(rows, "channel"),
            "label": slice_metrics(rows, "label"),
        },
        "failures": failures,
        "decision": decision(rows, missing_predictions, failures),
    }


def decision(rows, missing_predictions, failures):
    if missing_predictions:
        return "block_missing_predictions"
    if len(rows) < 30:
        return "review_test_too_small"
    if failures:
        return "review_failures"
    return "pass"


def write_decision(path, report):
    lines = [
        "# Decisión de evaluación por slices",
        "",
        f"Split evaluado: `{report['split']}`.",
        f"Estrategia de split: `{report['selected_strategy']}`.",
        f"Decisión: `{report['decision']}`.",
        "",
        "## Métrica global",
        "",
        f"- n: {report['n']}",
        f"- accuracy: {report['accuracy']}",
        f"- intervalo aproximado 95%: {report['accuracy_ci_95_normal_approx']}",
        f"- latencia media: {report['latency_ms']['avg']} ms",
        "",
        "## Fallos",
        "",
    ]
    if report["failures"]:
        lines.extend(
            f"- `{item['case_id']}`: esperado `{item['expected']}`, predicho `{item['predicted']}`, producto `{item['product']}`."
            for item in report["failures"]
        )
    else:
        lines.append("No se registraron fallos en test.")

    lines.extend(
        [
            "",
            "## Lectura",
            "",
            "Esta evaluación es útil como ejercicio operativo, pero el test es pequeño. No cierres una afirmacion publica con está muestra: aumenta el holdout o repite la medición con más casos versionados.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--predictions", type=Path, default=DEFAULT_PREDICTIONS)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    dataset = read_csv(args.dataset)
    predictions = read_csv(args.predictions)
    manifest = read_json(args.manifest)
    report = build_report(dataset, predictions, manifest)
    if args.write:
        write_json(args.output_dir / "evaluation_slice_report.json", report)
        write_decision(args.output_dir / "evaluation_slice_decision.md", report)
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
