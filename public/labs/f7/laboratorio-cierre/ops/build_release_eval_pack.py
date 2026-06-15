import argparse
import csv
import json
import shutil
import sys
from pathlib import Path


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, payload):
    Path(path).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def metric(payload, name):
    return payload.get("metrics", {}).get(name)


def add_check(checks, source, chapter, artifact, name, observed, required, passes, severity, note):
    checks.append({
        "source": source,
        "chapter": chapter,
        "artifact": artifact,
        "metric": name,
        "observed": observed,
        "required": required,
        "status": "pass" if passes else severity,
        "note": note,
    })


def check_min(checks, source, chapter, artifact, name, observed, required, severity="block"):
    add_check(
        checks,
        source,
        chapter,
        artifact,
        name,
        observed,
        f">= {required}",
        observed is not None and observed >= required,
        severity,
        "valor por debajo del umbral" if observed is not None and observed < required else "ok",
    )


def check_max(checks, source, chapter, artifact, name, observed, required, severity="block"):
    add_check(
        checks,
        source,
        chapter,
        artifact,
        name,
        observed,
        f"<= {required}",
        observed is not None and observed <= required,
        severity,
        "valor por encima del umbral" if observed is not None and observed > required else "ok",
    )


def write_matrix(path, checks):
    with Path(path).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["source", "chapter", "artifact", "metric", "observed", "required", "status", "note"],
        )
        writer.writeheader()
        writer.writerows(checks)


def copy_artifact(source, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)


def render_decision(report):
    status = report["status"]
    lines = [
        "# Decisión de release evaluada",
        "",
        f"Estado: **{status}**.",
        "",
        "## Lectura técnica",
        "",
        "Esta decisión no sale de una sola métrica. Cruza RAG, metaevaluación del evaluador, calibración e interpretabilidad.",
        "El paquete sirve para decidir si la release puede publicarse, publicarse con condiciones o bloquearse hasta corregir evidencia.",
        "",
        "## Resumen de checks",
        "",
        f"- checks correctos: {report['summary']['pass_count']}",
        f"- checks en revisión: {report['summary']['review_count']}",
        f"- checks bloqueantes: {report['summary']['block_count']}",
        "",
        "## Hallazgos",
        "",
    ]
    for item in report["checks"]:
        if item["status"] == "pass":
            continue
        lines.append(
            f"- `{item['artifact']}` / `{item['metric']}` queda en `{item['status']}`: "
            f"observado `{item['observed']}`, requerido `{item['required']}`."
        )
    if all(item["status"] == "pass" for item in report["checks"]):
        lines.append("- No hay checks fuera de umbral.")

    lines.extend([
        "",
        "## Decisión profesional",
        "",
    ])
    if status == "bloquear":
        lines.append("No publicaría la release. Corregiría primero los checks bloqueantes y repetiría el paquete completo.")
    elif status == "publicar_con_condiciones":
        lines.append("Publicaría solo con condiciones: canary pequeño, monitorización reforzada y revisión de los puntos marcados.")
    else:
        lines.append("Publicaría la release con vigilancia normal y conservaría el paquete como evidencia de decisión.")

    lines.extend([
        "",
        "## Acciones siguientes",
        "",
        "1. Convertir todo check bloqueante en tarea con owner y fecha.",
        "2. Mantener los hashes de datos y política junto a la release.",
        "3. Repetir calibración si cambian modelo, prompt, retrieval o mezcla de casos.",
        "4. Revisar el contrato de explicación antes de ampliar consumidores.",
    ])
    return "\n".join(lines) + "\n"


def build_report(contract, rag, evaluator, calibration_manifest, interpretation_report, explanation_contract, explanation_gate):
    must = contract["must_pass"]
    review = contract["review_triggers"]
    checks = []

    check_min(checks, "rag_eval", "07.03", "rag_eval_report.json", "hit_at_5", metric(rag, "hit_at_5"), must["rag_hit_at_5_min"])
    check_min(checks, "rag_eval", "07.03", "rag_eval_report.json", "groundedness", metric(rag, "groundedness"), must["rag_groundedness_min"])
    check_min(checks, "rag_eval", "07.03", "rag_eval_report.json", "citation_acceptance", metric(rag, "citation_acceptance"), must["rag_citation_acceptance_min"])
    check_min(checks, "rag_eval", "07.03", "rag_eval_report.json", "abstention_ok", metric(rag, "abstention_ok"), must["rag_abstention_ok_min"])
    check_min(checks, "rag_eval", "07.03", "rag_eval_report.json", "long_tail_coverage", metric(rag, "long_tail_coverage"), review["rag_long_tail_coverage_under"], "review")

    check_min(checks, "evaluator_metaeval", "07.04", "evaluator_metaeval.json", "agreement", metric(evaluator, "agreement"), must["evaluator_agreement_min"])
    check_max(checks, "evaluator_metaeval", "07.04", "evaluator_metaeval.json", "undue_pass_rate", metric(evaluator, "undue_pass_rate"), must["evaluator_undue_pass_rate_max"])
    check_max(checks, "evaluator_metaeval", "07.04", "evaluator_metaeval.json", "borderline_overturn_rate", metric(evaluator, "borderline_overturn_rate"), review["evaluator_borderline_overturn_rate_over"], "review")

    quality_gate = calibration_manifest.get("quality_gate", {}).get("passes")
    add_check(
        checks,
        "calibration",
        "07.05",
        "calibration_manifest.json",
        "quality_gate.passes",
        quality_gate,
        must["calibration_gate_required"],
        quality_gate is must["calibration_gate_required"],
        "block",
        "ok" if quality_gate else "la política calibrada no pasa gate",
    )
    recommended = calibration_manifest.get("recommended_policy", {})
    check_max(checks, "calibration", "07.05", "calibration_manifest.json", "auto_error_rate", recommended.get("auto_error_rate"), must["calibration_auto_error_rate_max"])
    check_max(checks, "calibration", "07.05", "calibration_manifest.json", "review_rate", recommended.get("review_rate"), must["calibration_review_rate_max"])
    wilson = recommended.get("auto_error_wilson_95") or [None, None]
    check_max(checks, "calibration", "07.05", "calibration_manifest.json", "auto_error_wilson_upper", wilson[1], review["calibration_auto_error_wilson_upper_over"], "review")

    gate = explanation_gate.get("gate")
    add_check(
        checks,
        "interpretability",
        "07.06",
        "ci_explanation_gate.json",
        "gate",
        gate,
        must["interpretability_gate"],
        gate == must["interpretability_gate"],
        "block",
        "ok" if gate == must["interpretability_gate"] else "el gate de explicación no pasa",
    )
    top_share = max((item.get("share", 0) for item in explanation_gate.get("top_feature_distribution", [])), default=0)
    check_max(checks, "interpretability", "07.06", "ci_explanation_gate.json", "top_feature_share", top_share, review["top_feature_share_over"], "review")

    required_fields = set(explanation_contract.get("required_fields", []))
    required_min = {"case_id", "model_version", "score", "prediction", "top_features", "data_hash_sha256", "policy_hash_sha256"}
    add_check(
        checks,
        "interpretability",
        "07.06",
        "explanation_contract.json",
        "required_fields",
        sorted(required_fields),
        sorted(required_min),
        required_min.issubset(required_fields),
        "block",
        "ok" if required_min.issubset(required_fields) else "faltan campos mínimos",
    )

    block_count = sum(item["status"] == "block" for item in checks)
    review_count = sum(item["status"] == "review" for item in checks)
    pass_count = sum(item["status"] == "pass" for item in checks)
    status = "bloquear" if block_count else "publicar_con_condiciones" if review_count else "publicar"

    return {
        "contract_id": contract["contract_id"],
        "contract_version": contract["contract_version"],
        "release_id": contract["release_id"],
        "status": status,
        "summary": {
            "pass_count": pass_count,
            "review_count": review_count,
            "block_count": block_count,
        },
        "checks": checks,
        "interpretability_accuracy": interpretation_report.get("accuracy"),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", default="contracts/release_eval_contract.json")
    parser.add_argument("--rag-report", default="evidence/rag_eval_report.json")
    parser.add_argument("--evaluator-report", default="evidence/evaluator_metaeval.json")
    parser.add_argument("--calibration-manifest", default="evidence/calibration_manifest.json")
    parser.add_argument("--calibration-report", default="evidence/calibration_report.json")
    parser.add_argument("--interpretability-report", default="evidence/interpretability_report.json")
    parser.add_argument("--explanation-contract", default="evidence/explanation_contract.json")
    parser.add_argument("--explanation-gate", default="evidence/ci_explanation_gate.json")
    parser.add_argument("--model-card", default="evidence/model_card_interpretability.md")
    parser.add_argument("--output-dir", default="output")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--fail-on-blocker", action="store_true")
    args = parser.parse_args()

    contract = read_json(args.contract)
    rag = read_json(args.rag_report)
    evaluator = read_json(args.evaluator_report)
    calibration_manifest = read_json(args.calibration_manifest)
    calibration_report = read_json(args.calibration_report)
    interpretation_report = read_json(args.interpretability_report)
    explanation_contract = read_json(args.explanation_contract)
    explanation_gate = read_json(args.explanation_gate)

    report = build_report(
        contract,
        rag,
        evaluator,
        calibration_manifest,
        interpretation_report,
        explanation_contract,
        explanation_gate,
    )
    print(json.dumps(report, indent=2, ensure_ascii=False))

    if args.write:
        out = Path(args.output_dir)
        out.mkdir(parents=True, exist_ok=True)
        write_json(out / "eval_contract.json", contract)
        write_json(out / "rag_eval_report.json", rag)
        write_json(out / "evaluator_metaeval.json", evaluator)
        write_json(out / "calibration_manifest.json", calibration_manifest)
        write_json(out / "calibration_report.json", calibration_report)
        write_json(out / "interpretability_report.json", interpretation_report)
        write_json(out / "explanation_contract.json", explanation_contract)
        write_json(out / "ci_explanation_gate.json", explanation_gate)
        copy_artifact(Path(args.model_card), out / "model_card_fragment.md")
        write_json(out / "release_eval_report.json", report)
        write_json(out / "ci_release_gate.json", {
            "status": report["status"],
            "block_count": report["summary"]["block_count"],
            "review_count": report["summary"]["review_count"],
            "release_id": report["release_id"],
        })
        write_matrix(out / "source_evidence_matrix.csv", report["checks"])
        (out / "decision.md").write_text(render_decision(report), encoding="utf-8")
        write_json(out / "release_eval_package_manifest.json", {
            "release_id": report["release_id"],
            "status": report["status"],
            "artifacts": contract["required_artifacts"] + ["ci_release_gate.json", "release_eval_package_manifest.json"],
        })

    if args.fail_on_blocker and report["summary"]["block_count"]:
        sys.exit(2)


if __name__ == "__main__":
    main()
