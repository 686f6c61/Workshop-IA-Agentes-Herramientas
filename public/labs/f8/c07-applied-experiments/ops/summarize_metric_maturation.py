#!/usr/bin/env python3
import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = ROOT / "data" / "late_metric_events.csv"
DEFAULT_OUTPUT = ROOT / "output"


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def as_float(row, field):
    return float(str(row[field]).replace(",", "."))


def mean(values):
    values = list(values)
    return sum(values) / len(values) if values else 0.0


def group_by(rows, *fields):
    result = defaultdict(list)
    for row in rows:
        key = tuple(row[field] for field in fields)
        result[key].append(row)
    return dict(result)


def pct(value):
    return round(value, 6)


def summarize(rows):
    metrics = ["resolved", "followup_needed", "student_satisfied"]
    output = []
    for (window, variant), subset in sorted(group_by(rows, "metric_window", "variant").items()):
        item = {
            "metric_window": window,
            "variant": variant,
            "n": len(subset),
        }
        for metric in metrics:
            item[f"{metric}_rate"] = pct(mean(as_float(row, metric) for row in subset))
        output.append(item)
    return output


def deltas(summary):
    by_window = defaultdict(dict)
    for row in summary:
        by_window[row["metric_window"]][row["variant"]] = row
    rows = []
    for window, variants in sorted(by_window.items()):
        if "control" not in variants or "treatment" not in variants:
            continue
        for metric in ["resolved_rate", "followup_needed_rate", "student_satisfied_rate"]:
            rows.append({
                "metric_window": window,
                "metric": metric,
                "control": variants["control"][metric],
                "treatment": variants["treatment"][metric],
                "delta": pct(variants["treatment"][metric] - variants["control"][metric]),
            })
    return rows


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


def render(delta_rows):
    lines = [
        "# Maduración de métricas",
        "",
        "## Deltas por ventana",
        "",
        "| Ventana | Métrica | Control | Treatment | Delta |",
        "|---|---|---:|---:|---:|",
    ]
    for row in delta_rows:
        lines.append(f"| `{row['metric_window']}` | `{row['metric']}` | `{row['control']}` | `{row['treatment']}` | `{row['delta']}` |")
    lines.extend([
        "",
        "## Lectura",
        "",
        "Una metrica temprana puede contar una historia incompleta. En este ejemplo, satisfaction mejora claramente en day_7 porque algunos casos que parecian incomodos en day_1 se estabilizan después.",
    ])
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    rows = read_csv(args.data)
    summary = summarize(rows)
    delta_rows = deltas(summary)
    payload = {"status": "review", "summary": summary, "deltas": delta_rows}
    if args.write:
        write_json(args.output_dir / "metric_maturation_report.json", payload)
        write_csv(args.output_dir / "metric_maturation_summary.csv", summary)
        write_csv(args.output_dir / "metric_maturation_deltas.csv", delta_rows)
        (args.output_dir / "metric_maturation_decision.md").write_text(render(delta_rows), encoding="utf-8")
    else:
        print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
