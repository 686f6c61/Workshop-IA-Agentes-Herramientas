from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from copy import deepcopy
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "contracts/release_policy.json"
BASELINE_PATH = ROOT / "data/baseline_cases.json"
REMEDIATED_PATH = ROOT / "data/remediated_cases.json"
CANDIDATE_PATCH_PATH = ROOT / "data/candidate_patch.json"
INVALID_CASES_PATH = ROOT / "data/invalid_case_examples.json"
OUTPUT = ROOT / "output"
SIGNATURE = "IA para gente curiosa / Facsímil 12 / Capítulo 12 / 686f6c61"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def apply_candidate_patch(remediated_cases: list[dict], patch: dict) -> list[dict]:
    candidate_cases = deepcopy(remediated_cases)
    target_id = patch["target_case_id"]
    changes = patch["changes"]
    for case in candidate_cases:
        if case["case_id"] != target_id:
            continue
        case["evidence_artifacts"] = sorted(set(case["evidence_artifacts"]) | set(changes.get("evidence_artifacts_add", [])))
        case["controls_present"] = sorted(set(case["controls_present"]) | set(changes.get("controls_add", [])))
        case["quality"].update(changes.get("quality_update", {}))
        case["ops"].update(changes.get("ops_update", {}))
        case["expected_decision"] = changes["expected_decision"]
        case["release_candidate_notes"] = changes["release_notes"]
        case["release_owner"] = changes["owner"]
        case["approvers"] = changes["approvers"]
        case["rollback_plan"] = changes["rollback_plan"]
        break
    else:
        raise ValueError(f"No existe el caso objetivo del parche: {target_id}")
    return candidate_cases


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def quality_score(case: dict) -> float:
    values = [float(value) for value in case["quality"].values()]
    return round(mean(values), 4)


def base_risk(case: dict) -> float:
    weights = {
        "pii": 0.18,
        "secret": 0.38,
        "untrusted_content": 0.12,
        "external_action": 0.24,
        "licensed_source": 0.08,
    }
    return round(min(1.0, sum(weight for key, weight in weights.items() if case["risks"].get(key))), 4)


def mitigation_credit(case: dict) -> float:
    controls = set(case["controls_present"])
    credit = 0.0
    if case["risks"].get("pii") and {"redaction_plan", "retention_policy"} <= controls:
        credit += 0.12
    if case["risks"].get("secret") and {"secret_scan", "revocation_runbook"} <= controls:
        credit += 0.20
    if case["risks"].get("untrusted_content") and "taint_label" in controls:
        credit += 0.08
    if case["risks"].get("external_action") and {"approval_gate", "egress_policy"} <= controls:
        credit += 0.18
    if case["risks"].get("licensed_source") and "source_license_check" in controls:
        credit += 0.05
    return round(credit, 4)


def risk_score(case: dict) -> float:
    return round(max(0.0, base_risk(case) - mitigation_credit(case)), 4)


def required_evidence(case: dict, policy: dict) -> list[str]:
    required = set()
    for capability in case["capabilities"]:
        required.update(policy["required_evidence_by_capability"].get(capability, []))
    return sorted(required)


def required_controls(case: dict, policy: dict) -> list[str]:
    required = set()
    for risk_name, active in case["risks"].items():
        if active:
            required.update(policy["required_controls_by_risk"].get(risk_name, []))
    return sorted(required)


def validate_case_contract(case: dict, policy: dict) -> list[str]:
    errors = []
    required_top = [
        "case_id",
        "title",
        "capabilities",
        "chapter_refs",
        "user_story",
        "modalities",
        "evidence_artifacts",
        "controls_present",
        "risks",
        "quality",
        "ops",
        "expected_decision",
    ]
    for field in required_top:
        if field not in case:
            errors.append(f"missing_top_level:{field}")

    if "ops" in case:
        for field in ("latency_ms", "cost_units", "failure_rate"):
            if field not in case["ops"]:
                errors.append(f"missing_ops:{field}")

    if "quality" in case and len(case["quality"]) < 3:
        errors.append("quality_too_sparse")

    if "risks" in case and "evidence_artifacts" in case and "controls_present" in case and "capabilities" in case:
        missing_evidence = sorted(set(required_evidence(case, policy)) - set(case["evidence_artifacts"]))
        missing_controls = sorted(set(required_controls(case, policy)) - set(case["controls_present"]))
        if missing_evidence:
            errors.append("missing_required_evidence:" + "|".join(missing_evidence))
        if missing_controls:
            errors.append("missing_required_controls:" + "|".join(missing_controls))

    if case.get("expected_decision") == "pass" and errors:
        errors.append("expected_pass_but_contract_fails")
    return errors


def score_case(case: dict, policy: dict, scenario: str) -> dict:
    q = quality_score(case)
    r = risk_score(case)
    gates = policy["quality_gates"]
    missing_evidence = sorted(set(required_evidence(case, policy)) - set(case["evidence_artifacts"]))
    missing_controls = sorted(set(required_controls(case, policy)) - set(case["controls_present"]))
    ops = case["ops"]

    failures = []
    if missing_evidence and gates["require_evidence_for_release"]:
        failures.append("missing_evidence")
    if missing_controls:
        failures.append("missing_controls")
    if q < gates["review_min_quality"]:
        failures.append("quality_below_review")
    elif q < gates["pass_min_quality"]:
        failures.append("quality_below_pass")
    if r >= gates["block_min_risk"]:
        failures.append("risk_above_block")
    elif r >= gates["review_min_risk"]:
        failures.append("risk_above_review")
    if ops["latency_ms"] > gates["max_latency_ms"]:
        failures.append("latency_above_slo")
    if ops["cost_units"] > gates["max_cost_units"]:
        failures.append("cost_above_budget")
    if ops["failure_rate"] > gates["max_failure_rate"]:
        failures.append("failure_rate_above_slo")
    if case["risks"].get("secret") and {"secret_scan", "revocation_runbook"} - set(case["controls_present"]):
        failures.append("secret_without_full_response")
    if case["risks"].get("external_action") and gates["require_human_approval_for_external_action"]:
        if {"approval_gate", "egress_policy"} - set(case["controls_present"]):
            failures.append("external_action_without_approval_or_egress")
    if gates["require_policy_decision_for_sensitive_cases"] and (case["risks"].get("pii") or case["risks"].get("secret") or case["risks"].get("external_action")):
        if "policy_decision" not in case["evidence_artifacts"] and "risk_ops" in case["capabilities"]:
            failures.append("missing_policy_decision")

    block_reasons = {
        "risk_above_block",
        "secret_without_full_response",
        "external_action_without_approval_or_egress",
    }
    if block_reasons & set(failures):
        decision = "block"
    elif failures:
        decision = "review"
    else:
        decision = "pass"

    return {
        "scenario": scenario,
        "case_id": case["case_id"],
        "title": case["title"],
        "capabilities": case["capabilities"],
        "chapter_refs": case["chapter_refs"],
        "modalities": case["modalities"],
        "quality_score": q,
        "base_risk": base_risk(case),
        "mitigation_credit": mitigation_credit(case),
        "risk_score": r,
        "latency_ms": ops["latency_ms"],
        "cost_units": ops["cost_units"],
        "failure_rate": ops["failure_rate"],
        "missing_evidence": missing_evidence,
        "missing_controls": missing_controls,
        "failures": sorted(set(failures)),
        "decision": decision,
        "expected_decision": case["expected_decision"],
        "decision_matches_expected": decision == case["expected_decision"],
        "next_action": next_action(decision, missing_evidence, missing_controls, sorted(set(failures))),
    }


def next_action(decision: str, missing_evidence: list[str], missing_controls: list[str], failures: list[str]) -> str:
    if decision == "pass":
        return "Publicar con monitorización y conservar evidencia de release."
    if "secret_without_full_response" in failures:
        return "Bloquear, escanear secretos, redactar artefactos y definir runbook de revocación."
    if "external_action_without_approval_or_egress" in failures:
        return "Bloquear ejecución externa hasta tener approval gate y egress policy."
    if missing_evidence:
        return "Completar evidencias: " + ", ".join(missing_evidence[:4])
    if missing_controls:
        return "Completar controles: " + ", ".join(missing_controls[:4])
    if "latency_above_slo" in failures or "failure_rate_above_slo" in failures:
        return "Revisar SLO, latencia, retries y degradación antes de publicar."
    return "Enviar a revisión técnica con evidencia y decisión explícita."


def aggregate(scored: list[dict], scenario: str) -> dict:
    decisions = Counter(item["decision"] for item in scored)
    return {
        "scenario": scenario,
        "case_count": len(scored),
        "pass_count": decisions["pass"],
        "review_count": decisions["review"],
        "block_count": decisions["block"],
        "avg_quality": round(mean([item["quality_score"] for item in scored]), 4),
        "avg_risk": round(mean([item["risk_score"] for item in scored]), 4),
        "global_decision": "block_release" if decisions["block"] else ("review_release" if decisions["review"] else "ship"),
        "mismatches": [item["case_id"] for item in scored if not item["decision_matches_expected"]],
    }


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    normalized = []
    for row in rows:
        clean = dict(row)
        for key, value in list(clean.items()):
            if isinstance(value, list):
                clean[key] = "|".join(str(item) for item in value)
        normalized.append(clean)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(normalized)


def chapter_traceability_rows(all_cases: list[dict], policy: dict) -> list[dict]:
    rows = []
    chapter_cases: dict[int, list[str]] = defaultdict(list)
    for case in all_cases:
        for chapter in case["chapter_refs"]:
            chapter_cases[int(chapter)].append(case["case_id"])
    for chapter, description in sorted(policy["chapter_traceability"].items(), key=lambda item: int(item[0])):
        cases = sorted(set(chapter_cases.get(int(chapter), [])))
        rows.append(
            {
                "chapter": chapter,
                "concept": description,
                "case_count": len(cases),
                "cases": cases,
            }
        )
    return rows


def modality_rows(scored: list[dict]) -> list[dict]:
    by_modality: dict[str, list[dict]] = defaultdict(list)
    for item in scored:
        for modality in item["modalities"]:
            by_modality[modality].append(item)
    rows = []
    for modality, items in sorted(by_modality.items()):
        rows.append(
            {
                "modality": modality,
                "case_count": len(items),
                "avg_quality": round(mean([item["quality_score"] for item in items]), 4),
                "avg_risk": round(mean([item["risk_score"] for item in items]), 4),
                "blocks": sum(1 for item in items if item["decision"] == "block"),
                "reviews": sum(1 for item in items if item["decision"] == "review"),
            }
        )
    return rows


def remediation_diff_rows(baseline: list[dict], remediated: list[dict]) -> list[dict]:
    by_base = {item["case_id"]: item for item in baseline}
    rows = []
    for item in remediated:
        before = by_base[item["case_id"]]
        rows.append(
            {
                "case_id": item["case_id"],
                "decision_before": before["decision"],
                "decision_after": item["decision"],
                "quality_delta": round(item["quality_score"] - before["quality_score"], 4),
                "risk_delta": round(item["risk_score"] - before["risk_score"], 4),
                "latency_delta_ms": item["latency_ms"] - before["latency_ms"],
                "failure_rate_delta": round(item["failure_rate"] - before["failure_rate"], 4),
                "remaining_failures": item["failures"],
            }
        )
    return rows


def sli_slo_rows(scored: list[dict], policy: dict) -> list[dict]:
    gates = policy["quality_gates"]
    rows = []
    for item in scored:
        checks = [
            ("quality_score", item["quality_score"], ">=", gates["pass_min_quality"], item["quality_score"] >= gates["pass_min_quality"]),
            ("risk_score", item["risk_score"], "<", gates["review_min_risk"], item["risk_score"] < gates["review_min_risk"]),
            ("latency_ms", item["latency_ms"], "<=", gates["max_latency_ms"], item["latency_ms"] <= gates["max_latency_ms"]),
            ("cost_units", item["cost_units"], "<=", gates["max_cost_units"], item["cost_units"] <= gates["max_cost_units"]),
            ("failure_rate", item["failure_rate"], "<=", gates["max_failure_rate"], item["failure_rate"] <= gates["max_failure_rate"]),
            ("missing_evidence_count", len(item["missing_evidence"]), "==", 0, len(item["missing_evidence"]) == 0),
            ("missing_controls_count", len(item["missing_controls"]), "==", 0, len(item["missing_controls"]) == 0),
        ]
        for metric, value, operator, threshold, ok in checks:
            rows.append(
                {
                    "scenario": item["scenario"],
                    "case_id": item["case_id"],
                    "metric": metric,
                    "value": value,
                    "operator": operator,
                    "threshold": threshold,
                    "status": "pass" if ok else "review",
                }
            )
    return rows


def write_version_manifest(patch: dict, summaries: dict) -> None:
    payload = {
        "schema_version": "1.0",
        "project": "IA para gente curiosa",
        "fasciculo": 12,
        "capitulo": 12,
        "artifact": "multimodal_release_lab",
        "dataset_versions": {
            "baseline": "baseline_cases.v1",
            "remediated": "remediated_cases.v1",
            "candidate_patch": patch["patch_id"],
        },
        "model_contract_versions": {
            "vision_language": "vlm_contract.v1",
            "document_ai": "document_ai_contract.v1",
            "multimodal_rag": "retrieval_manifest.v1",
            "realtime_voice": "voice_turn_contract.v1",
            "video_temporal": "temporal_event_contract.v1",
            "computer_use": "approval_card.v1",
            "risk_ops": "policy_decision.v1",
        },
        "release_summaries": summaries,
        "regression_policy": [
            "Repetir evaluación si cambia el modelo visual, LLM, OCR, ASR, embedding, índice, prompt, herramienta o policy.",
            "Bloquear release si una ruta sensible pierde policy_decision, lineage, redacción o aprobación.",
            "Abrir revisión si p95 de latencia, coste o failure_rate superan el SLO del contrato.",
        ],
    }
    (OUTPUT / "version_manifest.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def write_change_request(candidate: list[dict], summary: dict, diff: list[dict], patch: dict) -> None:
    target = next(item for item in candidate if item["case_id"] == patch["target_case_id"])
    target_diff = next(item for item in diff if item["case_id"] == patch["target_case_id"])
    lines = [
        "# Release change request · F12 C12",
        "",
        f"Estado propuesto: `{summary['global_decision']}`.",
        f"Caso que desbloquea el candidato: `{target['case_id']}`.",
        "",
        "## Cambio técnico",
        "",
    ]
    for note in patch["changes"]["release_notes"]:
        lines.append(f"- {note}")
    lines.extend(
        [
            "",
            "## Evidencia nueva",
            "",
        ]
    )
    for evidence in patch["changes"].get("evidence_artifacts_add", []):
        lines.append(f"- `{evidence}`")
    lines.extend(
        [
            "",
            "## Impacto medido",
            "",
            f"- Decisión antes: `{target_diff['decision_before']}`.",
            f"- Decisión después: `{target_diff['decision_after']}`.",
            f"- Delta calidad: `{target_diff['quality_delta']}`.",
            f"- Delta riesgo: `{target_diff['risk_delta']}`.",
            f"- Delta latencia: `{target_diff['latency_delta_ms']} ms`.",
            f"- Delta failure rate: `{target_diff['failure_rate_delta']}`.",
            "",
            "## Owner y aprobación",
            "",
            f"- Owner técnico: `{patch['changes']['owner']}`.",
            "- Aprobadores: " + ", ".join(f"`{item}`" for item in patch["changes"]["approvers"]) + ".",
            "",
            "## Rollback",
            "",
            patch["changes"]["rollback_plan"],
            "",
            "## Criterio de merge",
            "",
            "- `make test` debe pasar.",
            "- `output/sli_slo_matrix.csv` no debe contener métricas en revisión para el escenario `candidate`.",
            "- `output/release_candidate_diff.csv` debe explicar qué cambió respecto a `remediated`.",
            "- `output/version_manifest.json` debe registrar versiones de datos, contratos y policy.",
        ]
    )
    (OUTPUT / "release_change_request.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_pr_checklist() -> None:
    lines = [
        "# PR checklist · release multimodal",
        "",
        "- [ ] El ZIP se ejecuta con `make run` y `make test`.",
        "- [ ] La decisión global no depende de una media agregada.",
        "- [ ] Cada caso sensible tiene `policy_decision`, redacción y lineage.",
        "- [ ] Cada acción externa tiene approval card y egress policy.",
        "- [ ] Los SLI/SLO quedan dentro de umbral en `output/sli_slo_matrix.csv`.",
        "- [ ] Hay owner técnico, aprobadores y rollback.",
        "- [ ] Se repitieron evals tras cambios de modelo, OCR, ASR, retrieval, prompt, tool o policy.",
        "- [ ] La decisión final se puede defender con `output/evidence_pack.md` y `output/release_change_request.md`.",
    ]
    (OUTPUT / "release_pr_checklist.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_contract_validation_report(valid_cases: list[dict], invalid_cases: list[dict], policy: dict) -> list[dict]:
    rows = []
    for source, cases in (("candidate", valid_cases), ("invalid_examples", invalid_cases)):
        for case in cases:
            errors = validate_case_contract(case, policy)
            rows.append(
                {
                    "source": source,
                    "case_id": case.get("case_id", "missing_case_id"),
                    "status": "pass" if not errors else "fail",
                    "errors": errors,
                }
            )

    payload = {
        "schema_version": "1.0",
        "rows": rows,
        "summary": {
            "checked": len(rows),
            "passed": sum(1 for row in rows if row["status"] == "pass"),
            "failed": sum(1 for row in rows if row["status"] == "fail"),
        },
    }
    (OUTPUT / "contract_validation_report.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# Informe de validación de contratos",
        "",
        "Este informe muestra por qué un caso no debería entrar en una evaluación de release solo porque tenga una historia de usuario bonita.",
        "",
        "| Fuente | Caso | Estado | Errores |",
        "|---|---|---|---|",
    ]
    for row in rows:
        errors = ", ".join(row["errors"]) or "none"
        lines.append(f"| `{row['source']}` | `{row['case_id']}` | `{row['status']}` | {errors} |")
    lines.extend(
        [
            "",
            "## Lectura de ingeniería",
            "",
            "- Un contrato operativo incompleto no se arregla con más prompt.",
            "- Un caso sensible que espera `pass` pero no tiene evidencias o controles debe fallar antes de llegar al modelo.",
            "- Validar contratos reduce ambigüedad en CI/CD y evita discusiones tardías en producción.",
        ]
    )
    (OUTPUT / "contract_validation_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return rows


def write_report(path: Path, scored: list[dict], summary: dict) -> None:
    lines = [
        f"# Informe de release multimodal · {summary['scenario']}",
        "",
        f"Decisión global: `{summary['global_decision']}`",
        f"Casos: `{summary['case_count']}` · pass `{summary['pass_count']}` · review `{summary['review_count']}` · block `{summary['block_count']}`",
        f"Calidad media: `{summary['avg_quality']}` · riesgo medio: `{summary['avg_risk']}`",
        "",
        "| Caso | Calidad | Riesgo | Latencia | Decisión | Fallos | Siguiente acción |",
        "|---|---:|---:|---:|---|---|---|",
    ]
    for item in scored:
        failures = ", ".join(item["failures"]) or "none"
        lines.append(
            f"| `{item['case_id']}` | {item['quality_score']} | {item['risk_score']} | {item['latency_ms']} ms | `{item['decision']}` | {failures} | {item['next_action']} |"
        )
    lines.extend(
        [
            "",
            "## Lectura de ingeniería",
            "",
            "- `pass` significa que hay evidencias suficientes, calidad mínima, riesgo mitigado y operación dentro de límites.",
            "- `review` significa que el sistema puede ser prometedor, pero le falta evidencia, control, métrica o estabilidad.",
            "- `block` significa que publicar sería irresponsable: hay secreto, acción externa sin aprobación o riesgo no mitigado.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_evidence_pack(baseline: list[dict], remediated: list[dict], summaries: dict) -> None:
    blockers = [item for item in baseline if item["decision"] == "block"]
    improved = [item for item in remediated if item["decision"] == "pass"]
    lines = [
        "# Paquete de evidencias del laboratorio multimodal",
        "",
        "## Decisión ejecutiva",
        "",
        f"- Baseline: `{summaries['baseline']['global_decision']}`.",
        f"- Remediado: `{summaries['remediated']['global_decision']}`.",
        f"- Candidate: `{summaries['candidate']['global_decision']}`.",
        f"- Casos bloqueados al inicio: `{len(blockers)}`.",
        f"- Casos publicables tras remediación: `{len(improved)}`.",
        "",
        "## Casos que no pueden publicarse en baseline",
        "",
    ]
    for item in blockers:
        lines.append(f"- `{item['case_id']}`: {item['next_action']}")
    lines.extend(
        [
            "",
            "## Evidencias mínimas para defender el release",
            "",
            "- Contratos de entrada y salida por capacidad.",
            "- Golden set y slices de evaluación.",
            "- Manifest de retrieval, ACL de fuentes y grounding.",
            "- Trazas de turnos, latencia y tool calls.",
            "- Redaction plan, policy decision y artifact lineage.",
            "- Runbook para secretos, PII y acciones externas.",
            "- SLI/SLO por caso y por escenario.",
            "- Change request con owner, aprobadores y rollback.",
            "",
            "## Qué mirar en una revisión",
            "",
            "1. Ningún caso con secreto o acción externa puede depender solo del prompt.",
            "2. Las métricas deben estar separadas por modalidad y por slice.",
            "3. El coste y la latencia forman parte del release, no del apéndice.",
            "4. La evidencia debe poder descargarse, reproducirse y explicarse.",
            "5. Un release candidate debe incluir diff, manifest de versiones, contract tests y checklist de PR.",
        ]
    )
    (OUTPUT / "evidence_pack.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_decision_card(remediated: list[dict], summary: dict, candidate_summary: dict) -> None:
    lines = [
        "# Decision card · laboratorio multimodal",
        "",
        f"Decisión remediada: `{summary['global_decision']}`.",
        f"Release candidate propuesto: `{candidate_summary['global_decision']}`.",
        "",
        "## Condiciones",
        "",
        "- Mantener gates de privacidad y seguridad del capítulo 11.",
        "- No publicar casos `review` sin owner y plan de remediación.",
        "- Ejecutar regresión multimodal antes de cada cambio de modelo, prompt, OCR, ASR, retrieval o tool.",
        "- Aceptar el candidato solo si el change request conserva owner, aprobadores, rollback y SLI/SLO en verde.",
        "",
        "## Casos pendientes",
        "",
    ]
    pending = [item for item in remediated if item["decision"] != "pass"]
    if not pending:
        lines.append("- No quedan casos pendientes.")
    for item in pending:
        lines.append(f"- `{item['case_id']}`: `{item['decision']}` · {item['next_action']}")
    lines.extend(
        [
            "",
            "## Criterio de salida",
            "",
            "El sistema puede avanzar como candidato solo si los casos pendientes quedan cerrados en `output/release_change_request.md` y `output/sli_slo_matrix.csv`.",
        ]
    )
    (OUTPUT / "decision_card.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_svg(baseline_summary: dict, remediated_summary: dict) -> None:
    width = 1280
    height = 820
    stages = [
        ("Entrada", "imagen · PDF · audio · vídeo · pantalla"),
        ("Contratos", "schemas · request · output"),
        ("Evaluación", "golden set · slices · grounding"),
        ("Riesgo", "PII · secreto · acción externa"),
        ("Operación", "latencia · coste · fallos"),
        ("Release", "pass · review · block"),
    ]
    stage_svg = []
    for idx, (title, body) in enumerate(stages):
        x = 60 + idx * 200
        fill = "#FFFFFF" if idx % 2 == 0 else "#F7F7F7"
        stage_svg.append(f'<rect x="{x}" y="150" width="156" height="220" fill="{fill}" stroke="#111111" stroke-width="1.2"/>')
        stage_svg.append(f'<text x="{x + 78}" y="184" text-anchor="middle" font-size="13" font-weight="700" fill="#111111">{escape(title)}</text>')
        for line_idx, line in enumerate(body.split(" · ")):
            stage_svg.append(f'<text x="{x + 78}" y="{226 + line_idx * 28}" text-anchor="middle" font-size="11" fill="#555555">{escape(line)}</text>')
        if idx < len(stages) - 1:
            stage_svg.append(f'<line x1="{x + 156}" y1="260" x2="{x + 198}" y2="260" stroke="#111111" stroke-width="1.4" marker-end="url(#f12lab-arrow)"/>')
    svg = f'''<svg viewBox="0 0 {width} {height}" role="img" aria-labelledby="f12lab-title f12lab-desc" xmlns="http://www.w3.org/2000/svg">
  <title id="f12lab-title">Laboratorio multimodal de release</title>
  <desc id="f12lab-desc">Pipeline de laboratorio para decidir release multimodal con contratos, evaluación, riesgo, operación y evidencias.</desc>
  <defs>
    <marker id="f12lab-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L0,6 L9,3 z" fill="#111111"/>
    </marker>
  </defs>
  <rect width="{width}" height="{height}" fill="#FFFFFF"/>
  <text x="60" y="58" font-size="29" font-weight="700" fill="#111111">Laboratorio final: release multimodal defendible</text>
  <text x="60" y="90" font-size="15" fill="#555555">La salida no es un score: es una decisión con evidencias, riesgos, operación y remediación.</text>
  {''.join(stage_svg)}
  <rect x="100" y="462" width="480" height="140" fill="#F7F7F7" stroke="#111111" stroke-width="1.2"/>
  <text x="340" y="500" text-anchor="middle" font-size="18" font-weight="700" fill="#111111">Baseline</text>
  <text x="340" y="536" text-anchor="middle" font-size="14" fill="#111111">{baseline_summary["global_decision"]}</text>
  <text x="340" y="566" text-anchor="middle" font-size="13" fill="#555555">{baseline_summary["pass_count"]} pass · {baseline_summary["review_count"]} review · {baseline_summary["block_count"]} block</text>
  <rect x="700" y="462" width="480" height="140" fill="#FFFFFF" stroke="#111111" stroke-width="1.2"/>
  <text x="940" y="500" text-anchor="middle" font-size="18" font-weight="700" fill="#111111">Remediado</text>
  <text x="940" y="536" text-anchor="middle" font-size="14" fill="#111111">{remediated_summary["global_decision"]}</text>
  <text x="940" y="566" text-anchor="middle" font-size="13" fill="#555555">{remediated_summary["pass_count"]} pass · {remediated_summary["review_count"]} review · {remediated_summary["block_count"]} block</text>
  <line x1="582" y1="532" x2="698" y2="532" stroke="#111111" stroke-width="1.6" marker-end="url(#f12lab-arrow)"/>
  <text x="640" y="518" text-anchor="middle" font-size="12" fill="#555555">remediación</text>
  <text x="1190" y="766" text-anchor="end" font-size="11" fill="#999999">{SIGNATURE}</text>
</svg>
'''
    (OUTPUT / "multimodal_lab_architecture.svg").write_text(svg, encoding="utf-8")


def main() -> None:
    policy = load_json(POLICY_PATH)
    baseline_cases = load_json(BASELINE_PATH)
    remediated_cases = load_json(REMEDIATED_PATH)
    candidate_patch = load_json(CANDIDATE_PATCH_PATH)
    invalid_cases = load_json(INVALID_CASES_PATH)
    candidate_cases = apply_candidate_patch(remediated_cases, candidate_patch)
    OUTPUT.mkdir(exist_ok=True)

    baseline_scored = [score_case(case, policy, "baseline") for case in baseline_cases]
    remediated_scored = [score_case(case, policy, "remediated") for case in remediated_cases]
    candidate_scored = [score_case(case, policy, "candidate") for case in candidate_cases]
    baseline_summary = aggregate(baseline_scored, "baseline")
    remediated_summary = aggregate(remediated_scored, "remediated")
    candidate_summary = aggregate(candidate_scored, "candidate")
    summaries = {
        "baseline": baseline_summary,
        "remediated": remediated_summary,
        "candidate": candidate_summary,
    }
    all_scored = baseline_scored + remediated_scored + candidate_scored
    traceability = chapter_traceability_rows(baseline_cases + remediated_cases + candidate_cases, policy)
    diff = remediation_diff_rows(baseline_scored, remediated_scored)
    candidate_diff = remediation_diff_rows(remediated_scored, candidate_scored)
    modalities = modality_rows(all_scored)
    slis = sli_slo_rows(all_scored, policy)
    contract_validation = write_contract_validation_report(candidate_cases, invalid_cases, policy)

    report = {
        "schema_version": "1.0",
        "project": "IA para gente curiosa",
        "fasciculo": 12,
        "capitulo": 12,
        "summaries": summaries,
        "baseline": baseline_scored,
        "remediated": remediated_scored,
        "candidate": candidate_scored,
        "remediation_diff": diff,
        "release_candidate_diff": candidate_diff,
        "chapter_traceability": traceability,
        "modality_coverage": modalities,
        "sli_slo_matrix": slis,
        "contract_validation": contract_validation,
        "candidate_patch": candidate_patch,
        "policy": policy,
    }
    (OUTPUT / "release_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    write_report(OUTPUT / "baseline_release_report.md", baseline_scored, baseline_summary)
    write_report(OUTPUT / "remediated_release_report.md", remediated_scored, remediated_summary)
    write_report(OUTPUT / "candidate_release_report.md", candidate_scored, candidate_summary)
    write_evidence_pack(baseline_scored, remediated_scored, summaries)
    write_decision_card(remediated_scored, remediated_summary, candidate_summary)
    write_version_manifest(candidate_patch, summaries)
    write_change_request(candidate_scored, candidate_summary, candidate_diff, candidate_patch)
    write_pr_checklist()
    write_svg(baseline_summary, remediated_summary)
    write_csv(
        OUTPUT / "release_matrix.csv",
        all_scored,
        ["scenario", "case_id", "title", "capabilities", "chapter_refs", "modalities", "quality_score", "base_risk", "mitigation_credit", "risk_score", "latency_ms", "cost_units", "failure_rate", "decision", "failures", "missing_evidence", "missing_controls", "next_action"],
    )
    write_csv(
        OUTPUT / "remediation_diff.csv",
        diff,
        ["case_id", "decision_before", "decision_after", "quality_delta", "risk_delta", "latency_delta_ms", "failure_rate_delta", "remaining_failures"],
    )
    write_csv(
        OUTPUT / "release_candidate_diff.csv",
        candidate_diff,
        ["case_id", "decision_before", "decision_after", "quality_delta", "risk_delta", "latency_delta_ms", "failure_rate_delta", "remaining_failures"],
    )
    write_csv(
        OUTPUT / "chapter_traceability.csv",
        traceability,
        ["chapter", "concept", "case_count", "cases"],
    )
    write_csv(
        OUTPUT / "modality_coverage.csv",
        modalities,
        ["modality", "case_count", "avg_quality", "avg_risk", "blocks", "reviews"],
    )
    write_csv(
        OUTPUT / "sli_slo_matrix.csv",
        slis,
        ["scenario", "case_id", "metric", "value", "operator", "threshold", "status"],
    )
    write_csv(
        OUTPUT / "contract_validation_matrix.csv",
        contract_validation,
        ["source", "case_id", "status", "errors"],
    )
    print(
        "OK: baseline "
        f"{baseline_summary['global_decision']} -> remediated {remediated_summary['global_decision']} "
        f"-> candidate {candidate_summary['global_decision']} ({len(baseline_scored)} casos)"
    )


if __name__ == "__main__":
    main()
