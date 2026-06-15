#!/usr/bin/env python3
import argparse
import json
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SUBMISSION = ROOT / "solutions" / "reference"
DEFAULT_OUTPUT = ROOT / "output" / "student_submission_report.md"

REQUIRED = {
    "bandit_policy_report.json": ["selected_policy", "regret", "action_share"],
    "bandit_policy_decision.md": ["Política seleccionada", "regret", "rollback"],
    "bandit_trace.jsonl": ["policy_id", "action", "reward"],
    "reward_audit_report.json": ["pass_rate", "reward_terms", "case_ok"],
    "reward_card.md": ["Reward card", "abstención", "No hay bonus por longitud"],
    "ci_reward_gate.json": ["publicar_reward_spec", "pass_rate", "gate_ok"],
    "ope_decision.md": ["Decisión OPE", "doubly_robust", "modo sombra"],
    "ope_quality_card.md": ["OPE quality card", "ESS", "soporte"],
    "serving_decision.md": ["Decisión de serving", "drift|population_stability_index|psi", "rollout"],
    "serving_runbook.md": ["Serving runbook", "rollback", "politica de reserva"]
}


def read_text(path):
    return path.read_text(encoding="utf-8") if path.exists() else ""


def normalize(text):
    decomposed = unicodedata.normalize("NFD", text.lower())
    return "".join(char for char in decomposed if unicodedata.category(char) != "Mn")


def missing_terms(text, terms):
    normalized_text = normalize(text)
    missing = []
    for term in terms:
        alternatives = [normalize(part.strip()) for part in term.split("|")]
        if not any(alternative in normalized_text for alternative in alternatives):
            missing.append(term)
    return missing


def json_valid(path):
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
        valid = True
        if filename.endswith(".json"):
            valid = path.exists() and json_valid(path)
        if path.exists() and not missing and valid:
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
    lines = [
        "# Informe de entrega F10",
        "",
        f"Carpeta revisada: `{submission_dir}`.",
        f"Puntuacion: {score}/{max_score}.",
        "",
        "| Archivo | Estado | Puntos | Nota |",
        "|---|---|---:|---|",
    ]
    for filename, status, points, note in rows:
        lines.append(f"| `{filename}` | `{status}` | {points}/10 | {note} |")
    lines.append("")
    return {"score": score, "max_score": max_score, "gate_ok": score == max_score, "markdown": "\n".join(lines)}


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
