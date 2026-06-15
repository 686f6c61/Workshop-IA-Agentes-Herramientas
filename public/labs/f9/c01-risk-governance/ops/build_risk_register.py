#!/usr/bin/env python3
import argparse
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "risk_scenarios.csv"
SYSTEM_CONTEXT = ROOT / "contracts" / "ai_system_context.json"
CONTROL_POLICY = ROOT / "contracts" / "control_policy.json"
OUTPUT = ROOT / "output"
EVIDENCE_PACK = OUTPUT / "evidence_pack"


def load_json(path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_rows(path):
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def risk_band(score, thresholds):
    if score >= thresholds["alto"]:
        return "critico"
    if score >= thresholds["medio"]:
        return "alto"
    if score >= thresholds["bajo"]:
        return "medio"
    return "bajo"


def split_list(value):
    return [item.strip() for item in value.split(";") if item.strip()]


def enrich(row, policy):
    likelihood = int(row["likelihood"])
    impact = int(row["impact"])
    exposure = int(row["exposure"])
    detectability_gap = int(row["detectability_gap"])
    score = likelihood * impact * exposure * detectability_gap
    band = risk_band(score, policy["risk_thresholds"])
    control_area = row["control_area"]
    catalog_controls = policy["control_catalog"].get(control_area, [])
    existing_controls = split_list(row["existing_controls"])
    missing_controls = [control for control in catalog_controls if control not in existing_controls]
    required_evidence = split_list(row["evidence_required"])

    return {
        **row,
        "likelihood": likelihood,
        "impact": impact,
        "exposure": exposure,
        "detectability_gap": detectability_gap,
        "risk_score": score,
        "risk_band": band,
        "existing_controls": existing_controls,
        "recommended_controls": missing_controls[:4],
        "evidence_required": required_evidence,
        "needs_release_condition": band in {"alto", "critico"},
    }


def decide_release(items, context, policy):
    rules = policy["release_rules"]
    critical = [item for item in items if item["risk_band"] == "critico"]
    high = [item for item in items if item["risk_band"] == "alto"]
    high_without_owner = [item for item in high if not item["owner"]]
    personal_data = any(item["data_class"] in {"tickets_seudonimizados", "trazas_operativas"} for item in items)

    blockers = []
    if len(critical) > rules["max_critical"]:
        blockers.append(f"{len(critical)} escenario(s) critico(s)")
    if len(high_without_owner) > rules["max_high_without_owner"]:
        blockers.append(f"{len(high_without_owner)} escenario(s) alto(s) sin owner")
    if rules["require_privacy_review_when_personal_data"] and personal_data and "privacy_review" not in context["evidence_sources"]:
        blockers.append("falta privacy_review en evidence_sources")

    if blockers:
        decision = rules["decision_if_blocked"]
    elif high:
        decision = "publicar_con_condiciones"
    else:
        decision = "publicar_con_seguimiento"

    return {
        "decision": decision,
        "blockers": blockers,
        "critical_count": len(critical),
        "high_count": len(high),
        "release_stage": context["release_stage"],
        "required_conditions": [
            item for item in items if item["needs_release_condition"]
        ],
    }


def write_json(path, payload):
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def render_register_md(context, items, release):
    lines = [
        f"# Registro de riesgos: {context['name']}",
        "",
        "## Lectura ejecutiva",
        "",
        f"- Sistema: `{context['system_id']}`.",
        f"- Fase: `{release['release_stage']}`.",
        f"- Decisión: `{release['decision']}`.",
        f"- Escenarios críticos: {release['critical_count']}.",
        f"- Escenarios altos: {release['high_count']}.",
        "",
        "## Fórmula usada",
        "",
        "`riesgo = probabilidad x impacto x exposición x hueco_de_detección`",
        "",
        "Cada factor usa escala 1-5. El hueco de detección mide lo difícil que sería ver el problema a tiempo.",
        "",
        "## Escenarios priorizados",
        "",
        "| ID | Área | Banda | Score | Owner | Controles recomendados | Evidencia |",
        "|---|---|---:|---:|---|---|---|",
    ]
    for item in sorted(items, key=lambda row: row["risk_score"], reverse=True):
        lines.append(
            "| {scenario_id} | {area} | {risk_band} | {risk_score} | {owner} | {controls} | {evidence} |".format(
                scenario_id=item["scenario_id"],
                area=item["area"],
                risk_band=item["risk_band"],
                risk_score=item["risk_score"],
                owner=item["owner"],
                controls=", ".join(item["recommended_controls"]) or "sin huecos principales",
                evidence=", ".join(item["evidence_required"]),
            )
        )

    lines.extend([
        "",
        "## Bloqueos y condiciones",
        "",
    ])
    if release["blockers"]:
        for blocker in release["blockers"]:
            lines.append(f"- {blocker}")
    else:
        lines.append("- No hay bloqueos absolutos según la política actual.")

    lines.extend([
        "",
        "## Siguiente revisión",
        "",
        "Revisar owners, evidencias y controles antes de subir de fase. Si cambia el corpus, el modelo, las tools o la finalidad, volver a ejecutar este kit.",
        "",
    ])
    return "\n".join(lines)


def render_release_gate(context, release):
    lines = [
        f"# Gate de salida: {context['name']}",
        "",
        f"Decisión: `{release['decision']}`",
        "",
        "## Condiciones obligatorias",
        "",
    ]
    if release["required_conditions"]:
        for item in release["required_conditions"]:
            controls = ", ".join(item["recommended_controls"][:3]) or "mantener controles existentes"
            evidence = ", ".join(item["evidence_required"])
            lines.append(
                f"- `{item['scenario_id']}` ({item['risk_band']}): owner `{item['owner']}`, controles `{controls}`, evidencia `{evidence}`."
            )
    else:
        lines.append("- Mantener seguimiento normal y conservar trazas de muestra.")

    lines.extend([
        "",
        "## Criterio de aceptación",
        "",
        "Una versión puede avanzar si no quedan escenarios críticos abiertos, todo escenario alto tiene owner y cada condición tiene evidencia revisable.",
        "",
        "## Cómo explicarlo",
        "",
        "No estamos buscando certeza absoluta. Estamos dejando claro qué puede salir mal, quién lo mira, qué control lo reduce y qué prueba demuestra que no estamos improvisando.",
        "",
    ])
    return "\n".join(lines)


def build_release_manifest(context, release):
    return {
        "system_id": context["system_id"],
        "name": context["name"],
        "release_stage": context["release_stage"],
        "decision": release["decision"],
        "versioned_components": {
            "model_id": "provider-model@2026-06-07",
            "prompt_version": "academic-assistant-system-prompt@0.4.2",
            "rag_index_version": "normativa-académica-index@2026-06-07",
            "tool_policy_version": "ticket-tools-policy@0.3.0",
            "risk_policy_version": "control_policy@0.1.0",
            "evaluation_set": "rag-governance-smoke@0.2.0"
        },
        "required_evidence": context["evidence_sources"],
        "owners": {
            "technical_owner": context["owner"],
            "human_review_owner": context["human_review"]["owner"],
            "privacy_owner": "owner-privacy",
            "governance_owner": "owner-governance"
        }
    }


def render_evidence_index(context, policy, items, release):
    framework_map = policy.get("framework_artifact_map", {})
    lines = [
        f"# Índice de evidencias: {context['name']}",
        "",
        "Este índice no demuestra cumplimiento legal por sí solo. Sirve para que ingeniería, privacidad, producto y operación sepan qué mirar antes de cambiar de fase.",
        "",
        "## Decisión",
        "",
        f"- Fase revisada: `{context['release_stage']}`.",
        f"- Decisión: `{release['decision']}`.",
        f"- Escenarios altos: {release['high_count']}.",
        "",
        "## Marcos y artefactos",
        "",
        "| Marco o función | Artefactos que debe enseñar el equipo |",
        "|---|---|",
    ]
    for framework, artifacts in framework_map.items():
        lines.append(f"| `{framework}` | {', '.join(f'`{artifact}`' for artifact in artifacts)} |")

    lines.extend([
        "",
        "## Evidencias por escenario alto",
        "",
        "| ID | Owner | Evidencias mínimas |",
        "|---|---|---|",
    ])
    for item in sorted(items, key=lambda row: row["risk_score"], reverse=True):
        if item["risk_band"] in {"alto", "critico"}:
            lines.append(f"| `{item['scenario_id']}` | `{item['owner']}` | {', '.join(f'`{e}`' for e in item['evidence_required'])} |")

    lines.extend([
        "",
        "## Huecos que no aceptaría sin explicación",
        "",
        "- Un escenario alto sin owner.",
        "- Un control declarado sin evidencia ejecutable o revisable.",
        "- Una tool con efecto externo sin traza de aprobación.",
        "- Un RAG sin manifest de índice y sin casos de abstención.",
        "- Logs o memoria sin política de retención.",
        "",
    ])
    return "\n".join(lines)


def render_trace_sample(context):
    trace = {
        "trace_id": "trace-demo-f9-c01-001",
        "system_id": context["system_id"],
        "release_stage": context["release_stage"],
        "request_class": "consulta_normativa",
        "model_id": "provider-model@2026-06-07",
        "prompt_version": "academic-assistant-system-prompt@0.4.2",
        "rag_index_version": "normativa-académica-index@2026-06-07",
        "retrieved_sources": [
            {"source_id": "normativa-matricula-2026", "versión": "2026-06-01", "trust_level": "alta"},
            {"source_id": "faq-becas-2025", "versión": "2025-09-15", "trust_level": "media"}
        ],
        "tool_calls": [
            {"tool": "create_ticket", "mode": "readiness_demo", "approval_required": True, "executed": False}
        ],
        "privacy": {
            "raw_user_text_stored": False,
            "pseudonymous_user_id": "user_hash_demo",
            "retention_days": 30
        },
        "decision": "abstener_o_derivar_si_no_hay_fuente_actual",
        "output_contract_ok": True
    }
    return json.dumps(trace, ensure_ascii=False) + "\n"


def render_privacy_review(context):
    data_classes = ", ".join(f"`{item}`" for item in context["data_classes"])
    lines = [
        f"# Revisión inicial de privacidad: {context['name']}",
        "",
        "Esta revisión es deliberadamente mínima. Su función es abrir preguntas técnicas antes de hacer una DPIA completa cuando aplique.",
        "",
        "## Datos tratados",
        "",
        f"- Clases declaradas: {data_classes}.",
        "- La práctica asume seudonimización para tickets y trazas.",
        "- La práctica no conserva texto bruto de usuario en la traza de muestra.",
        "",
        "## Preguntas obligatorias",
        "",
        "1. ¿Qué dato personal entra en prompt, RAG, memoria, logs y proveedor?",
        "2. ¿Qué dato se conserva y durante cuánto tiempo?",
        "3. ¿Qué dato se puede borrar sin romper observabilidad?",
        "4. ¿Qué finalidad justifica cada dato?",
        "5. ¿Qué owner revisa excepciones?",
        "",
        "## Decisión provisional",
        "",
        "No subiría de fase sin revisar retención, seudonimización, muestreo de trazas y rutas de borrado.",
        "",
    ]
    return "\n".join(lines)


def write_control_matrix(path, items):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "scenario_id",
                "area",
                "risk_band",
                "risk_score",
                "owner",
                "recommended_controls",
                "evidence_required",
            ],
        )
        writer.writeheader()
        for item in sorted(items, key=lambda row: row["risk_score"], reverse=True):
            writer.writerow({
                "scenario_id": item["scenario_id"],
                "area": item["area"],
                "risk_band": item["risk_band"],
                "risk_score": item["risk_score"],
                "owner": item["owner"],
                "recommended_controls": ";".join(item["recommended_controls"]),
                "evidence_required": ";".join(item["evidence_required"]),
            })


def main():
    parser = argparse.ArgumentParser(description="Construye un registro de riesgos de IA con controles y evidencias.")
    parser.add_argument("--write", action="store_true", help="Escribe los artefactos en output/.")
    args = parser.parse_args()

    context = load_json(SYSTEM_CONTEXT)
    policy = load_json(CONTROL_POLICY)
    items = [enrich(row, policy) for row in load_rows(DATA)]
    release = decide_release(items, context, policy)

    payload = {
        "system": context,
        "policy": policy,
        "risk_register": sorted(items, key=lambda row: row["risk_score"], reverse=True),
        "release_gate": release,
    }

    if args.write:
        OUTPUT.mkdir(parents=True, exist_ok=True)
        EVIDENCE_PACK.mkdir(parents=True, exist_ok=True)
        write_json(OUTPUT / "risk_register.json", payload)
        (OUTPUT / "risk_register.md").write_text(render_register_md(context, items, release), encoding="utf-8")
        (OUTPUT / "release_gate.md").write_text(render_release_gate(context, release), encoding="utf-8")
        write_control_matrix(OUTPUT / "control_matrix.csv", items)
        write_json(EVIDENCE_PACK / "release_manifest.json", build_release_manifest(context, release))
        (EVIDENCE_PACK / "evidence_index.md").write_text(render_evidence_index(context, policy, items, release), encoding="utf-8")
        (EVIDENCE_PACK / "trace_sample.jsonl").write_text(render_trace_sample(context), encoding="utf-8")
        (EVIDENCE_PACK / "privacy_review.md").write_text(render_privacy_review(context), encoding="utf-8")

    print(f"escenarios: {len(items)}")
    print(f"criticos: {release['critical_count']}")
    print(f"altos: {release['high_count']}")
    print(f"decision: {release['decision']}")


if __name__ == "__main__":
    main()
