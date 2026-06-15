#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = [
    "product_release_decision.md",
    "metric_tree.md",
    "unit_economics.csv",
    "nota_de_decision.md",
    "ux_contract.md",
    "ux_decision.md",
    "ux_release_gate.json",
    "final_product_packet.md",
]
REQUIRED_TERMS = [
    "piloto",
    "metrica",
    "coste",
    "evidencia",
    "recuperacion",
    "privacidad",
    "rollback",
    "baseline",
    "guardrail",
    "slice",
    "sensibilidad",
    "parada",
    "responsable",
]


def normalize(text):
    return (
        text.lower()
        .replace("é", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("á", "a")
        .replace("ú", "u")
    )


def check(submission_dir):
    submission_dir = Path(submission_dir)
    missing_files = [name for name in REQUIRED_FILES if not (submission_dir / name).exists()]
    combined = ""
    for name in REQUIRED_FILES:
        path = submission_dir / name
        if path.exists() and path.suffix in {".md", ".csv", ".json"}:
            combined += "\n" + path.read_text(encoding="utf-8")

    normalized = normalize(combined)
    missing_terms = [term for term in REQUIRED_TERMS if term not in normalized]

    json_errors = []
    gate_path = submission_dir / "ux_release_gate.json"
    if gate_path.exists():
        try:
            json.loads(gate_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            json_errors.append(f"ux_release_gate.json no es JSON válido: {error}")

    max_score = 10 * len(REQUIRED_FILES)
    score = max_score
    score -= 7 * len(missing_files)
    score -= 4 * len(missing_terms)
    score -= 8 * len(json_errors)
    score = max(score, 0)

    return {
        "submission_dir": str(submission_dir),
        "score": score,
        "max_score": max_score,
        "gate_ok": score >= int(max_score * 0.83) and not missing_files and not json_errors,
        "missing_files": missing_files,
        "missing_terms": missing_terms,
        "json_errors": json_errors,
    }


def write_report(result, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "student_submission_report.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    missing_files = [f"- {item}" for item in result["missing_files"]] if result["missing_files"] else ["- Ninguno."]
    missing_terms = [f"- {item}" for item in result["missing_terms"]] if result["missing_terms"] else ["- Ninguno."]
    json_errors = [f"- {item}" for item in result["json_errors"]] if result["json_errors"] else ["- Ninguno."]
    lines = [
        "# Revisión de entrega F11",
        "",
        f"Score: {result['score']} / {result['max_score']}.",
        "",
        f"Gate: {'pass' if result['gate_ok'] else 'review'}.",
        "",
        "## Archivos faltantes",
        "",
        *missing_files,
        "",
        "## Términos ausentes",
        "",
        *missing_terms,
        "",
        "## Errores JSON",
        "",
        *json_errors,
    ]
    (output_dir / "student_submission_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--submission-dir", required=True)
    parser.add_argument("--output-dir", default=ROOT / "output")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--fail-on-missing", action="store_true")
    args = parser.parse_args()

    result = check(args.submission_dir)
    if args.write:
        write_report(result, Path(args.output_dir))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if args.fail_on_missing and not result["gate_ok"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
