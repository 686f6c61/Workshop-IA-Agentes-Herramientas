#!/usr/bin/env python3
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def metrics(rows, threshold, policy):
    tp = fp = tn = fn = 0
    for row in rows:
        pred = 1 if row["score"] >= threshold else 0
        label = row["label"]
        tp += pred == 1 and label == 1
        fp += pred == 1 and label == 0
        tn += pred == 0 and label == 0
        fn += pred == 0 and label == 1
    recall = tp / max(1, tp + fn)
    precision = tp / max(1, tp + fp)
    cost = fp * policy["cost_false_positive"] + fn * policy["cost_false_negative"]
    return {"threshold": threshold, "tp": tp, "fp": fp, "tn": tn, "fn": fn, "precision": round(precision, 4), "recall": round(recall, 4), "cost": cost}


def main():
    rows = read_jsonl(ROOT / "evals/classification_cases.jsonl")
    policy = json.loads((ROOT / "ops/ai/threshold_policy.json").read_text(encoding="utf-8"))
    candidates = [metrics(rows, t, policy) for t in policy["threshold_grid"]]
    viable = [item for item in candidates if item["recall"] >= policy["min_operational_recall"]]
    best = min(viable, key=lambda item: item["cost"]) if viable else None
    report = {"candidates": candidates, "selected": best, "decision": "use_threshold" if best else "manual_review"}
    (ROOT / "output/threshold_scorecard.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (ROOT / "output/threshold_decision.md").write_text(f"# Decisión de umbral\n\nEstado: `{report['decision']}`.\n\nUmbral seleccionado: `{best['threshold'] if best else 'n/a'}`.\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
