#!/usr/bin/env python3
import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = ROOT / "data" / "cluster_interference_events.csv"
DEFAULT_OUTPUT = ROOT / "output"


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def as_float(row, field):
    return float(str(row[field]).replace(",", "."))


def mean(values):
    values = list(values)
    return sum(values) / len(values) if values else 0.0


def group_by(rows, field):
    result = defaultdict(list)
    for row in rows:
        result[row[field]].append(row)
    return dict(result)


def pct(value):
    return round(value, 6)


def build_report(rows):
    cluster_rows = []
    mixed_clusters = []
    for cluster_id, subset in sorted(group_by(rows, "cluster_id").items()):
        variants = sorted({row["variant"] for row in subset})
        resolved_by_variant = {
            variant: pct(mean(as_float(row, "resolved") for row in subset if row["variant"] == variant))
            for variant in variants
        }
        item = {
            "cluster_id": cluster_id,
            "n": len(subset),
            "variants": ",".join(variants),
            "mixed": len(variants) > 1,
            "resolved_control": resolved_by_variant.get("control", ""),
            "resolved_treatment": resolved_by_variant.get("treatment", ""),
            "spillover_events": sum(1 for row in subset if row["spillover_note"] != "none"),
        }
        cluster_rows.append(item)
        if item["mixed"] and item["spillover_events"]:
            mixed_clusters.append(cluster_id)
    status = "review" if mixed_clusters else "pass"
    return {
        "status": status,
        "mixed_clusters_with_spillover": mixed_clusters,
        "cluster_summary": cluster_rows,
        "decision": "si hay aprendizaje compartido por operador o equipo, considera asignar por cluster_id",
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
        "# Interferencia por cluster",
        "",
        f"Estado: **{report['status']}**.",
        "",
        "## Lectura",
        "",
        "Hay clusters donde control y tratamiento conviven y aparece aprendizaje compartido. Si el operador cambia su forma de trabajar por ver la variante, control deja de ser control limpio dentro de ese equipo.",
        "",
        "## Decisión",
        "",
        report["decision"] + ".",
    ]
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    report = build_report(read_csv(args.data))
    if args.write:
        write_json(args.output_dir / "cluster_interference_report.json", report)
        write_csv(args.output_dir / "cluster_interference_summary.csv", report["cluster_summary"])
        (args.output_dir / "cluster_interference_decision.md").write_text(render(report), encoding="utf-8")
    else:
        print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
