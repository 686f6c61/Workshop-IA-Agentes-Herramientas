#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SUBMISSION = ROOT / "solutions" / "reference"
DEFAULT_OUTPUT = ROOT / "output" / "student_submission_report.md"

REQUIRED_FILES = {
    "decision_memo.md": ["block", "missing_trace_rate", "missing_required_fields_rate"],
    "correction_plan.md": ["trace_id", "has_required_fields", "final_review_contract.json"],
    "next_experiment_plan.md": ["case_id", "resolved_day_7", "exposure"],
    "residual_data_risk.md": ["riesgo residual", "missing_trace_rate", "owner"],
    "data_release_ci_gate.json": ["status", "block_count", "review_count"],
}

OPTIONAL_EVIDENCE = {
    "traceability_policy.md": ["trace_id", "missing_trace_rate"],
    "data_quality_contract.json": ["required_columns", "blocking_rules"],
    "slice_remediation_plan.md": ["language=en", "segment=practicas"],
    "experiment_exposure_contract.json": ["case_id", "required_exposure_fields"],
}


def read_text(path):
    return path.read_text(encoding="utf-8") if path.exists() else ""


def missing_terms(text, needles):
    lowered = text.lower()
    return [needle for needle in needles if needle.lower() not in lowered]


def read_json(path):
    try:
        return json.loads(read_text(path)), None
    except json.JSONDecodeError as exc:
        return None, str(exc)


def check_group(submission_dir, spec, points_each):
    rows = []
    score = 0
    max_score = 0
    for filename, needles in spec.items():
        max_score += points_each
        path = submission_dir / filename
        missing = missing_terms(read_text(path), needles)
        if path.exists() and not missing:
            status = "pass"
            points = points_each
        elif path.exists():
            status = "review"
            points = max(1, points_each // 2)
        else:
            status = "missing"
            points = 0
        score += points
        rows.append({
            "file": filename,
            "status": status,
            "points": points,
            "max_points": points_each,
            "note": "faltan: " + ", ".join(missing) if missing else "ok",
        })
    return score, max_score, rows


def build_report(submission_dir):
    score_a, max_a, rows_a = check_group(submission_dir, REQUIRED_FILES, 10)
    score_b, max_b, rows_b = check_group(submission_dir, OPTIONAL_EVIDENCE, 5)
    score = score_a + score_b
    max_score = max_a + max_b
    rows = rows_a + rows_b

    gate_path = submission_dir / "data_release_ci_gate.json"
    gate, gate_error = read_json(gate_path) if gate_path.exists() else (None, "no existe")
    gate_ok = bool(
        isinstance(gate, dict)
        and gate.get("status") in {"review", "pass"}
        and int(gate.get("block_count", 999)) == 0
    )

    lines = [
        "# Informe de entrega del laboratorio F8",
        "",
        f"Carpeta revisada: `{submission_dir}`.",
        f"Puntuación: {score}/{max_score}.",
        "",
        "| Archivo | Estado | Puntos | Nota |",
        "|---|---|---:|---|",
    ]
    for row in rows:
        lines.append(
            f"| `{row['file']}` | `{row['status']}` | {row['points']}/{row['max_points']} | {row['note']} |"
        )
    lines.extend([
        "",
        "## Gate CI",
        "",
    ])
    if gate_ok:
        lines.append("- `data_release_ci_gate.json` es valido y no conserva bloqueos.")
    else:
        lines.append(f"- Revisar `data_release_ci_gate.json`: {gate_error or gate}.")
    lines.extend([
        "",
        "## Criterio",
        "",
        "Una entrega buena no relaja umbrales después de mirar el resultado. Corrige trazabilidad, ingesta o slices, repite el gate y deja un plan experimental conectado con el fallo detectado.",
        "",
    ])
    return {
        "score": score,
        "max_score": max_score,
        "gate_ok": gate_ok,
        "markdown": "\n".join(lines),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--submission-dir", type=Path, default=DEFAULT_SUBMISSION)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--fail-on-missing", action="store_true")
    args = parser.parse_args()

    report = build_report(args.submission_dir)
    if args.write:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report["markdown"], encoding="utf-8")

    print(json.dumps({
        "score": report["score"],
        "max_score": report["max_score"],
        "gate_ok": report["gate_ok"],
        "wrote_output": args.write,
    }, ensure_ascii=False, indent=2))

    if args.fail_on_missing and (report["score"] < report["max_score"] or not report["gate_ok"]):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
