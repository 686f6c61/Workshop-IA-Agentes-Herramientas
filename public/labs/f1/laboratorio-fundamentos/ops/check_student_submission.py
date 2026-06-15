#!/usr/bin/env python3
import argparse
import json
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SUBMISSION = ROOT / "solutions" / "reference"
DEFAULT_OUTPUT = ROOT / "output" / "student_submission_report.md"

REQUIRED = {
    "classifier_metrics.json": ["selected_model", "modelo_b", "priority_queue"],
    "classifier_decision.md": ["Modelo elegido", "capacidad diaria", "precision"],
    "semantic_search_report.json": ["hit_at_1", "mrr", "trace_complete_rate"],
    "semantic_search_decision.md": ["Hit@1", "MRR", "trazas"],
    "semantic_search_traces.jsonl": ["tokenize_query", "score_documents", "rank"]
}


def read_text(path):
    return path.read_text(encoding="utf-8") if path.exists() else ""


def normalize(text):
    text = unicodedata.normalize("NFD", text.lower())
    return "".join(ch for ch in text if unicodedata.category(ch) != "Mn")


def missing_terms(text, terms):
    lowered = normalize(text)
    return [term for term in terms if normalize(term) not in lowered]


def json_ok(path):
    try:
        json.loads(read_text(path))
        return True
    except json.JSONDecodeError:
        return False


def build_report(submission_dir):
    rows = []
    score = 0
    max_score = 0
    for filename, terms in REQUIRED.items():
        max_score += 10
        path = submission_dir / filename
        missing = missing_terms(read_text(path), terms)
        valid_json = True
        if filename.endswith(".json"):
            valid_json = path.exists() and json_ok(path)
        if path.exists() and not missing and valid_json:
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
        "# Informe de entrega F1",
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
