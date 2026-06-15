#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SUBMISSION = ROOT / "solutions" / "reference"
DEFAULT_OUTPUT = ROOT / "output" / "student_submission_report.md"

REQUIRED_FILES = {
    "decision_memo.md": ["revisar_antes", "recordkeeping_export", "owner-platform"],
    "diff_notes.md": ["publicar_con_condiciones", "recordkeeping_export"],
    "residual_risk_acceptance.md": ["riesgo residual", "owner"],
    "next_gate_date.md": ["python3 ops/run_governance_lab.py", "governance_findings_student.csv"],
    "ci_gate.json": ["decision", "blocker_count"],
}

OPTIONAL_EVIDENCE = {
    "agent_identity_policy.yaml": ["agent_id", "credential_ttl_minutes"],
    "tool_boundary_contract.yaml": ["prepare", "execute"],
    "memory_retention_policy.md": ["TTL", "purga"],
    "recordkeeping_contract.json": ["required_fields", "agent_id"],
}


def read_text(path):
    return path.read_text(encoding="utf-8") if path.exists() else ""


def check_contains(text, needles):
    lowered = text.lower()
    return [needle for needle in needles if needle.lower() not in lowered]


def check_json(path):
    try:
        return json.loads(read_text(path)), None
    except json.JSONDecodeError as exc:
        return None, str(exc)


def build_report(submission_dir):
    rows = []
    score = 0
    max_score = 0

    for filename, needles in REQUIRED_FILES.items():
        max_score += 10
        path = submission_dir / filename
        missing_terms = check_contains(read_text(path), needles)
        if path.exists() and not missing_terms:
            status = "pass"
            points = 10
        elif path.exists():
            status = "review"
            points = 5
        else:
            status = "missing"
            points = 0
        score += points
        rows.append({
            "file": filename,
            "status": status,
            "points": points,
            "max_points": 10,
            "note": "faltan: " + ", ".join(missing_terms) if missing_terms else "ok",
        })

    for filename, needles in OPTIONAL_EVIDENCE.items():
        max_score += 5
        path = submission_dir / filename
        missing_terms = check_contains(read_text(path), needles)
        if path.exists() and not missing_terms:
            status = "pass"
            points = 5
        elif path.exists():
            status = "review"
            points = 2
        else:
            status = "missing"
            points = 0
        score += points
        rows.append({
            "file": filename,
            "status": status,
            "points": points,
            "max_points": 5,
            "note": "faltan: " + ", ".join(missing_terms) if missing_terms else "ok",
        })

    ci_path = submission_dir / "ci_gate.json"
    ci_payload, ci_error = check_json(ci_path) if ci_path.exists() else (None, "no existe")
    ci_ok = bool(
        isinstance(ci_payload, dict)
        and ci_payload.get("decision") in {"publicar_con_condiciones", "publicar_con_seguimiento"}
        and int(ci_payload.get("blocker_count", 999)) == 0
    )

    lines = [
        "# Informe de entrega del laboratorio",
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
    if ci_ok:
        lines.append("- `ci_gate.json` es valido y no conserva bloqueos.")
    else:
        lines.append(f"- Revisar `ci_gate.json`: {ci_error or ci_payload}.")
    lines.extend([
        "",
        "## Criterio",
        "",
        "Una entrega util no intenta marcar todo como `pass`. Debe explicar que se cerro, que sigue condicionado, quien es owner, que evidencia se compara y cuando se repite el gate.",
        "",
    ])

    return {
        "score": score,
        "max_score": max_score,
        "ci_ok": ci_ok,
        "rows": rows,
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
        "ci_ok": report["ci_ok"],
        "wrote_output": args.write,
    }, ensure_ascii=False, indent=2))

    if args.fail_on_missing and (report["score"] < report["max_score"] or not report["ci_ok"]):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
