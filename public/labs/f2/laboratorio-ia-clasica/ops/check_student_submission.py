#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SUBMISSION = ROOT / "solutions" / "reference"
DEFAULT_OUTPUT = ROOT / "output" / "student_submission_report.md"

REQUIRED = {
    "csp_solution.json": ["solucion_valida", "repaso", "practica", "tutoria"],
    "csp_decision.md": ["practica", "Lab", "martes"],
    "csp_trace.jsonl": ["select_variable", "try_value"],
    "symbolic_plan_report.json": ["conceder_acceso_temporal", "rol_requerido", "aprobacion_del_equipo"],
    "symbolic_plan_decision.md": ["Plan trazable", "precondiciones"],
    "symbolic_plan_trace.jsonl": ["resolver_entidades", "validar_precondicion", "registrar_traza"]
}


def read_text(path):
    return path.read_text(encoding="utf-8") if path.exists() else ""


def missing_terms(text, terms):
    lowered = text.lower()
    return [term for term in terms if term.lower() not in lowered]


def build_report(submission_dir):
    rows = []
    score = 0
    max_score = 0
    for filename, terms in REQUIRED.items():
        max_score += 10
        path = submission_dir / filename
        missing = missing_terms(read_text(path), terms)
        if path.exists() and not missing:
            status = "pass"
            points = 10
        elif path.exists():
            status = "review"
            points = 5
        else:
            status = "missing"
            points = 0
        score += points
        rows.append((filename, status, points, "faltan: " + ", ".join(missing) if missing else "ok"))
    markdown = [
        "# Informe de entrega F2",
        "",
        f"Carpeta revisada: `{submission_dir}`.",
        f"Puntuación: {score}/{max_score}.",
        "",
        "| Archivo | Estado | Puntos | Nota |",
        "|---|---|---:|---|",
    ]
    for filename, status, points, note in rows:
        markdown.append(f"| `{filename}` | `{status}` | {points}/10 | {note} |")
    markdown.append("")
    return {"score": score, "max_score": max_score, "gate_ok": score == max_score, "markdown": "\n".join(markdown)}


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
    print(json.dumps({"score": report["score"], "max_score": report["max_score"], "gate_ok": report["gate_ok"]}, ensure_ascii=False, indent=2))
    if args.fail_on_missing and not report["gate_ok"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
