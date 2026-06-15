#!/usr/bin/env python3
import argparse
import csv
from collections import defaultdict
from pathlib import Path

from audit_reward_card import DEFAULT_SPEC, read_json, score_candidate


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "output" / "threshold_calibration.csv"
DEFAULT_RECOMMENDATION = ROOT / "output" / "threshold_recommendation.md"


def parse_thresholds(raw):
    if raw:
        return [float(value.strip()) for value in raw.split(",") if value.strip()]
    return [round(value / 100, 2) for value in range(40, 91, 5)]


def candidate_rows(spec):
    rows = []
    terms = spec["reward_terms"]
    for case in spec["test_cases"]:
        for candidate in case["candidates"]:
            score, _ = score_candidate(candidate, terms)
            rows.append({
                "case_id": case["case_id"],
                "slice": case["slice"],
                "candidate_id": candidate["candidate_id"],
                "score": score,
                "label": candidate["candidate_id"] == case["expected_winner"],
            })
    return rows


def metrics_for(rows, threshold):
    total = len(rows)
    predicted_pass = [row for row in rows if row["score"] >= threshold]
    true_pass = [row for row in rows if row["label"]]
    false_passes = [
        row for row in rows
        if row["score"] >= threshold and not row["label"]
    ]
    false_blocks = [
        row for row in rows
        if row["score"] < threshold and row["label"]
    ]
    true_passes = [
        row for row in rows
        if row["score"] >= threshold and row["label"]
    ]

    precision = len(true_passes) / len(predicted_pass) if predicted_pass else 0.0
    recall = len(true_passes) / len(true_pass) if true_pass else 0.0
    pass_rate = len(predicted_pass) / total if total else 0.0
    error_count = len(false_passes) + len(false_blocks)

    return {
        "threshold": threshold,
        "cases": total,
        "pass_rate": round(pass_rate, 6),
        "precision": round(precision, 6),
        "recall": round(recall, 6),
        "false_passes": len(false_passes),
        "false_blocks": len(false_blocks),
        "error_count": error_count,
        "false_pass_case_ids": ";".join(sorted({row["case_id"] for row in false_passes})),
        "false_block_case_ids": ";".join(sorted({row["case_id"] for row in false_blocks})),
    }


def calibration_rows(spec, thresholds):
    rows = []
    all_candidates = candidate_rows(spec)
    by_slice = defaultdict(list)
    for row in all_candidates:
        by_slice[row["slice"]].append(row)

    groups = {"all": all_candidates, **dict(sorted(by_slice.items()))}
    for group_name, group_rows in groups.items():
        for threshold in thresholds:
            metrics = metrics_for(group_rows, threshold)
            rows.append({"slice": group_name, **metrics})
    return rows


def recommendations(rows):
    by_slice = defaultdict(list)
    for row in rows:
        by_slice[row["slice"]].append(row)

    chosen = []
    for slice_name, slice_rows in sorted(by_slice.items()):
        ranked = sorted(
            slice_rows,
            key=lambda row: (
                row["false_passes"],
                row["error_count"],
                -row["recall"],
                abs(row["threshold"] - 0.7),
            ),
        )
        chosen.append(ranked[0])
    return chosen


def render_recommendation(chosen):
    lines = [
        "# Threshold calibration",
        "",
        "Esta recomendacion prioriza reducir falsos pases. Si tu dominio prefiere no bloquear respuestas utiles, cambia el criterio y vuelve a ejecutar el script.",
        "",
        "| Slice | Threshold | Precision | Recall | Falsos pases | Falsos bloqueos | Casos a revisar |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in chosen:
        review = ";".join(
            value for value in [
                row["false_pass_case_ids"],
                row["false_block_case_ids"],
            ]
            if value
        )
        lines.append(
            f"| `{row['slice']}` | {row['threshold']} | {row['precision']} | "
            f"{row['recall']} | {row['false_passes']} | {row['false_blocks']} | "
            f"{review or 'none'} |"
        )
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", default=str(DEFAULT_SPEC))
    parser.add_argument("--thresholds", default="")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--recommendation", default=str(DEFAULT_RECOMMENDATION))
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    spec = read_json(Path(args.spec))
    thresholds = parse_thresholds(args.thresholds)
    rows = calibration_rows(spec, thresholds)
    chosen = recommendations(rows)

    if args.write:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        Path(args.recommendation).write_text(
            render_recommendation(chosen),
            encoding="utf-8",
        )

    print(f"rows={len(rows)}")
    for row in chosen:
        print(
            f"slice={row['slice']} threshold={row['threshold']} "
            f"false_passes={row['false_passes']} false_blocks={row['false_blocks']}"
        )


if __name__ == "__main__":
    main()
