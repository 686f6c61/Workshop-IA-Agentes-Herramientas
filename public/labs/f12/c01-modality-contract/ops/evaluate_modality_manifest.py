#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_json(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def modality_set(case):
    return sorted({entry["modality"] for entry in case.get("available_inputs", [])})


def recommended_architecture(modalities, policy):
    if "action" in modalities or "screen" in modalities:
        return "computer_use_or_tool_agent_with_policy"
    if "video" in modalities:
        return "video_sampling_plus_temporal_evaluation"
    if "audio" in modalities:
        return "asr_plus_llm_with_timestamps"
    if "document" in modalities:
        return "ocr_layout_plus_llm_or_multimodal_rag"
    if "image" in modalities and "text" in modalities:
        return "vlm_or_multimodal_embedding_retrieval"
    if modalities == ["text"]:
        return policy["architecture_hints"]["text"]
    return "hybrid_pipeline_with_explicit_contract"


def risk_score(risks, policy):
    total = 0
    reasons = []
    for risk in risks:
        lower = risk.lower()
        matched = False
        for token, weight in policy["risk_weights"].items():
            if token in lower:
                total += weight
                reasons.append({"risk": risk, "token": token, "weight": weight})
                matched = True
                break
        if not matched:
            total += 1
            reasons.append({"risk": risk, "token": "default", "weight": 1})
    return total, reasons


def modality_tax(modalities, risk_total):
    tax = {
        "complexity": len(modalities),
        "latency": 1,
        "privacy": risk_total,
        "evaluation": 1 + max(len(modalities) - 1, 0),
    }
    if "audio" in modalities:
        tax["latency"] += 2
        tax["evaluation"] += 1
    if "video" in modalities:
        tax["latency"] += 3
        tax["evaluation"] += 2
    if "document" in modalities:
        tax["latency"] += 1
        tax["evaluation"] += 1
    if "image" in modalities:
        tax["latency"] += 1
        tax["evaluation"] += 1
    if "action" in modalities or "screen" in modalities:
        tax["privacy"] += 2
        tax["evaluation"] += 2
    return tax


def validate_case(case, policy):
    issues = []
    for field in policy["required_case_fields"]:
        if field not in case:
            issues.append(f"missing_field:{field}")
    modalities = modality_set(case)
    unknown = [item for item in modalities if item not in policy["allowed_modalities"]]
    if unknown:
        issues.append(f"unknown_modalities:{','.join(unknown)}")
    if not case.get("evidence_required"):
        issues.append("missing_evidence_required")
    if len(case.get("metrics", [])) < policy["gates"]["min_metrics_per_case"]:
        issues.append("too_few_metrics")
    if len(case.get("risks", [])) < policy["gates"]["min_risks_per_case"]:
        issues.append("too_few_risks")
    required_fields = case.get("output_contract", {}).get("required_fields", [])
    if not required_fields:
        issues.append("missing_output_required_fields")
    if not str(case.get("human_review", "")).strip():
        issues.append("missing_human_review_rule")
    return issues


def evaluate_manifest(manifest, policy):
    cases = manifest.get("cases", [])
    report_cases = []
    global_issues = []
    if len(cases) < policy["gates"]["min_cases"]:
        global_issues.append("too_few_cases")

    for case in cases:
        modalities = modality_set(case)
        issues = validate_case(case, policy)
        risk_total, risk_reasons = risk_score(case.get("risks", []), policy)
        recommended = recommended_architecture(modalities, policy)
        output_fields = case.get("output_contract", {}).get("required_fields", [])
        report_cases.append(
            {
                "case_id": case.get("case_id"),
                "title": case.get("title"),
                "modalities": modalities,
                "minimum_modalities": case.get("minimum_modalities", []),
                "candidate_architecture": case.get("candidate_architecture"),
                "recommended_architecture": recommended,
                "architecture_match": case.get("candidate_architecture") in recommended
                or recommended in case.get("candidate_architecture", ""),
                "output_required_fields": output_fields,
                "evidence_required": case.get("evidence_required", []),
                "metrics": case.get("metrics", []),
                "risk_score": risk_total,
                "risk_reasons": risk_reasons,
                "modality_tax": modality_tax(modalities, risk_total),
                "human_review": case.get("human_review"),
                "issues": issues,
            }
        )

    invalid_cases = [case["case_id"] for case in report_cases if case["issues"]]
    high_risk_cases = [case["case_id"] for case in report_cases if case["risk_score"] >= 6]
    return {
        "manifest_id": manifest.get("manifest_id"),
        "owner": manifest.get("owner"),
        "goal": manifest.get("goal"),
        "case_count": len(cases),
        "valid": not global_issues and not invalid_cases,
        "global_issues": global_issues,
        "invalid_cases": invalid_cases,
        "high_risk_cases": high_risk_cases,
        "cases": report_cases,
        "engineering_decision": {
            "default_rule": "usar la modalidad minima que aporte evidencia nueva medible",
            "do_not_do": "no convertir una tarea textual en multimodal solo porque el proveedor acepte imagenes o audio",
            "measure_before_shipping": [
                "schema_pass_rate",
                "evidence_coverage",
                "cost_per_valid_answer",
                "latency_p95",
                "manual_review_rate",
            ],
        },
    }


def markdown(report):
    lines = [
        f"# Reporte de contrato multimodal: {report['manifest_id']}",
        "",
        f"Owner: `{report['owner']}`",
        f"Casos revisados: {report['case_count']}",
        f"Gate valido: `{report['valid']}`",
        "",
        "## Decision de ingenieria",
        "",
        f"- Regla base: {report['engineering_decision']['default_rule']}.",
        f"- Evitar: {report['engineering_decision']['do_not_do']}.",
        "- Medir antes de publicar: "
        + ", ".join(report["engineering_decision"]["measure_before_shipping"])
        + ".",
        "",
        "## Casos",
        "",
    ]
    for case in report["cases"]:
        lines.extend(
            [
                f"### {case['case_id']}: {case['title']}",
                "",
                f"- Modalidades disponibles: {', '.join(case['modalities'])}.",
                f"- Modalidad minima declarada: {', '.join(case['minimum_modalities'])}.",
                f"- Arquitectura candidata: `{case['candidate_architecture']}`.",
                f"- Arquitectura recomendada por el gate: `{case['recommended_architecture']}`.",
                f"- Campos obligatorios: {', '.join(case['output_required_fields'])}.",
                f"- Evidencia requerida: {', '.join(case['evidence_required'])}.",
                f"- Metricas: {', '.join(case['metrics'])}.",
                f"- Riesgo acumulado: {case['risk_score']}.",
                f"- Impuesto multimodal: complejidad={case['modality_tax']['complexity']}, latencia={case['modality_tax']['latency']}, privacidad={case['modality_tax']['privacy']}, evaluacion={case['modality_tax']['evaluation']}.",
                f"- Revision humana: {case['human_review']}.",
                f"- Issues: {', '.join(case['issues']) if case['issues'] else 'sin issues bloqueantes'}.",
                "",
            ]
        )
    if report["high_risk_cases"]:
        lines.extend(
            [
                "## Casos que necesitan mas cuidado",
                "",
                "Estos casos no estan prohibidos, pero deben llevar minimizacion, evidencias y revision antes de publicarse:",
                "",
            ]
        )
        lines.extend(f"- `{case_id}`" for case_id in report["high_risk_cases"])
        lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--fail-on-invalid", action="store_true")
    args = parser.parse_args()

    manifest = load_json("data/modality_manifest.json")
    policy = load_json("contracts/modality_policy.json")
    report = evaluate_manifest(manifest, policy)

    if args.write:
        output = ROOT / "output"
        output.mkdir(exist_ok=True)
        (output / "modality_contract_report.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (output / "modality_contract_report.md").write_text(markdown(report), encoding="utf-8")
    else:
        print(json.dumps(report, ensure_ascii=False, indent=2))

    if args.fail_on_invalid and not report["valid"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
