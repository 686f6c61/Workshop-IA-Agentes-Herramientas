from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "contracts/multimodal_risk_policy.json"
CASES_PATH = ROOT / "data/multimodal_risk_cases.json"
DETECTOR_EVAL_PATH = ROOT / "data/detector_eval_cases.json"
POLICY_DECISIONS_PATH = ROOT / "data/policy_decision_examples.json"
OUTPUT = ROOT / "output"
SIGNATURE = "IA para gente curiosa / Facsímil 12 / Capítulo 11 / 686f6c61"
SECRET_ENTITY_TYPES = {"API_KEY", "INTERNAL_SECRET", "ACCESS_TOKEN_FRAGMENT", "COOKIE"}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def entity_sensitivity(case: dict, policy: dict) -> float:
    entities = case.get("entities", [])
    if not entities:
        return 0.0
    scores = []
    for entity in entities:
        base = policy["entity_sensitivity"].get(entity["type"], 0.4)
        confidence = float(entity.get("confidence", 0.5))
        scores.append(base * confidence)
    return min(1.0, max(scores))


def exposure_score(case: dict, policy: dict) -> float:
    score = 0.0
    if case["destination"] not in policy["approved_destinations"]:
        score += 0.28
    if case["destination"] in policy["blocked_destinations"]:
        score += 0.28
    if case["storage"] in {"raw_prompt", "secret_leak"}:
        score += 0.22
    if case["modality"] in {"ui_trace", "video", "eval_dataset"}:
        score += 0.12
    if case.get("external_action"):
        score += 0.22
    return min(1.0, score)


def missing_controls(case: dict, policy: dict) -> list[str]:
    required = set(policy["required_controls_by_modality"].get(case["modality"], []))
    present = set(case.get("present_controls", []))
    return sorted(required - present)


def required_redactions(case: dict, policy: dict) -> list[dict]:
    rows = []
    for entity in case.get("entities", []):
        rows.append(
            {
                "case_id": case["case_id"],
                "entity_type": entity["type"],
                "operator": policy["redaction_operators"].get(entity["type"], "review"),
                "location": entity.get("location", ""),
                "confidence": entity.get("confidence", ""),
            }
        )
    return rows


def retention_days(case: dict, policy: dict) -> int | None:
    return policy["retention_days"].get(case["storage"])


def score_case(case: dict, policy: dict) -> dict:
    sensitivity = entity_sensitivity(case, policy)
    exposure = exposure_score(case, policy)
    impact = float(case.get("impact", 0.5))
    missing = missing_controls(case, policy)
    control_penalty = min(0.25, 0.06 * len(missing))
    risk = min(1.0, (0.36 * sensitivity) + (0.24 * exposure) + (0.28 * impact) + control_penalty)

    failures = []
    gates = policy["quality_gates"]
    unredacted = set(case.get("unredacted_entities_in_output", []))
    if gates["block_on_unredacted_secret"] and SECRET_ENTITY_TYPES & unredacted:
        failures.append("secreto_sin_redactar")
    if gates["block_on_actionable_prompt_injection"] and case.get("prompt_injection_detected") and case["modality"] == "ui_trace":
        failures.append("prompt_injection_visual_actionable")
    if case["destination"] in policy["blocked_destinations"]:
        failures.append("destino_bloqueado")
    if gates["require_human_approval_for_external_submit"] and case.get("external_action"):
        failures.append("accion_externa_requiere_aprobacion")
    if gates["require_owner_for_high_risk"] and risk >= gates["review_min_risk"] and not case.get("owner"):
        failures.append("owner_faltante")
    if gates["require_retention_for_persistent_storage"] and retention_days(case, policy) is None:
        failures.append("retencion_no_definida")
    if missing:
        failures.append("controles_faltantes")

    if any(item in failures for item in ["secreto_sin_redactar", "prompt_injection_visual_actionable", "destino_bloqueado"]) or risk >= gates["block_min_risk"]:
        decision = "block"
    elif failures or risk >= gates["review_min_risk"]:
        decision = "review"
    else:
        decision = "pass"

    return {
        "case_id": case["case_id"],
        "title": case["title"],
        "modality": case["modality"],
        "purpose": case["purpose"],
        "owner": case["owner"],
        "destination": case["destination"],
        "storage": case["storage"],
        "entity_count": len(case.get("entities", [])),
        "max_entity_sensitivity": round(sensitivity, 4),
        "exposure_score": round(exposure, 4),
        "impact": round(impact, 4),
        "risk_score": round(risk, 4),
        "missing_controls": missing,
        "retention_days": retention_days(case, policy),
        "decision": decision,
        "expected_decision": case["expected_decision"],
        "decision_matches_expected": decision == case["expected_decision"],
        "failures": failures,
        "next_action": next_action(decision, failures, missing, case),
    }


def next_action(decision: str, failures: list[str], missing: list[str], case: dict) -> str:
    if decision == "pass":
        return "Mantener como caso de regresión y vigilar drift de entradas."
    if "secreto_sin_redactar" in failures:
        entity_types = {entity["type"] for entity in case.get("entities", [])}
        if not {"API_KEY", "ACCESS_TOKEN_FRAGMENT", "COOKIE"} & entity_types:
            return "Redactar información interna, revisar acceso de la fuente y bloquear publicación."
        return "Revocar secreto, redactar captura, abrir incidente y bloquear publicación."
    if "prompt_injection_visual_actionable" in failures:
        return "Etiquetar OCR como contenido no confiable y bloquear cualquier acción derivada."
    if "destino_bloqueado" in failures:
        return "Revisar egress policy: el destino no puede recibir esta modalidad."
    if missing:
        return "Añadir controles faltantes: " + ", ".join(missing)
    if case.get("external_action"):
        return "Solicitar aprobación humana antes de salida externa."
    return "Enviar a revisión de privacidad/seguridad antes de publicar."


def aggregate(scored: list[dict]) -> dict:
    by_decision = Counter(item["decision"] for item in scored)
    by_modality = defaultdict(list)
    for item in scored:
        by_modality[item["modality"]].append(item["risk_score"])
    modality_rows = [
        {
            "modality": modality,
            "case_count": len(scores),
            "avg_risk_score": round(sum(scores) / len(scores), 4),
            "max_risk_score": round(max(scores), 4),
        }
        for modality, scores in sorted(by_modality.items())
    ]
    global_decision = "pass"
    if by_decision["block"]:
        global_decision = "block_release"
    elif by_decision["review"]:
        global_decision = "review_before_release"
    return {
        "global_decision": global_decision,
        "case_count": len(scored),
        "pass_count": by_decision["pass"],
        "review_count": by_decision["review"],
        "block_count": by_decision["block"],
        "max_risk_score": round(max(item["risk_score"] for item in scored), 4),
        "avg_risk_score": round(sum(item["risk_score"] for item in scored) / len(scored), 4),
        "modality_rows": modality_rows,
        "mismatches": [item["case_id"] for item in scored if not item["decision_matches_expected"]],
    }


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    normalized = []
    for row in rows:
        clean = dict(row)
        for key, value in list(clean.items()):
            if isinstance(clean.get(key), list):
                clean[key] = "|".join(str(item) for item in value)
        normalized.append(clean)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(normalized)


def threat_model_rows(cases: list[dict], scored: list[dict]) -> list[dict]:
    scored_by_case = {item["case_id"]: item for item in scored}
    catalog = {
        "document": {
            "asset": "PDF, OCR y campos extraídos",
            "trust_boundary": "upload de usuario -> OCR/Document AI -> proveedor o store interno",
            "failure_mode": "un identificador se conserva o viaja fuera de finalidad",
            "control": "ocr_pii_scan, field_level_redaction, retention_policy",
            "test": "fixture con DNI/correo y aserción de redacción por campo",
        },
        "image": {
            "asset": "píxeles, regiones detectadas y metadatos EXIF",
            "trust_boundary": "imagen del usuario -> preprocesado -> modelo visual",
            "failure_mode": "cara, matrícula, dirección o GPS quedan visibles",
            "control": "image_pii_scan, region_redaction, metadata_strip",
            "test": "imagen con región sensible y metadatos antes/después",
        },
        "audio": {
            "asset": "audio bruto, transcript, slots y voz",
            "trust_boundary": "stream de voz -> ASR -> extractor de intención",
            "failure_mode": "dato personal o sanitario se guarda como transcript bruto",
            "control": "transcript_pii_scan, slot_confirmation, retention_policy",
            "test": "transcript con baja confianza y entidad sensible",
        },
        "video": {
            "asset": "frames, objetos, eventos y marcas temporales",
            "trust_boundary": "vídeo -> muestreo de frames -> analítica temporal",
            "failure_mode": "se conservan identificadores en frames no necesarios",
            "control": "frame_sampling_policy, region_redaction, retention_policy",
            "test": "frame con matrícula/cara y control faltante",
        },
        "rag": {
            "asset": "fuentes recuperadas, OCR de documentos y citas",
            "trust_boundary": "índice multimodal -> retrieval -> contexto del modelo",
            "failure_mode": "fuente interna o nota confidencial aparece en respuesta",
            "control": "acl_filter, source_label, claim_grounding",
            "test": "documento con ACL y claim sensible no autorizado",
        },
        "ui_trace": {
            "asset": "captura, DOM, OCR, cookies, panel de red y acción externa",
            "trust_boundary": "pantalla observada -> agente -> tool externa",
            "failure_mode": "OCR malicioso o secreto gobierna una acción",
            "control": "secret_scan, taint_ocr, approval_gate, egress_policy",
            "test": "captura con API key y orden visual",
        },
        "eval_dataset": {
            "asset": "fixture, prompt, metadatos, expected output y trazas",
            "trust_boundary": "incidente real -> dataset de evaluación -> CI",
            "failure_mode": "un dato real queda congelado como regresión",
            "control": "redacted_fixture, dataset_owner, retention_policy",
            "test": "fixture con correo o token reconstruible",
        },
    }
    rows = []
    for case in cases:
        item = scored_by_case[case["case_id"]]
        template = catalog.get(case["modality"], {})
        rows.append(
            {
                "case_id": case["case_id"],
                "modality": case["modality"],
                "asset": template.get("asset", "artefacto multimodal"),
                "trust_boundary": template.get("trust_boundary", "entrada -> sistema"),
                "failure_mode": template.get("failure_mode", "salida o conservación no autorizada"),
                "control": template.get("control", ", ".join(case.get("present_controls", []))),
                "test": template.get("test", "caso de regresión específico"),
                "decision": item["decision"],
                "risk_score": item["risk_score"],
            }
        )
    return rows


def short_hash(value: dict) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def lineage_rows(cases: list[dict], scored: list[dict], policy: dict) -> list[dict]:
    scored_by_case = {item["case_id"]: item for item in scored}
    policy_hash = short_hash(policy)
    rows = []
    for case in cases:
        item = scored_by_case[case["case_id"]]
        operators = sorted(
            {
                policy["redaction_operators"].get(entity["type"], "review")
                for entity in case.get("entities", [])
            }
        )
        rows.append(
            {
                "artifact_id": f"art_{case['case_id']}",
                "case_id": case["case_id"],
                "artifact_hash": short_hash(case),
                "modality": case["modality"],
                "surface": case.get("surface", ""),
                "owner": case.get("owner", ""),
                "destination": case.get("destination", ""),
                "storage": case.get("storage", ""),
                "policy_hash": policy_hash,
                "detector_version": "simulated-multimodal-detector-0.1",
                "redaction_operators": "|".join(operators) if operators else "none",
                "decision": item["decision"],
                "retention_days": item["retention_days"],
            }
        )
    return rows


def evaluate_policy_decisions(examples: list[dict], policy: dict) -> list[dict]:
    rows = []
    approved = set(policy["approved_destinations"])
    blocked = set(policy["blocked_destinations"])
    for example in examples:
        context = example["context"]
        if context["destination"] in blocked or context["has_unredacted_secret"] or context["external_action"]:
            decision = "deny"
        elif context["destination"] in approved and context["risk_score"] < policy["quality_gates"]["review_min_risk"] and context["missing_controls"] == 0:
            decision = "allow"
        elif context["destination"] in approved:
            decision = "review"
        else:
            decision = "deny"
        reasons = []
        if context["destination"] in blocked:
            reasons.append("blocked_destination")
        if context["has_unredacted_secret"]:
            reasons.append("unredacted_secret")
        if context["external_action"]:
            reasons.append("external_action_requires_approval")
        if context["missing_controls"]:
            reasons.append("missing_controls")
        if context["risk_score"] >= policy["quality_gates"]["review_min_risk"]:
            reasons.append("risk_above_review_threshold")
        rows.append(
            {
                "decision_id": example["decision_id"],
                "principal": example["principal"],
                "action": example["action"],
                "resource": example["resource"],
                "destination": context["destination"],
                "risk_score": context["risk_score"],
                "missing_controls": context["missing_controls"],
                "decision": decision,
                "expected_decision": example["expected_decision"],
                "matches_expected": decision == example["expected_decision"],
                "reasons": reasons,
            }
        )
    return rows


def evaluate_detectors(samples: list[dict], policy: dict) -> tuple[list[dict], list[dict]]:
    settings = policy["detector_eval"]
    threshold = float(settings["default_threshold"])
    high_recall = set(settings["high_recall_entities"])
    beta = float(settings["beta"])
    by_entity: dict[str, Counter] = defaultdict(Counter)
    sample_rows = []
    for sample in samples:
        gold = Counter(sample.get("gold_entities", []))
        detected = Counter(
            item["type"]
            for item in sample.get("detected_entities", [])
            if float(item.get("confidence", 0)) >= threshold
        )
        entities = sorted(set(gold) | set(detected))
        false_negatives = []
        false_positives = []
        for entity in entities:
            tp = min(gold[entity], detected[entity])
            fn = max(0, gold[entity] - detected[entity])
            fp = max(0, detected[entity] - gold[entity])
            by_entity[entity]["tp"] += tp
            by_entity[entity]["fn"] += fn
            by_entity[entity]["fp"] += fp
            if fn:
                false_negatives.extend([entity] * fn)
            if fp:
                false_positives.extend([entity] * fp)
        sample_rows.append(
            {
                "sample_id": sample["sample_id"],
                "modality": sample["modality"],
                "gold_count": sum(gold.values()),
                "detected_count": sum(detected.values()),
                "false_negatives": "|".join(false_negatives) or "none",
                "false_positives": "|".join(false_positives) or "none",
                "needs_review": bool(set(false_negatives) & high_recall),
            }
        )

    metric_rows = []
    for entity, counts in sorted(by_entity.items()):
        tp = counts["tp"]
        fp = counts["fp"]
        fn = counts["fn"]
        precision = tp / (tp + fp) if tp + fp else 1.0
        recall = tp / (tp + fn) if tp + fn else 1.0
        beta_sq = beta * beta
        f_beta = ((1 + beta_sq) * precision * recall / ((beta_sq * precision) + recall)) if precision + recall else 0.0
        metric_rows.append(
            {
                "entity_type": entity,
                "tp": tp,
                "fp": fp,
                "fn": fn,
                "precision": round(precision, 4),
                "recall": round(recall, 4),
                f"f{beta:g}": round(f_beta, 4),
                "high_recall_entity": entity in high_recall,
                "passes_recall_target": (recall >= settings["minimum_recall_for_high_risk"]) if entity in high_recall else True,
            }
        )
    return metric_rows, sample_rows


def write_policy_report(rows: list[dict]) -> None:
    lines = [
        "# Decisiones de policy-as-code",
        "",
        "Este informe simula las mismas reglas que aparecen como ejemplos en `policies/egress_policy.rego` y `policies/egress_policy.cedar`.",
        "No sustituye a OPA ni Cedar en producción: sirve para entender el input que debe recibir una policy real y qué evidencia conviene guardar.",
        "",
        "| Decisión | Acción | Destino | Riesgo | Resultado | Razones |",
        "|---|---|---|---:|---|---|",
    ]
    for row in rows:
        reasons = ", ".join(row["reasons"]) or "none"
        lines.append(
            f"| `{row['decision_id']}` | `{row['action']}` | `{row['destination']}` | {row['risk_score']} | `{row['decision']}` | {reasons} |"
        )
    lines.extend(
        [
            "",
            "## Lectura",
            "",
            "- La aplicación no pregunta al modelo si puede enviar una captura: evalúa una política externa.",
            "- `deny` bloquea destino, secreto o acción externa sin aprobación.",
            "- `review` mantiene el flujo humano cuando el riesgo o los controles faltantes superan el umbral.",
            "- `allow` solo aparece con destino aprobado, riesgo bajo y controles completos.",
        ]
    )
    (OUTPUT / "policy_decisions.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_detector_report(metric_rows: list[dict], sample_rows: list[dict]) -> None:
    lines = [
        "# Evaluación de detectores multimodales",
        "",
        "Este informe separa dos preguntas que suelen mezclarse: qué entidades debería detectar el sistema y qué entidades detectó por encima del umbral.",
        "",
        "## Métricas por entidad",
        "",
        "| Entidad | TP | FP | FN | Precision | Recall | F2 | Objetivo recall |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in metric_rows:
        lines.append(
            f"| `{row['entity_type']}` | {row['tp']} | {row['fp']} | {row['fn']} | {row['precision']} | {row['recall']} | {row['f2']} | {row['passes_recall_target']} |"
        )
    lines.extend(
        [
            "",
            "## Muestras que necesitan revisión",
            "",
            "| Muestra | Modalidad | Falsos negativos | Falsos positivos | Revisión |",
            "|---|---|---|---|---|",
        ]
    )
    for row in sample_rows:
        if row["needs_review"] or row["false_negatives"] != "none" or row["false_positives"] != "none":
            lines.append(
                f"| `{row['sample_id']}` | `{row['modality']}` | {row['false_negatives']} | {row['false_positives']} | {row['needs_review']} |"
            )
    lines.extend(
        [
            "",
            "## Lectura",
            "",
            "- En PII de alto impacto suele doler más el falso negativo que el falso positivo.",
            "- Si no detectas `GPS_LOCATION`, `HEALTH`, `API_KEY` o `ACCESS_TOKEN_FRAGMENT`, no tienes un problema estético: tienes un posible incidente.",
            "- La métrica útil no vive en abstracto; debe estar separada por entidad, modalidad y tipo de fallo.",
        ]
    )
    (OUTPUT / "detector_eval_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_lineage_jsonl(rows: list[dict]) -> None:
    content = "\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows)
    (OUTPUT / "artifact_lineage.jsonl").write_text(content + "\n", encoding="utf-8")


def write_report(scored: list[dict], summary: dict) -> None:
    lines = [
        "# Informe de privacidad, seguridad y operación multimodal",
        "",
        f"Decisión global: `{summary['global_decision']}`",
        f"Casos: `{summary['case_count']}` · pass `{summary['pass_count']}` · review `{summary['review_count']}` · block `{summary['block_count']}`",
        f"Riesgo medio: `{summary['avg_risk_score']}` · riesgo máximo `{summary['max_risk_score']}`",
        "",
        "## Casos",
        "",
        "| Caso | Modalidad | Riesgo | Decisión | Fallos | Siguiente acción |",
        "|---|---|---:|---|---|---|",
    ]
    for item in scored:
        failures = ", ".join(item["failures"]) or "ninguno"
        lines.append(
            f"| `{item['case_id']}` | {item['modality']} | {item['risk_score']} | `{item['decision']}` | {failures} | {item['next_action']} |"
        )
    lines.extend(["", "## Por modalidad", "", "| Modalidad | Casos | Riesgo medio | Riesgo máximo |", "|---|---:|---:|---:|"])
    for row in summary["modality_rows"]:
        lines.append(f"| `{row['modality']}` | {row['case_count']} | {row['avg_risk_score']} | {row['max_risk_score']} |")
    lines.extend(
        [
            "",
            "## Lectura de ingeniería",
            "",
            "- Imagen, vídeo y pantalla no son solo “archivos”: pueden contener PII, secretos y órdenes visuales.",
            "- Un caso bloqueado no se arregla con prompt: exige redacción, revocación, egress policy o aprobación.",
            "- Si una traza se usa como eval, debe redactarse antes de entrar al dataset.",
            "- Si hay secreto sin redactar, el primer paso es revocar, no discutir métricas.",
        ]
    )
    (OUTPUT / "risk_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_runbook(scored: list[dict]) -> None:
    blockers = [item for item in scored if item["decision"] == "block"]
    lines = [
        "# Runbook de incidente multimodal",
        "",
        "## Cuándo usarlo",
        "",
        "Usa este runbook si una imagen, documento, audio, vídeo, RAG o traza de pantalla contiene PII, secreto, prompt injection visual o salida externa no autorizada.",
        "",
        "## Primeros 30 minutos",
        "",
        "1. Congela la run y conserva `output/risk_report.json`.",
        "2. Identifica modalidad, destino, storage y owner.",
        "3. Si hay API key o secreto, revoca antes de debatir si la salida fue visible.",
        "4. Redacta o elimina artefactos derivados: screenshots, OCR, transcript, frames, logs y eval fixtures.",
        "5. Abre ticket de seguridad con case_id, evidencia y decisión.",
        "",
        "## Casos bloqueados en esta ejecución",
        "",
    ]
    if not blockers:
        lines.append("No hay casos bloqueados.")
    for item in blockers:
        lines.append(f"- `{item['case_id']}`: {item['title']} -> {item['next_action']}")
    lines.extend(
        [
            "",
            "## Cierre",
            "",
            "- Añade un caso de regresión redactado.",
            "- Revisa egress policy y controles faltantes.",
            "- Documenta retención y borrado.",
            "- Si afectó a datos personales, activa revisión de privacidad.",
        ]
    )
    (OUTPUT / "incident_runbook.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_svg(scored: list[dict], summary: dict) -> None:
    width = 1180
    height = 760
    lanes = [
        ("Entrada", "documento · imagen · audio · vídeo · pantalla"),
        ("Clasificación", "PII · secretos · OCR no confiable"),
        ("Controles", "redacción · retención · ACL · egress"),
        ("Gate", "pass · review · block"),
        ("Evidencia", "CSV · runbook · caso de regresión"),
    ]
    lane_svg = []
    for idx, (title, body) in enumerate(lanes):
        x = 66 + idx * 218
        fill = "#FFFFFF" if idx % 2 == 0 else "#F7F7F7"
        lane_svg.append(f'<rect x="{x}" y="150" width="178" height="260" fill="{fill}" stroke="#111111" stroke-width="1.3"/>')
        lane_svg.append(f'<text x="{x + 89}" y="184" text-anchor="middle" font-size="14" font-weight="700" fill="#111111">{escape(title)}</text>')
        parts = body.split(" · ")
        for j, part in enumerate(parts):
            lane_svg.append(f'<text x="{x + 89}" y="{230 + j * 30}" text-anchor="middle" font-size="11" fill="#555555">{escape(part)}</text>')
        if idx < len(lanes) - 1:
            lane_svg.append(f'<line x1="{x + 178}" y1="280" x2="{x + 216}" y2="280" stroke="#111111" stroke-width="1.5" marker-end="url(#f12c11-arrow)"/>')
    bars = []
    top_cases = sorted(scored, key=lambda item: item["risk_score"], reverse=True)[:5]
    for idx, item in enumerate(top_cases):
        y = 494 + idx * 32
        bar = int(520 * item["risk_score"])
        bars.append(f'<text x="96" y="{y + 17}" font-size="11" fill="#111111">{escape(item["case_id"])}</text>')
        bars.append(f'<rect x="330" y="{y}" width="520" height="20" fill="#F3F3F3" stroke="#111111" stroke-width="0.8"/>')
        bars.append(f'<rect x="330" y="{y}" width="{bar}" height="20" fill="#111111"/>')
        bars.append(f'<text x="870" y="{y + 16}" font-size="11" fill="#111111">{item["risk_score"]:.2f} · {escape(item["decision"])}</text>')
    svg = f'''<svg viewBox="0 0 {width} {height}" role="img" aria-labelledby="f12c11-title f12c11-desc" xmlns="http://www.w3.org/2000/svg">
  <title id="f12c11-title">Gate multimodal de privacidad y seguridad</title>
  <desc id="f12c11-desc">Pipeline de clasificación, controles, gate e informe para riesgos multimodales.</desc>
  <defs>
    <marker id="f12c11-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L0,6 L9,3 z" fill="#111111"/>
    </marker>
  </defs>
  <rect width="{width}" height="{height}" fill="#FFFFFF"/>
  <text x="64" y="58" font-size="28" font-weight="700" fill="#111111">Privacidad, seguridad y operación multimodal</text>
  <text x="64" y="88" font-size="15" fill="#555555">La entrada multimodal se clasifica, se redacta, se gobierna por destino y se decide con un gate.</text>
  {''.join(lane_svg)}
  <rect x="64" y="454" width="1052" height="218" fill="#FFFFFF" stroke="#111111" stroke-width="1.2"/>
  <text x="96" y="482" font-size="13" font-weight="700" fill="#111111">Top riesgos de la ejecución</text>
  {''.join(bars)}
  <text x="96" y="704" font-size="13" font-weight="700" fill="#111111">Decisión global</text>
  <text x="224" y="704" font-size="13" fill="#111111">{escape(summary["global_decision"])} · {summary["block_count"]} bloqueos · {summary["review_count"]} revisiones · riesgo medio {summary["avg_risk_score"]}</text>
  <text x="1092" y="728" text-anchor="end" font-size="11" fill="#999999">{SIGNATURE}</text>
</svg>
'''
    (OUTPUT / "multimodal_risk_gate.svg").write_text(svg, encoding="utf-8")


def main() -> None:
    policy = load_json(POLICY_PATH)
    cases = load_json(CASES_PATH)
    detector_eval_samples = load_json(DETECTOR_EVAL_PATH)
    policy_examples = load_json(POLICY_DECISIONS_PATH)
    OUTPUT.mkdir(exist_ok=True)
    (OUTPUT / "case_cards").mkdir(exist_ok=True)

    scored = [score_case(case, policy) for case in cases]
    summary = aggregate(scored)
    redactions = [row for case in cases for row in required_redactions(case, policy)]
    threat_rows = threat_model_rows(cases, scored)
    lineage = lineage_rows(cases, scored, policy)
    policy_decisions = evaluate_policy_decisions(policy_examples, policy)
    detector_metrics, detector_samples = evaluate_detectors(detector_eval_samples, policy)
    retention_rows = [
        {
            "case_id": item["case_id"],
            "storage": item["storage"],
            "retention_days": item["retention_days"],
            "decision": item["decision"],
        }
        for item in scored
    ]

    report = {
        "schema_version": "1.0",
        "project": "IA para gente curiosa",
        "fasciculo": 12,
        "capitulo": 11,
        "summary": summary,
        "cases": scored,
        "threat_model": threat_rows,
        "lineage": lineage,
        "policy_decisions": policy_decisions,
        "detector_metrics": detector_metrics,
        "policy": policy,
    }
    (OUTPUT / "risk_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    for item in scored:
        (OUTPUT / "case_cards" / f"{item['case_id']}.json").write_text(json.dumps(item, indent=2, ensure_ascii=False), encoding="utf-8")
    write_report(scored, summary)
    write_runbook(scored)
    write_csv(
        OUTPUT / "risk_matrix.csv",
        scored,
        ["case_id", "title", "modality", "destination", "storage", "risk_score", "decision", "failures", "missing_controls", "next_action"],
    )
    write_csv(
        OUTPUT / "redaction_plan.csv",
        redactions,
        ["case_id", "entity_type", "operator", "location", "confidence"],
    )
    write_csv(
        OUTPUT / "retention_matrix.csv",
        retention_rows,
        ["case_id", "storage", "retention_days", "decision"],
    )
    write_csv(
        OUTPUT / "threat_model.csv",
        threat_rows,
        ["case_id", "modality", "asset", "trust_boundary", "failure_mode", "control", "test", "decision", "risk_score"],
    )
    write_csv(
        OUTPUT / "artifact_lineage.csv",
        lineage,
        ["artifact_id", "case_id", "artifact_hash", "modality", "surface", "owner", "destination", "storage", "policy_hash", "detector_version", "redaction_operators", "decision", "retention_days"],
    )
    write_csv(
        OUTPUT / "policy_decisions.csv",
        policy_decisions,
        ["decision_id", "principal", "action", "resource", "destination", "risk_score", "missing_controls", "decision", "expected_decision", "matches_expected", "reasons"],
    )
    write_csv(
        OUTPUT / "detector_metrics.csv",
        detector_metrics,
        ["entity_type", "tp", "fp", "fn", "precision", "recall", "f2", "high_recall_entity", "passes_recall_target"],
    )
    write_csv(
        OUTPUT / "detector_samples.csv",
        detector_samples,
        ["sample_id", "modality", "gold_count", "detected_count", "false_negatives", "false_positives", "needs_review"],
    )
    write_lineage_jsonl(lineage)
    write_policy_report(policy_decisions)
    write_detector_report(detector_metrics, detector_samples)
    write_svg(scored, summary)
    print(f"OK: {len(scored)} casos auditados; decisión {summary['global_decision']} en {OUTPUT}")


if __name__ == "__main__":
    main()
