#!/usr/bin/env python3
import argparse
import csv
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TIERS = {"free": 0.0, "standard": 1.0, "enterprise": 2.0}


def load_json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def load_rows():
    with (ROOT / "data/support_tickets.csv").open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def features(row):
    return [
        float(row["hours_since_open"]),
        TIERS[row["customer_tier"]],
        float(row["has_sla"]),
        float(row["prior_incidents"]),
        float(row["urgent_words"])
    ]


def split(rows, every_nth):
    train, test = [], []
    for index, row in enumerate(rows, start=1):
        (test if index % every_nth == 0 else train).append(row)
    return train, test


def standardize(train_x, test_x):
    columns = list(zip(*train_x))
    means = [sum(col) / len(col) for col in columns]
    stds = []
    for col, mean in zip(columns, means):
        variance = sum((value - mean) ** 2 for value in col) / len(col)
        stds.append(math.sqrt(variance) or 1.0)

    def apply(row):
        return [(value - mean) / std for value, mean, std in zip(row, means, stds)]

    return [apply(row) for row in train_x], [apply(row) for row in test_x], means, stds


def sigmoid(value):
    if value < -50:
        return 0.0
    if value > 50:
        return 1.0
    return 1 / (1 + math.exp(-value))


def train_logistic(train_x, train_y, learning_rate, epochs):
    weights = [0.0] * (len(train_x[0]) + 1)
    for _ in range(epochs):
        gradients = [0.0] * len(weights)
        for x, y in zip(train_x, train_y):
            z = weights[0] + sum(w * value for w, value in zip(weights[1:], x))
            pred = sigmoid(z)
            error = pred - y
            gradients[0] += error
            for i, value in enumerate(x, start=1):
                gradients[i] += error * value
        for i in range(len(weights)):
            weights[i] -= learning_rate * gradients[i] / len(train_x)
    return weights


def predict_proba(weights, x):
    return sigmoid(weights[0] + sum(w * value for w, value in zip(weights[1:], x)))


def metrics(y_true, y_pred):
    tp = sum(1 for y, p in zip(y_true, y_pred) if y == 1 and p == 1)
    tn = sum(1 for y, p in zip(y_true, y_pred) if y == 0 and p == 0)
    fp = sum(1 for y, p in zip(y_true, y_pred) if y == 0 and p == 1)
    fn = sum(1 for y, p in zip(y_true, y_pred) if y == 1 and p == 0)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    accuracy = (tp + tn) / len(y_true) if y_true else 0.0
    return {
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "accuracy": round(accuracy, 4)
    }


def run(policy):
    rows = load_rows()
    train_rows, test_rows = split(rows, policy["test_every_nth_row"])
    train_x_raw = [features(row) for row in train_rows]
    test_x_raw = [features(row) for row in test_rows]
    train_y = [int(row["label"]) for row in train_rows]
    test_y = [int(row["label"]) for row in test_rows]
    train_x, test_x, means, stds = standardize(train_x_raw, test_x_raw)
    weights = train_logistic(train_x, train_y, policy["learning_rate"], policy["epochs"])

    probabilities = [predict_proba(weights, row) for row in test_x]
    predictions = [1 if value >= policy["threshold"] else 0 for value in probabilities]
    majority_class = 1 if sum(train_y) >= len(train_y) / 2 else 0
    majority_predictions = [majority_class] * len(test_y)
    model_metrics = metrics(test_y, predictions)
    majority_metrics = metrics(test_y, majority_predictions)
    valid = model_metrics["recall"] >= policy["min_recall"] and model_metrics["f1"] >= policy["min_f1"]
    if policy["require_f1_above_majority"]:
        valid = valid and model_metrics["f1"] > majority_metrics["f1"]

    return {
        "train_rows": len(train_rows),
        "test_rows": len(test_rows),
        "feature_means": [round(v, 4) for v in means],
        "feature_stds": [round(v, 4) for v in stds],
        "weights": [round(v, 4) for v in weights],
        "model_metrics": model_metrics,
        "majority_metrics": majority_metrics,
        "predictions": [
            {
                "id": row["id"],
                "label": int(row["label"]),
                "probability": round(prob, 4),
                "prediction": pred
            }
            for row, prob, pred in zip(test_rows, probabilities, predictions)
        ],
        "valid": valid
    }


def write_markdown(report):
    m = report["model_metrics"]
    b = report["majority_metrics"]
    lines = [
        "# Baseline clásico de tickets",
        "",
        f"Filas de entrenamiento: `{report['train_rows']}`. Filas de test: `{report['test_rows']}`.",
        "",
        "## Métricas",
        "",
        "| Modelo | Accuracy | Precision | Recall | F1 | FP | FN |",
        "|---|---:|---:|---:|---:|---:|---:|",
        f"| Regresión logística | {m['accuracy']} | {m['precision']} | {m['recall']} | {m['f1']} | {m['fp']} | {m['fn']} |",
        f"| Mayoría | {b['accuracy']} | {b['precision']} | {b['recall']} | {b['f1']} | {b['fp']} | {b['fn']} |",
        "",
        "## Decisión",
        "",
    ]
    if report["valid"]:
        lines.append("La regresión logística supera la baseline y cumple el mínimo de recall/F1. El siguiente paso no es meter un LLM: es validar con más datos, separar por tiempo y revisar errores.")
    else:
        lines.append("El modelo no cumple el contrato. Antes de complicar arquitectura, revisa etiquetas, recoge más datos y analiza falsos negativos.")
    lines.extend([
        "",
        "## Predicciones de test",
        "",
        "| Ticket | Real | Probabilidad | Predicción |",
        "|---|---:|---:|---:|"
    ])
    for item in report["predictions"]:
        lines.append(f"| {item['id']} | {item['label']} | {item['probability']} | {item['prediction']} |")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--fail-on-invalid", action="store_true")
    args = parser.parse_args()

    policy = load_json("contracts/ml_classic_policy.json")
    report = run(policy)

    if args.write:
        (ROOT / "output").mkdir(exist_ok=True)
        (ROOT / "output/ml_classic_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        (ROOT / "output/ml_classic_decision.md").write_text(write_markdown(report), encoding="utf-8")

    print(json.dumps(report, indent=2, ensure_ascii=False))
    if args.fail_on_invalid and not report["valid"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

