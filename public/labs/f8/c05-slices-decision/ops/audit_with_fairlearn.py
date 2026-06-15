#!/usr/bin/env python3
import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = ROOT / "data" / "decision_predictions.csv"
DEFAULT_POLICY = ROOT / "contracts" / "slice_decision_policy.json"
DEFAULT_OUTPUT = ROOT / "output" / "fairlearn_metricframe.json"


def ensure_optional_dependencies():
    try:
        import pandas as pd
        from fairlearn.metrics import MetricFrame, false_positive_rate, selection_rate, true_positive_rate
    except ModuleNotFoundError as error:
        return None, error.name
    return pd, MetricFrame, false_positive_rate, selection_rate, true_positive_rate


def load_policy(path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def decide(score, policy):
    labels = policy["decision_labels"]
    if score >= policy["thresholds"]["positive_if_score_gte"]:
        return labels["positive"]
    if score < policy["thresholds"]["negative_if_score_lt"]:
        return labels["negative"]
    return labels["review"]


def miss_rate(y_true, y_pred):
    positives = sum(1 for value in y_true if int(value) == 1)
    if positives == 0:
        return 0.0
    misses = sum(1 for truth, pred in zip(y_true, y_pred) if int(truth) == 1 and int(pred) == 0)
    return misses / positives


def to_plain(value):
    if hasattr(value, "to_dict"):
        return value.to_dict()
    if hasattr(value, "item"):
        return value.item()
    return value


def rate(numerator, denominator):
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 6)


def summarize_rows(rows):
    total = len(rows)
    positives = sum(1 for row in rows if int(row["label"]) == 1)
    negatives = total - positives
    auto_positive = sum(1 for row in rows if row["auto_positive"] == 1)
    true_auto_positive = sum(1 for row in rows if int(row["label"]) == 1 and row["auto_positive"] == 1)
    false_auto_positive = sum(1 for row in rows if int(row["label"]) == 0 and row["auto_positive"] == 1)
    safe_positive = sum(1 for row in rows if int(row["label"]) == 1 and row["safe_capture"] == 1)
    missed = sum(1 for row in rows if int(row["label"]) == 1 and row["auto_positive"] == 0)
    return {
        "n": total,
        "positives": positives,
        "auto_recall": rate(true_auto_positive, positives),
        "false_positive_rate": rate(false_auto_positive, negatives),
        "priority_selection_rate": rate(auto_positive, total),
        "miss_rate": rate(missed, positives),
        "safe_capture": rate(safe_positive, positives),
    }


def difference_between_groups(group_metrics):
    metric_names = ("auto_recall", "false_positive_rate", "priority_selection_rate", "miss_rate", "safe_capture")
    differences = {}
    for metric in metric_names:
        values = [payload[metric] for payload in group_metrics.values()]
        differences[metric] = round(max(values) - min(values), 6) if values else 0.0
    return differences


def fallback_metricframe(args, missing_dependency):
    policy = load_policy(args.policy)
    with args.data.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = []
        for row in reader:
            if row["split"] != policy["evaluation_split"]:
                continue
            decision = decide(float(row[policy["score_field"]]), policy)
            rows.append(
                {
                    args.field: row[args.field],
                    "label": row[policy["label_field"]],
                    "decision": decision,
                    "auto_positive": 1 if decision == policy["decision_labels"]["positive"] else 0,
                    "safe_capture": 0 if decision == policy["decision_labels"]["negative"] else 1,
                }
            )

    groups = {}
    for row in rows:
        groups.setdefault(row[args.field], []).append(row)
    by_group = {group: summarize_rows(group_rows) for group, group_rows in sorted(groups.items())}

    payload = {
        "status": "generated_with_standard_library_fallback",
        "missing_optional_dependency": missing_dependency,
        "install_for_real_fairlearn_metricframe": [
            "python3 -m venv .venv",
            "source .venv/bin/activate",
            "python3 -m pip install pandas fairlearn",
            "python3 ops/audit_with_fairlearn.py --field access_need --write",
        ],
        "field": args.field,
        "policy": args.policy.name,
        "meaning": {
            "auto_recall": "Recall si solo cuenta la decisión automatica de priorizar.",
            "safe_capture": "Recall si cuentan priorizar y revisar, porque ambas evitan flujo normal.",
            "miss_rate": "Casos prioritarios enviados a flujo normal.",
            "priority_selection_rate": "Proporcion de casos priorizados automáticamente.",
        },
        "overall": summarize_rows(rows),
        "by_group": by_group,
        "difference": difference_between_groups(by_group),
        "why_fallback_is_kept": "El kit base debe ejecutarse sin dependencias externas. Este fallback permite aprender la lectura por grupos; Fairlearn aporta el MetricFrame profesional cuando está instalado.",
    }
    if args.write:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    else:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    return payload


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    parser.add_argument("--field", default="access_need")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    dependencies, missing_dependency = ensure_optional_dependencies()
    if dependencies is None:
        fallback_metricframe(args, missing_dependency)
        return

    pd, MetricFrame, false_positive_rate, selection_rate, true_positive_rate = dependencies
    policy = load_policy(args.policy)
    df = pd.read_csv(args.data)
    df = df[df["split"] == policy["evaluation_split"]].copy()
    df["decision"] = df[policy["score_field"]].apply(lambda score: decide(float(score), policy))
    df["auto_positive"] = (df["decision"] == policy["decision_labels"]["positive"]).astype(int)
    df["safe_capture"] = (df["decision"] != policy["decision_labels"]["negative"]).astype(int)

    y_true = df[policy["label_field"]].astype(int)
    by_field_auto = MetricFrame(
        metrics={
            "auto_recall": true_positive_rate,
            "false_positive_rate": false_positive_rate,
            "priority_selection_rate": selection_rate,
            "miss_rate": miss_rate,
        },
        y_true=y_true,
        y_pred=df["auto_positive"],
        sensitive_features=df[args.field],
    )
    by_field_safe = MetricFrame(
        metrics={"safe_capture": true_positive_rate},
        y_true=y_true,
        y_pred=df["safe_capture"],
        sensitive_features=df[args.field],
    )

    payload = {
        "field": args.field,
        "policy": args.policy.name,
        "meaning": {
            "auto_recall": "Recall si solo cuenta la decisión automatica de priorizar.",
            "safe_capture": "Recall si cuentan priorizar y revisar, porque ambas evitan flujo normal.",
            "miss_rate": "Casos prioritarios enviados a flujo normal.",
            "priority_selection_rate": "Proporcion de casos priorizados automáticamente.",
        },
        "overall": {
            "auto": to_plain(by_field_auto.overall),
            "safe": to_plain(by_field_safe.overall),
        },
        "by_group": {
            "auto": to_plain(by_field_auto.by_group),
            "safe": to_plain(by_field_safe.by_group),
        },
        "difference": {
            "auto": to_plain(by_field_auto.difference(method="between_groups")),
            "safe": to_plain(by_field_safe.difference(method="between_groups")),
        },
    }

    if args.write:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    else:
        print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
