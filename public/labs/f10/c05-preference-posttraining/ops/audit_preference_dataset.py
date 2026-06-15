#!/usr/bin/env python3
import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PAIRS = ROOT / "data" / "preference_pairs.jsonl"
DEFAULT_CONTRACT = ROOT / "contracts" / "preference_dataset_contract.json"
DEFAULT_OUTPUT = ROOT / "output"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path):
    rows = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if line.strip():
            row = json.loads(line)
            row["_line"] = line_number
            rows.append(row)
    return rows


def normalize(text):
    return re.sub(r"\s+", " ", str(text).strip().lower())


def validate_rows(rows, contract):
    errors = []
    required = contract["required_fields"]
    required_rubric = contract["required_rubric_keys"]
    seen_ids = set()
    for row in rows:
        row_id = row.get("pair_id", f"line_{row.get('_line')}")
        if row_id in seen_ids:
            errors.append(f"{row_id} pair_id duplicado")
        seen_ids.add(row_id)
        for field in required:
            if field not in row:
                errors.append(f"{row_id} falta {field}")
        rubric = row.get("rubric_scores", {})
        for key in required_rubric:
            if key not in rubric:
                errors.append(f"{row_id} falta rubric_scores.{key}")
        agreement = row.get("agreement")
        if agreement is not None and not (0 <= float(agreement) <= 1):
            errors.append(f"{row_id} agreement fuera de [0,1]")
        for score_field in ("chosen_reward_score", "rejected_reward_score"):
            if score_field in row and not (0 <= float(row[score_field]) <= 1):
                errors.append(f"{row_id} {score_field} fuera de [0,1]")
        verifier = row.get("verifier_result", {})
        if verifier.get("available") and verifier.get("score") is None:
            errors.append(f"{row_id} verifier disponible sin score")
    return errors


def pair_key(row):
    return (
        normalize(row.get("prompt", "")),
        normalize(row.get("chosen", "")),
        normalize(row.get("rejected", "")),
    )


def reversed_key(row):
    return (
        normalize(row.get("prompt", "")),
        normalize(row.get("rejected", "")),
        normalize(row.get("chosen", "")),
    )


def safe_average(values):
    return sum(values) / len(values) if values else 0.0


def task_family_summary(rows):
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["task_family"]].append(row)
    summary = []
    for family, items in sorted(grouped.items()):
        margins = [float(row["chosen_reward_score"]) - float(row["rejected_reward_score"]) for row in items]
        agreements = [float(row["agreement"]) for row in items]
        summary.append({
            "task_family": family,
            "pairs": len(items),
            "avg_margin": round(safe_average(margins), 6),
            "avg_agreement": round(safe_average(agreements), 6),
            "verifier_coverage": round(
                sum(1 for row in items if row["verifier_result"].get("available")) / len(items),
                6,
            ),
        })
    return summary


def evaluate(rows, contract):
    validation_errors = validate_rows(rows, contract)
    if validation_errors:
        return {
            "scenario_id": contract["scenario_id"],
            "contract_version": contract["contract_version"],
            "status": "block",
            "validation_errors": validation_errors,
            "checks": {"schema": False},
        }, []

    margins = [float(row["chosen_reward_score"]) - float(row["rejected_reward_score"]) for row in rows]
    agreements = [float(row["agreement"]) for row in rows]
    verifier_available = [bool(row["verifier_result"].get("available")) for row in rows]
    low_agreement_threshold = float(contract["low_agreement_threshold"])
    duplicate_counts = Counter(pair_key(row) for row in rows)
    duplicate_pairs = sum(count - 1 for count in duplicate_counts.values() if count > 1)
    all_keys = set(duplicate_counts)
    reversed_conflicts = sum(1 for row in rows if reversed_key(row) in all_keys) // 2
    avg_chosen_tokens = safe_average([float(row["chosen_tokens"]) for row in rows])
    avg_rejected_tokens = safe_average([float(row["rejected_tokens"]) for row in rows])
    length_bias_ratio = max(
        avg_chosen_tokens / avg_rejected_tokens if avg_rejected_tokens else 0,
        avg_rejected_tokens / avg_chosen_tokens if avg_chosen_tokens else 0,
    )

    diagnostics = {
        "pairs": len(rows),
        "task_families": len(set(row["task_family"] for row in rows)),
        "avg_agreement": round(safe_average(agreements), 6),
        "low_agreement_rate": round(sum(1 for value in agreements if value < low_agreement_threshold) / len(rows), 6),
        "chosen_win_rate": round(sum(1 for margin in margins if margin > 0) / len(rows), 6),
        "avg_reward_margin": round(safe_average(margins), 6),
        "negative_margin_rate": round(sum(1 for margin in margins if margin <= 0) / len(rows), 6),
        "verifier_coverage": round(sum(1 for value in verifier_available if value) / len(rows), 6),
        "duplicate_pair_rate": round(duplicate_pairs / len(rows), 6),
        "reversed_conflicts": reversed_conflicts,
        "length_bias_ratio": round(length_bias_ratio, 6),
    }

    checks = {
        "schema": True,
        "min_pairs": diagnostics["pairs"] >= contract["min_pairs"],
        "min_task_families": diagnostics["task_families"] >= contract["min_task_families"],
        "min_avg_agreement": diagnostics["avg_agreement"] >= contract["min_avg_agreement"],
        "max_low_agreement_rate": diagnostics["low_agreement_rate"] <= contract["max_low_agreement_rate"],
        "min_chosen_win_rate": diagnostics["chosen_win_rate"] >= contract["min_chosen_win_rate"],
        "min_avg_reward_margin": diagnostics["avg_reward_margin"] >= contract["min_avg_reward_margin"],
        "max_negative_margin_rate": diagnostics["negative_margin_rate"] <= contract["max_negative_margin_rate"],
        "min_verifier_coverage": diagnostics["verifier_coverage"] >= contract["min_verifier_coverage"],
        "max_duplicate_pair_rate": diagnostics["duplicate_pair_rate"] <= contract["max_duplicate_pair_rate"],
        "max_reversed_conflicts": diagnostics["reversed_conflicts"] <= contract["max_reversed_conflicts"],
        "max_length_bias_ratio": diagnostics["length_bias_ratio"] <= contract["max_length_bias_ratio"],
    }

    pair_scorecard = []
    for row, margin in zip(rows, margins):
        pair_scorecard.append({
            "pair_id": row["pair_id"],
            "prompt_id": row["prompt_id"],
            "task_family": row["task_family"],
            "agreement": round(float(row["agreement"]), 6),
            "reward_margin": round(margin, 6),
            "chosen_wins": margin > 0,
            "verifier_available": bool(row["verifier_result"].get("available")),
            "verifier_score": row["verifier_result"].get("score"),
            "chosen_tokens": row["chosen_tokens"],
            "rejected_tokens": row["rejected_tokens"],
        })

    status = "pass" if all(checks.values()) else "block"
    report = {
        "scenario_id": contract["scenario_id"],
        "contract_version": contract["contract_version"],
        "dataset_snapshot_id": contract["dataset_snapshot_id"],
        "target_use": contract["target_use"],
        "status": status,
        "diagnostics": diagnostics,
        "checks": checks,
        "task_family_summary": task_family_summary(rows),
    }
    return report, pair_scorecard


def render_decision(report):
    lines = [
        "# Decision del dataset de preferencias",
        "",
        f"Estado: `{report['status']}`",
        f"Snapshot: `{report.get('dataset_snapshot_id', 'desconocido')}`",
        f"Uso previsto: `{report.get('target_use', 'desconocido')}`",
        "",
    ]
    if report.get("validation_errors"):
        lines.extend(["## Errores de validación", ""])
        for error in report["validation_errors"]:
            lines.append(f"- {error}")
        lines.append("")
        return "\n".join(lines)

    lines.extend([
        "## Diagnósticos",
        "",
        "| Métrica | Valor |",
        "|---|---:|",
    ])
    for key, value in report["diagnostics"].items():
        lines.append(f"| `{key}` | {value} |")
    lines.extend([
        "",
        "## Checks",
        "",
        "| Check | Pasa |",
        "|---|---|",
    ])
    for key, value in report["checks"].items():
        lines.append(f"| `{key}` | {'si' if value else 'no'} |")
    lines.extend([
        "",
        "## Lectura tecnica",
        "",
    ])
    if report["status"] == "pass":
        lines.append("El dataset pasa el contrato mínimo para experimentar con DPO o reward modeling en un entorno controlado. No significa que el modelo ajustado sea publicable; significa que el dato deja suficiente evidencia para entrenar y evaluar sin empezar a ciegas.")
    else:
        lines.append("El dataset debe bloquearse antes de entrenar. Revisa pares con margen negativo, bajo acuerdo, duplicados, contradicciones, cobertura de verificador y sesgo de longitud antes de gastar GPU.")
    return "\n".join(lines) + "\n"


def render_reward_card(report):
    lines = [
        "# Reward card / preference card",
        "",
        f"Snapshot: `{report.get('dataset_snapshot_id', 'desconocido')}`",
        f"Estado: `{report['status']}`",
        "",
    ]
    if "diagnostics" not in report:
        lines.append("El dataset no cumple el contrato de campos, asi que no hay tarjeta defendible.")
        return "\n".join(lines) + "\n"

    diagnostics = report["diagnostics"]
    lines.extend([
        "## Senal",
        "",
        "Pares de preferencia `prompt/chosen/rejected` con razon de preferencia, rubric scores, acuerdo y verificador cuando existe.",
        "",
        "## Cobertura",
        "",
        f"- Pares: {diagnostics['pairs']}",
        f"- Familias de tarea: {diagnostics['task_families']}",
        f"- Cobertura de verificador: {diagnostics['verifier_coverage']}",
        f"- Acuerdo medio: {diagnostics['avg_agreement']}",
        f"- Margen medio chosen-rejected: {diagnostics['avg_reward_margin']}",
        "",
        "## Riesgos conocidos",
        "",
        "- La recompensa es una aproximacion de preferencia, no una prueba de verdad.",
        "- Los pares sin verificador requieren revision humana retenida.",
        "- Si cambia la rubrica, este snapshot debe auditarse de nuevo.",
        "- El entrenamiento posterior debe compararse contra prompt baseline y SFT.",
        "",
        "## Decision",
        "",
    ])
    if report["status"] == "pass":
        lines.append("Puede pasar a experimento controlado con eval retenida y revision de samples.")
    else:
        lines.append("No debe pasar a entrenamiento hasta corregir los checks fallidos.")
    return "\n".join(lines) + "\n"


def write_outputs(output_dir, report, scorecard):
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "preference_dataset_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (output_dir / "preference_dataset_decision.md").write_text(render_decision(report), encoding="utf-8")
    (output_dir / "reward_card.md").write_text(render_reward_card(report), encoding="utf-8")
    if scorecard:
        with (output_dir / "pair_scorecard.csv").open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(scorecard[0].keys()))
            writer.writeheader()
            writer.writerows(scorecard)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pairs", default=str(DEFAULT_PAIRS))
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    rows = read_jsonl(Path(args.pairs))
    contract = read_json(Path(args.contract))
    report, scorecard = evaluate(rows, contract)
    if args.write:
        write_outputs(Path(args.output), report, scorecard)
    print(f"status={report['status']}")
    print(f"pairs={report.get('diagnostics', {}).get('pairs', len(rows))}")
    if "diagnostics" in report:
        print(f"chosen_win_rate={report['diagnostics']['chosen_win_rate']}")
        print(f"avg_reward_margin={report['diagnostics']['avg_reward_margin']}")


if __name__ == "__main__":
    main()
