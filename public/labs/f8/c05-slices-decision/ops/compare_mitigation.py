#!/usr/bin/env python3
import argparse
import csv
import json
from pathlib import Path

import audit_decision_slices as audit


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = ROOT / "data" / "decision_predictions.csv"
DEFAULT_BASELINE = ROOT / "contracts" / "slice_decision_policy.json"
DEFAULT_CANDIDATE = ROOT / "contracts" / "slice_decision_policy_review_band.json"
DEFAULT_OUTPUT = ROOT / "output"


def row_from_report(label, report):
    overall = report["overall"]
    return {
        "policy": label,
        "status": report["release_status"],
        "positive_if_score_gte": report["policy"]["thresholds"]["positive_if_score_gte"],
        "negative_if_score_lt": report["policy"]["thresholds"]["negative_if_score_lt"],
        "n": overall["n"],
        "safety_capture": overall["safety_capture"],
        "miss_rate": overall["miss_rate"],
        "review_rate": overall["review_rate"],
        "automation_rate": overall["automation_rate"],
        "cost_total": overall["cost_total"],
        "cost_per_case": overall["cost_per_case"],
        "block_flags": sum(1 for flag in report["flags"] if flag["severity"] == "block"),
        "review_flags": sum(1 for flag in report["flags"] if flag["severity"] == "review"),
    }


def critical_slice_rows(label, report):
    critical = set(report["policy"]["critical_slices"])
    rows = []
    for metric in report["slice_metrics"]:
        if metric["slice_id"] not in critical:
            continue
        rows.append({
            "policy": label,
            "slice_id": metric["slice_id"],
            "n": metric["n"],
            "positives": metric["positives"],
            "auto_recall": metric["auto_recall"],
            "miss_rate": metric["miss_rate"],
            "safety_capture": metric["safety_capture"],
            "review_rate": metric["review_rate"],
            "cost_per_case": metric["cost_per_case"],
        })
    return rows


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def render_markdown(baseline_row, candidate_row, critical_rows):
    lines = [
        "# Comparación de mitigación por banda de revisión",
        "",
        "Esta comparación no busca ganar una metrica tocando test. Muestra una hipótesis de mitigación: ampliar la banda de revisión para evitar que casos prioritarios inciertos pasen a flujo normal.",
        "",
        "## Resultado global",
        "",
        "| Politica | Estado | Normal si score < | Captura segura | Perdida operativa | Tasa de revisión | Coste por caso | Flags block | Flags review |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in [baseline_row, candidate_row]:
        lines.append(
            f"| {row['policy']} | {row['status']} | {row['negative_if_score_lt']} | {row['safety_capture']} | {row['miss_rate']} | {row['review_rate']} | {row['cost_per_case']} | {row['block_flags']} | {row['review_flags']} |"
        )

    lines.extend([
        "",
        "## Lectura de ingeniería",
        "",
        f"- La política base queda en `{baseline_row['status']}`: captura segura `{baseline_row['safety_capture']}` y perdida operativa `{baseline_row['miss_rate']}`.",
        f"- La política candidata queda en `{candidate_row['status']}`: captura segura `{candidate_row['safety_capture']}` y perdida operativa `{candidate_row['miss_rate']}`.",
        f"- El coste es que la tasa de revisión sube de `{baseline_row['review_rate']}` a `{candidate_row['review_rate']}`.",
        "- Si el equipo no tiene capacidad humana para esa revisión, la mitigación no está lista aunque mejore la captura.",
        "",
        "## Slices críticos",
        "",
        "| Politica | Slice | n | Positivos | Auto-recall | Perdida | Captura segura | Revision | Coste por caso |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for row in critical_rows:
        lines.append(
            f"| {row['policy']} | `{row['slice_id']}` | {row['n']} | {row['positives']} | {row['auto_recall']} | {row['miss_rate']} | {row['safety_capture']} | {row['review_rate']} | {row['cost_per_case']} |"
        )

    lines.extend([
        "",
        "## Decisión",
        "",
        "Esta candidata no se publica automáticamente. Pasa de `block` a `review`, que es justo el aprendizaje: mitigar puede reducir un fallo grave, pero debe revisarse contra capacidad, coste, experiencia de usuario y datos adicionales.",
    ])
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--baseline-policy", type=Path, default=DEFAULT_BASELINE)
    parser.add_argument("--candidate-policy", type=Path, default=DEFAULT_CANDIDATE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    baseline = audit.build_report(args.data.resolve(), args.baseline_policy.resolve())
    candidate = audit.build_report(args.data.resolve(), args.candidate_policy.resolve())

    baseline_row = row_from_report("base", baseline)
    candidate_row = row_from_report("banda_revision", candidate)
    critical_rows = critical_slice_rows("base", baseline) + critical_slice_rows("banda_revision", candidate)
    payload = {
        "summary": [baseline_row, candidate_row],
        "critical_slices": critical_rows,
        "baseline_flags": baseline["flags"],
        "candidate_flags": candidate["flags"],
    }

    if args.write:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        (args.output_dir / "mitigation_before_after.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        write_csv(args.output_dir / "mitigation_before_after.csv", payload["summary"])
        write_csv(args.output_dir / "mitigation_critical_slices.csv", payload["critical_slices"])
        (args.output_dir / "mitigation_before_after.md").write_text(render_markdown(baseline_row, candidate_row, critical_rows), encoding="utf-8")
    else:
        print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
