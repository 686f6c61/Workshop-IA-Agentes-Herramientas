import argparse
import csv
import json
import sys
from pathlib import Path


REQUIRED_FILES = [
    "eval_contract.json",
    "rag_eval_report.json",
    "evaluator_metaeval.json",
    "calibration_manifest.json",
    "interpretability_report.json",
    "explanation_contract.json",
    "ci_explanation_gate.json",
    "model_card_fragment.md",
    "release_eval_report.json",
    "source_evidence_matrix.csv",
    "decision.md",
]


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def add(result, points, max_points, ok, message):
    result["score"] += points if ok else 0
    result["max_score"] += max_points
    result["checks"].append({
        "ok": ok,
        "points": points if ok else 0,
        "max_points": max_points,
        "message": message,
    })


def contains_all(text, terms):
    lower = text.lower()
    return all(term in lower for term in terms)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--submission-dir", default="solutions/reference")
    parser.add_argument("--output", default="output/student_submission_report.md")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--fail-on-missing", action="store_true")
    args = parser.parse_args()

    base = Path(args.submission_dir)
    result = {"score": 0, "max_score": 0, "checks": []}

    missing = [name for name in REQUIRED_FILES if not (base / name).exists()]
    for name in REQUIRED_FILES:
        add(result, 2, 2, (base / name).exists(), f"archivo requerido: {name}")

    if missing:
        gate_ok = False
    else:
        contract = read_json(base / "eval_contract.json")
        rag = read_json(base / "rag_eval_report.json")
        evaluator = read_json(base / "evaluator_metaeval.json")
        calibration = read_json(base / "calibration_manifest.json")
        explanation_contract = read_json(base / "explanation_contract.json")
        explanation_gate = read_json(base / "ci_explanation_gate.json")
        report = read_json(base / "release_eval_report.json")

        must = contract.get("must_pass", {})
        add(result, 6, 6, {"rag_groundedness_min", "evaluator_undue_pass_rate_max", "interpretability_gate"}.issubset(must), "contrato con umbrales críticos")

        rag_metrics = rag.get("metrics", {})
        add(result, 6, 6, {"hit_at_5", "groundedness", "citation_acceptance", "abstention_ok"}.issubset(rag_metrics), "RAG medido por recuperación, evidencia y abstención")

        evaluator_metrics = evaluator.get("metrics", {})
        add(result, 6, 6, {"agreement", "undue_pass_rate", "borderline_overturn_rate", "rubric_coverage"}.issubset(evaluator_metrics), "metaevaluación del evaluador con rúbrica y errores")

        add(result, 6, 6, bool(calibration.get("quality_gate", {}).get("checks")), "manifest de calibración con gate y checks")

        required_fields = set(explanation_contract.get("required_fields", []))
        add(result, 6, 6, {"case_id", "model_version", "score", "prediction", "top_features"}.issubset(required_fields), "contrato de explicación con campos mínimos")

        add(result, 6, 6, explanation_gate.get("gate") in {"pass", "fail"}, "gate de interpretabilidad parseable")

        decision = (base / "decision.md").read_text(encoding="utf-8")
        add(result, 6, 6, contains_all(decision, ["rag", "calibr", "interpret", "release"]) and ("public" in decision.lower() or "bloque" in decision.lower()), "decisión escrita con RAG, calibración, interpretabilidad y acción")

        matrix_rows = list(csv.DictReader((base / "source_evidence_matrix.csv").open(encoding="utf-8")))
        add(result, 4, 4, len(matrix_rows) >= 8 and {"chapter", "artifact", "metric", "status"}.issubset(matrix_rows[0]), "matriz de evidencia por capítulo")

        gate_status = read_json(base / "ci_release_gate.json").get("status") if (base / "ci_release_gate.json").exists() else None
        add(result, 2, 2, gate_status == report.get("status") if gate_status else True, "estado del gate coherente con el reporte")

        gate_ok = result["score"] >= 60 and not any(item.get("status") == "block" for item in report.get("checks", []))

    result["gate_ok"] = gate_ok
    print(json.dumps({"score": result["score"], "max_score": result["max_score"], "gate_ok": gate_ok}, indent=2, ensure_ascii=False))

    if args.write:
        lines = [
            "# Correccion de entrega F7",
            "",
            f"Score: {result['score']} / {result['max_score']}.",
            f"Gate: {'ok' if gate_ok else 'revisar'}.",
            "",
            "| Check | Puntos |",
            "|---|---:|",
        ]
        for check in result["checks"]:
            lines.append(f"| {check['message']} | {check['points']} / {check['max_points']} |")
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text("\n".join(lines) + "\n", encoding="utf-8")

    if args.fail_on_missing and (missing or not gate_ok):
        sys.exit(2)


if __name__ == "__main__":
    main()
