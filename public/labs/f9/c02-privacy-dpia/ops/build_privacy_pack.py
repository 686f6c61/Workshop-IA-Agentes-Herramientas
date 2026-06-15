#!/usr/bin/env python3
import argparse
import csv
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "contracts" / "privacy_policy.json"
FLOWS = ROOT / "data" / "data_flows.csv"
TRACES = ROOT / "data" / "sample_traces.jsonl"
OUTPUT = ROOT / "output"

EMAIL_RE = re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(?:(?:\+34\s*)?)\b(?:\d[\s-]?){9}\b")
DNI_RE = re.compile(r"\b\d{8}[A-Z]\b")

PII_ENTITY_RULES = [
    {
        "entity_type": "EMAIL_ADDRESS",
        "recognizer": "EmailRecognizer",
        "pattern_name": "email_format",
        "regex": EMAIL_RE,
        "base_score": 0.94,
        "context_words": {"correo", "email", "mail", "user_email"},
        "operator": "hash",
        "store_in_trace": False,
    },
    {
        "entity_type": "PHONE_NUMBER",
        "recognizer": "PhoneRecognizer",
        "pattern_name": "spanish_phone_format",
        "regex": PHONE_RE,
        "base_score": 0.82,
        "context_words": {"telefono", "teléfono", "phone", "movil", "móvil"},
        "operator": "redact",
        "store_in_trace": False,
    },
    {
        "entity_type": "NATIONAL_ID",
        "recognizer": "DniRecognizer",
        "pattern_name": "dni_format",
        "regex": DNI_RE,
        "base_score": 0.9,
        "context_words": {"dni", "nie", "documento", "identificador"},
        "operator": "redact",
        "store_in_trace": False,
    },
]


def load_json(path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_csv(path):
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def load_jsonl(path):
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def split_items(value):
    return [item.strip() for item in value.split(";") if item.strip()]


def as_bool(value):
    return str(value).strip().lower() in {"true", "1", "yes", "si", "sí"}


def retention_factor(days):
    days = int(days)
    if days <= 7:
        return 1
    if days <= 30:
        return 2
    if days <= 90:
        return 3
    if days <= 365:
        return 4
    return 5


def sensitivity_factor(row, items):
    if as_bool(row["special_category"]):
        return 5
    personal_markers = {"email", "phone", "question_text", "answer_text", "student_status"}
    if personal_markers.intersection(items):
        return 4
    if row["memory_type"] in {"memoria_usuario", "traza_operativa"}:
        return 3
    return 2


def exposure_factor(row):
    flags = [
        as_bool(row["stores_raw_text"]),
        as_bool(row["large_scale"]),
        as_bool(row["cross_border"]),
        as_bool(row["third_party"]),
        as_bool(row["model_training"]),
        row["memory_type"] in {"memoria_usuario", "corpus_rag", "traza_operativa"},
    ]
    return min(5, 1 + sum(1 for flag in flags if flag))


def detectability_gap(row):
    evidence = split_items(row["evidence"])
    gap = 2
    if as_bool(row["stores_raw_text"]):
        gap += 1
    if as_bool(row["third_party"]):
        gap += 1
    if not evidence:
        gap += 1
    return min(5, gap)


def risk_band(score, thresholds):
    if score >= thresholds["alto"]:
        return "alto"
    if score >= thresholds["medio"]:
        return "medio"
    if score >= thresholds["bajo"]:
        return "bajo"
    return "mínimo"


def minimization(flow, policy):
    items = split_items(flow["data_items"])
    allowed = set(policy["purpose_allowlist"].get(flow["purpose"], []))
    keep = [item for item in items if item in allowed]
    review = [item for item in items if item not in allowed]
    transformations = []
    for item in review:
        if item in {"email", "phone", "dni", "question_text", "answer_text"}:
            transformations.append({"field": item, "action": "redactar_o_sustituir_por_hash"})
        else:
            transformations.append({"field": item, "action": "justificar_o_eliminar"})
    return {
        "allowed_fields": keep,
        "fields_to_review": review,
        "transformations": transformations,
        "minimization_ratio": round(len(keep) / max(1, len(items)), 3),
    }


def dpia_triggers(flow, policy):
    triggers = []
    if as_bool(flow["special_category"]):
        triggers.append("special_category")
    if as_bool(flow["automated_decision"]):
        triggers.append("automated_decision")
    if as_bool(flow["large_scale"]):
        triggers.append("large_scale")
    if as_bool(flow["cross_border"]) and as_bool(flow["third_party"]):
        triggers.append("cross_border_third_party")
    if as_bool(flow["model_training"]) and sensitivity_factor(flow, split_items(flow["data_items"])) >= 4:
        triggers.append("model_training_personal_data")
    if as_bool(flow["stores_raw_text"]) and int(flow["retention_days"]) > policy["release_rules"]["block_if_raw_text_over_days"]:
        triggers.append("long_retention_raw_text")
    return triggers


def enrich_flow(flow, policy):
    items = split_items(flow["data_items"])
    c = sensitivity_factor(flow, items)
    e = exposure_factor(flow)
    t = retention_factor(flow["retention_days"])
    d = detectability_gap(flow)
    score = c * e * t * d
    mini = minimization(flow, policy)
    triggers = dpia_triggers(flow, policy)
    return {
        **flow,
        "data_items": items,
        "stores_raw_text": as_bool(flow["stores_raw_text"]),
        "special_category": as_bool(flow["special_category"]),
        "automated_decision": as_bool(flow["automated_decision"]),
        "large_scale": as_bool(flow["large_scale"]),
        "cross_border": as_bool(flow["cross_border"]),
        "model_training": as_bool(flow["model_training"]),
        "third_party": as_bool(flow["third_party"]),
        "retention_days": int(flow["retention_days"]),
        "privacy_factors": {
            "criticality": c,
            "exposure": e,
            "retention": t,
            "detectability_gap": d,
        },
        "privacy_score": score,
        "privacy_band": risk_band(score, policy["risk_thresholds"]),
        "minimization": mini,
        "dpia_triggers": triggers,
        "needs_dpia_precheck": bool(triggers),
        "evidence": split_items(flow["evidence"]),
    }


def hash_value(value):
    if not value:
        return ""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def context_hit(text, field_name, start, end, context_words):
    lowered = text.lower()
    field_context = field_name.lower()
    window_start = max(0, start - 40)
    window_end = min(len(text), end + 40)
    window = lowered[window_start:window_end]
    for word in context_words:
        if word in field_context or word in window:
            return word
    return ""


def analyze_text_presidio_style(text, field_name):
    findings = []
    for rule in PII_ENTITY_RULES:
        for match in rule["regex"].finditer(text):
            raw_value = match.group(0)
            supportive_context = context_hit(
                text,
                field_name,
                match.start(),
                match.end(),
                rule["context_words"],
            )
            context_boost = 0.04 if supportive_context else 0
            score = min(0.99, rule["base_score"] + context_boost)
            findings.append({
                "field": field_name,
                "entity_type": rule["entity_type"],
                "start": match.start(),
                "end": match.end(),
                "score": round(score, 3),
                "recognizer": rule["recognizer"],
                "pattern_name": rule["pattern_name"],
                "value_hash": hash_value(raw_value),
                "decision_process": {
                    "original_score": rule["base_score"],
                    "score_after_context": round(score, 3),
                    "supportive_context_word": supportive_context,
                },
                "operator": rule["operator"],
                "store_in_trace": rule["store_in_trace"],
                "send_to_model": "solo_si_finalidad_lo_exige",
            })
    findings.sort(key=lambda item: (item["field"], item["start"], -item["score"]))
    return findings


def build_presidio_style_findings(traces):
    analyzed_fields = ["user_text", "user_email", "phone"]
    findings = []
    for trace in traces:
        for field in analyzed_fields:
            value = trace.get(field)
            if not value:
                continue
            for finding in analyze_text_presidio_style(str(value), field):
                findings.append({
                    "trace_id": trace["trace_id"],
                    **finding,
                })
    return {
        "engine_profile": {
            "name": "presidio_style_demo",
            "language": "es",
            "note": "Simulación sin dependencias externas. En producción sustituir por Microsoft Presidio Analyzer y Anonymizer.",
            "entities": [rule["entity_type"] for rule in PII_ENTITY_RULES],
        },
        "findings": findings,
    }


def render_presidio_detection_report(presidio_pack):
    findings = presidio_pack["findings"]
    counts = {}
    for item in findings:
        counts[item["entity_type"]] = counts.get(item["entity_type"], 0) + 1

    lines = [
        "# Informe técnico de detección PII estilo Presidio",
        "",
        "Este informe no conserva valores literales. Guarda entidad, campo, span, score, reconocedor, hash del valor y operador recomendado. La forma se parece a Presidio, pero el kit usa una simulación local sin dependencias para que pueda ejecutarse en cualquier máquina.",
        "",
        "## Perfil de motor",
        "",
        f"- Motor: `{presidio_pack['engine_profile']['name']}`",
        f"- Idioma: `{presidio_pack['engine_profile']['language']}`",
        f"- Entidades activas: {', '.join('`' + item + '`' for item in presidio_pack['engine_profile']['entities'])}",
        "",
        "## Hallazgos por entidad",
        "",
        "| Entidad | Hallazgos | Operador recomendado |",
        "|---|---:|---|",
    ]
    operator_by_entity = {rule["entity_type"]: rule["operator"] for rule in PII_ENTITY_RULES}
    for entity_type in sorted(counts):
        lines.append(f"| `{entity_type}` | {counts[entity_type]} | `{operator_by_entity[entity_type]}` |")
    if not findings:
        lines.append("| sin hallazgos | 0 | revisar corpus de prueba |")

    lines.extend([
        "",
        "## Muestra revisable",
        "",
        "| Trace | Campo | Entidad | Span | Score | Reconocedor | Contexto | Operador | Guardar en traza |",
        "|---|---|---|---:|---:|---|---|---|---|",
    ])
    for item in findings:
        context = item["decision_process"]["supportive_context_word"] or "-"
        lines.append(
            f"| `{item['trace_id']}` | `{item['field']}` | `{item['entity_type']}` | {item['start']}-{item['end']} | {item['score']} | `{item['recognizer']}` | `{context}` | `{item['operator']}` | `{str(item['store_in_trace']).lower()}` |"
        )

    lines.extend([
        "",
        "## Cómo convertirlo en Presidio real",
        "",
        "1. Sustituye está simulación por `AnalyzerEngine(language='es')` y reconocedores propios para DNI/NIE, expediente, matrícula o identificadores internos.",
        "2. Define umbrales por entidad y finalidad. No uses el mismo score para email, teléfono, persona y expediente.",
        "3. Pasa contexto técnico al análisis: nombre de campo, origen, finalidad, idioma y tipo de flujo.",
        "4. Aplica `AnonymizerEngine` con operadores por entidad: `hash`, `redact`, `replace`, `mask`, `encrypt` o `custom`.",
        "5. Evalúa con un dataset etiquetado y mide TP, FP, FN, precisión, recall y F2 antes de publicar.",
        "",
        "## Criterio de aceptación",
        "",
        "- Ningún valor literal detectado debe quedar en logs o trazas si no existe una finalidad escrita.",
        "- Todo hallazgo debe conservar score, reconocedor y operador aplicado para poder revisar la decisión.",
        "- Un falso negativo en una entidad crítica debe crear tarea de ingeniería: nuevo reconocedor, mejor contexto o umbral revisado.",
        "",
    ])
    return "\n".join(lines)


def redact_text(value):
    value = EMAIL_RE.sub("[email_redactado]", value)
    value = PHONE_RE.sub("[telefono_redactado]", value)
    value = DNI_RE.sub("[id_redactado]", value)
    return value


def redact_trace(trace):
    redacted = dict(trace)
    if "user_text" in redacted:
        redacted["user_text"] = redact_text(redacted["user_text"])
    if "user_email" in redacted:
        redacted["user_email_hash"] = hash_value(redacted.get("user_email", ""))
        redacted.pop("user_email", None)
    if "phone" in redacted:
        redacted["phone_present"] = bool(redacted.get("phone"))
        redacted.pop("phone", None)
    redacted["redaction_status"] = "applied"
    return redacted


def decide_release(flows, policy):
    blockers = []
    rules = policy["release_rules"]
    high_without_owner = [flow for flow in flows if flow["privacy_band"] == "alto" and not flow["owner"]]
    raw_over_limit = [
        flow for flow in flows
        if flow["stores_raw_text"] and flow["retention_days"] > rules["block_if_raw_text_over_days"]
    ]
    training_personal = [
        flow for flow in flows
        if flow["model_training"] and sensitivity_factor(flow, flow["data_items"]) >= 4
    ]
    if rules["block_if_high_without_owner"] and high_without_owner:
        blockers.append("hay flujos altos sin owner")
    if raw_over_limit:
        blockers.append("hay texto bruto retenido por encima del límite")
    if rules["block_if_training_personal_data"] and training_personal:
        blockers.append("hay uso de datos personales para entrenamiento sin decisión específica")
    if any(flow["needs_dpia_precheck"] for flow in flows) and rules["require_dpia_note_when_triggered"]:
        blockers.append("hay señales que exigen prechequeo EIPD/DPIA documentado")
    if blockers:
        decision = "revisar_antes_de_publicar"
    elif any(flow["privacy_band"] == "alto" for flow in flows):
        decision = "publicar_con_condiciones"
    else:
        decision = "publicar_con_seguimiento"
    return {
        "decision": decision,
        "blockers": blockers,
        "high_flows": [flow["flow_id"] for flow in flows if flow["privacy_band"] == "alto"],
        "dpia_flows": [flow["flow_id"] for flow in flows if flow["needs_dpia_precheck"]],
    }


def render_data_flow_map(flows):
    lines = [
        "# Mapa de flujos de datos personales",
        "",
        "Este mapa no sustituye una revisión legal. Sirve para que el equipo técnico vea qué dato entra, dónde se guarda, para qué finalidad se usa y qué evidencia debería existir.",
        "",
        "| Flujo | Origen -> destino | Finalidad | Memoria | Retención | Banda | Owner |",
        "|---|---|---|---|---:|---|---|",
    ]
    for flow in flows:
        lines.append(
            f"| `{flow['flow_id']}` {flow['name']} | `{flow['source']}` -> `{flow['destination']}` | `{flow['purpose']}` | `{flow['memory_type']}` | {flow['retention_days']} días | {flow['privacy_band']} | `{flow['owner']}` |"
        )
    lines.append("")
    return "\n".join(lines)


def render_minimization_report(flows):
    lines = [
        "# Informe de minimización",
        "",
        "Minimizar no significa borrar al azar. Significa conservar solo los campos necesarios para la finalidad declarada, transformar lo que pueda exponerse menos y justificar lo que deba permanecer.",
        "",
        "| Flujo | Campos permitidos | Revisar o transformar | Ratio |",
        "|---|---|---|---:|",
    ]
    for flow in flows:
        mini = flow["minimization"]
        review = ", ".join(item["field"] + ":" + item["action"] for item in mini["transformations"]) or "sin cambios principales"
        lines.append(
            f"| `{flow['flow_id']}` | {', '.join(mini['allowed_fields']) or 'ninguno'} | {review} | {mini['minimization_ratio']} |"
        )
    lines.extend([
        "",
        "## Criterio de aceptación",
        "",
        "- Cualquier campo fuera de la allowlist debe eliminarse, redactarse, agregarse o justificarse.",
        "- Si un campo aparece solo para depuración, debe tener TTL, owner y muestra de traza revisada.",
        "- La memoria de usuario necesita consentimiento, fecha de expiración y ruta de borrado.",
        "",
    ])
    return "\n".join(lines)


def render_dpia_precheck(flows, policy):
    descriptions = policy["dpia_triggers"]
    lines = [
        "# Prechequeo EIPD/DPIA",
        "",
        "Una EIPD/DPIA es una evaluación previa cuando un tratamiento puede implicar alto riesgo para derechos y libertades. Este prechequeo no decide por la organización: detecta señales que justifican una revisión formal.",
        "",
        "| Flujo | Señales detectadas | Lectura técnica |",
        "|---|---|---|",
    ]
    for flow in flows:
        if flow["dpia_triggers"]:
            labels = ", ".join(f"`{trigger}`" for trigger in flow["dpia_triggers"])
            explanation = " ".join(descriptions[trigger] for trigger in flow["dpia_triggers"])
            lines.append(f"| `{flow['flow_id']}` | {labels} | {explanation} |")
    if not any(flow["dpia_triggers"] for flow in flows):
        lines.append("| sin señales | Ninguna | Mantener revisión periódica. |")
    lines.extend([
        "",
        "## Qué documentaría antes de publicar",
        "",
        "1. Naturaleza, alcance, contexto y fines del tratamiento.",
        "2. Categorías de datos y personas afectadas.",
        "3. Flujos hacia proveedores, tools, memoria, logs y backups.",
        "4. Medidas de minimización, seudonimización, cifrado, retención y borrado.",
        "5. Cómo se atienden acceso, rectificación, supresión, oposición y limitación.",
        "6. Riesgo residual y owner que acepta o bloquea el uso.",
        "",
    ])
    return "\n".join(lines)


def render_release_gate(flows, release, policy):
    lines = [
        "# Gate de privacidad",
        "",
        f"Decisión: `{release['decision']}`",
        "",
        "## Bloqueos",
        "",
    ]
    if release["blockers"]:
        lines.extend(f"- {blocker}" for blocker in release["blockers"])
    else:
        lines.append("- No hay bloqueos según la política actual.")
    lines.extend([
        "",
        "## Condiciones por flujo",
        "",
        "| Flujo | Banda | Condición mínima |",
        "|---|---|---|",
    ])
    for flow in flows:
        if flow["privacy_band"] == "alto" or flow["needs_dpia_precheck"]:
            evidence = ", ".join(f"`{item}`" for item in flow["evidence"])
            lines.append(f"| `{flow['flow_id']}` | {flow['privacy_band']} | Revisar `{flow['owner']}` y conservar evidencias: {evidence}. |")
    lines.extend([
        "",
        "## Evidencias obligatorias",
        "",
    ])
    lines.extend(f"- `{item}`" for item in policy["required_evidence"])
    lines.append("")
    return "\n".join(lines)


def write_outputs(flows, traces, policy, release):
    OUTPUT.mkdir(parents=True, exist_ok=True)
    presidio_pack = build_presidio_style_findings(traces)
    (OUTPUT / "data_flow_inventory.json").write_text(
        json.dumps({"flows": flows, "release": release}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (OUTPUT / "data_flow_map.md").write_text(render_data_flow_map(flows), encoding="utf-8")
    (OUTPUT / "minimization_report.md").write_text(render_minimization_report(flows), encoding="utf-8")
    (OUTPUT / "dpia_precheck.md").write_text(render_dpia_precheck(flows, policy), encoding="utf-8")
    (OUTPUT / "privacy_release_gate.md").write_text(render_release_gate(flows, release, policy), encoding="utf-8")

    with (OUTPUT / "retention_plan.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["flow_id", "memory_type", "retention_days", "default_days", "owner", "action"])
        writer.writeheader()
        for flow in flows:
            default_days = policy["retention_defaults_days"].get(flow["memory_type"], flow["retention_days"])
            action = "reducir" if flow["retention_days"] > default_days else "mantener"
            writer.writerow({
                "flow_id": flow["flow_id"],
                "memory_type": flow["memory_type"],
                "retention_days": flow["retention_days"],
                "default_days": default_days,
                "owner": flow["owner"],
                "action": action,
            })

    with (OUTPUT / "redacted_trace_sample.jsonl").open("w", encoding="utf-8") as handle:
        for trace in traces:
            handle.write(json.dumps(redact_trace(trace), ensure_ascii=False) + "\n")

    (OUTPUT / "presidio_style_findings.json").write_text(
        json.dumps(presidio_pack, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (OUTPUT / "presidio_detection_report.md").write_text(
        render_presidio_detection_report(presidio_pack),
        encoding="utf-8",
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="escribe los artefactos en output/")
    args = parser.parse_args()

    policy = load_json(POLICY)
    flows = [enrich_flow(row, policy) for row in load_csv(FLOWS)]
    traces = load_jsonl(TRACES)
    release = decide_release(flows, policy)

    if args.write:
        write_outputs(flows, traces, policy, release)

    print(f"flujos: {len(flows)}")
    print(f"altos: {len(release['high_flows'])}")
    print(f"prechequeo_dpia: {len(release['dpia_flows'])}")
    print(f"decision: {release['decision']}")


if __name__ == "__main__":
    main()
