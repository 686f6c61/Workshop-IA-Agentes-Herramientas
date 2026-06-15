#!/usr/bin/env python3
import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = ROOT / "data" / "observational_campaign.csv"
DEFAULT_OUTPUT = ROOT / "output"


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def as_float(row, field):
    return float(str(row[field]).replace(",", "."))


def mean(values):
    values = list(values)
    return sum(values) / len(values) if values else 0.0


def pct(value):
    return round(value, 6)


def group_by(rows, field):
    result = defaultdict(list)
    for row in rows:
        result[row[field]].append(row)
    return dict(result)


def effect(rows):
    treated = [as_float(row, "resolved") for row in rows if row["received_action"] == "1"]
    control = [as_float(row, "resolved") for row in rows if row["received_action"] == "0"]
    return {
        "treated_n": len(treated),
        "control_n": len(control),
        "treated_mean": pct(mean(treated)),
        "control_mean": pct(mean(control)),
        "effect": pct(mean(treated) - mean(control)) if treated and control else None,
        "estimable": bool(treated and control),
    }


def stratified_effect(rows, field):
    total = len(rows)
    strata = []
    weighted = 0.0
    estimable_weight = 0.0
    for value, subset in sorted(group_by(rows, field).items()):
        item = effect(subset)
        item["stratum"] = value
        item["weight"] = pct(len(subset) / total)
        if item["estimable"]:
            weighted += item["effect"] * (len(subset) / total)
            estimable_weight += len(subset) / total
        strata.append(item)
    return {
        "field": field,
        "strata": strata,
        "weighted_effect_over_estimable_population": pct(weighted),
        "estimable_population_weight": pct(estimable_weight),
        "status": "review" if estimable_weight < 0.95 else "pass",
    }


def build_report(rows):
    naive = effect(rows)
    by_priority = stratified_effect(rows, "prior_priority")
    by_segment = stratified_effect(rows, "segment")
    reasons = []
    if by_priority["status"] == "review":
        reasons.append("falta solapamiento en alguna prioridad: hay niveles donde solo vemos acción o solo vemos control")
    if naive["effect"] is not None and by_priority["weighted_effect_over_estimable_population"] is not None:
        gap = naive["effect"] - by_priority["weighted_effect_over_estimable_population"]
        if abs(gap) > 0.2:
            reasons.append("el efecto ingenuo cambia mucho al estratificar; hay señal de confusion por contexto")
    return {
        "status": "review" if reasons else "pass",
        "naive_effect": naive,
        "adjusted_by_priority": by_priority,
        "adjusted_by_segment": by_segment,
        "reasons": reasons,
        "decision": "usar como triage, no como conclusion causal final",
    }


def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def flatten_strata(report):
    rows = []
    for block in [report["adjusted_by_priority"], report["adjusted_by_segment"]]:
        for item in block["strata"]:
            row = dict(item)
            row["field"] = block["field"]
            rows.append(row)
    return rows


def render_decision(report):
    lines = [
        "# Triage causal observacional",
        "",
        f"Estado: **{report['status']}**.",
        "",
        "## Lectura principal",
        "",
        f"Efecto ingenuo: `{report['naive_effect']['effect']}`.",
        f"Efecto estratificado por prioridad en poblacion estimable: `{report['adjusted_by_priority']['weighted_effect_over_estimable_population']}`.",
        f"Peso de poblacion estimable por prioridad: `{report['adjusted_by_priority']['estimable_population_weight']}`.",
        "",
        "## Por que no basta",
        "",
    ]
    for reason in report["reasons"]:
        lines.append(f"- {reason}.")
    lines.extend([
        "",
        "## Decisión",
        "",
        "La muestra observacional sirve para formular una hipótesis y diseñar mejor el experimento. No permite publicar la acción como si el efecto estuviera demostrado.",
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
        args.output_dir.mkdir(parents=True, exist_ok=True)
        write_json(args.output_dir / "observational_causal_report.json", report)
        write_csv(args.output_dir / "observational_strata.csv", flatten_strata(report))
        (args.output_dir / "observational_decision.md").write_text(render_decision(report), encoding="utf-8")
    else:
        print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
