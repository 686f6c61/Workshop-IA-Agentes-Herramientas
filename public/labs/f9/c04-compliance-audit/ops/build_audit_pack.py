#!/usr/bin/env python3
import argparse
import csv
import hashlib
import json
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "contracts" / "compliance_policy.json"
SYSTEMS = ROOT / "data" / "ai_systems.csv"
EVIDENCE = ROOT / "data" / "evidence_catalog.csv"
PROVIDERS = ROOT / "data" / "providers.csv"
OUTPUT = ROOT / "output"


def load_json(path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_csv(path):
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_json(path, payload):
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_csv(path, rows, fieldnames):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def file_sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def split_items(value):
    return [item.strip() for item in str(value or "").split(";") if item.strip()]


def as_bool(value):
    return str(value or "").strip().lower() in {"true", "1", "yes", "si", "sí"}


def parse_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def age_days(reviewed_on, assessment_date):
    parsed = parse_date(reviewed_on)
    if not parsed:
        return None
    return (assessment_date - parsed).days


def build_recordkeeping_schema(policy):
    retention_until = (parse_date(policy["assessment_date"]) + timedelta(days=180)).isoformat()
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "F9 C04 compliance record-keeping event",
        "type": "object",
        "additionalProperties": False,
        "required": [
            "event_id",
            "event_type",
            "timestamp",
            "system_id",
            "policy_version",
            "model_id",
            "prompt_version",
            "rag_index_version",
            "tool_policy_version",
            "classification",
            "decision",
            "blockers",
            "conditions",
            "personal_data_stored",
            "retention_until"
        ],
        "properties": {
            "event_id": {"type": "string", "pattern": "^f9c04_trace_[0-9]{3,}$"},
            "event_type": {"type": "string", "enum": ["compliance_gate_evaluated"]},
            "timestamp": {"type": "string", "format": "date-time"},
            "system_id": {"type": "string"},
            "policy_version": {"type": "string"},
            "model_id": {"type": "string"},
            "prompt_version": {"type": "string"},
            "rag_index_version": {"type": "string"},
            "tool_policy_version": {"type": "string"},
            "classification": {"type": "string"},
            "decision": {
                "type": "string",
                "enum": [
                    "publicar_con_seguimiento",
                    "publicar_con_condiciones",
                    "revisar_antes"
                ]
            },
            "blockers": {"type": "array", "items": {"type": "string"}},
            "conditions": {"type": "array", "items": {"type": "string"}},
            "personal_data_stored": {"type": "boolean"},
            "retention_until": {"type": "string", "format": "date"}
        },
        "example_retention_until": retention_until
    }


def infer_classification(system, policy):
    domain = system["domain"]
    effects = set(split_items(system["effect"]))
    high_domains = set(policy["classification"]["high_impact_domains"])
    high_effects = set(policy["classification"]["high_impact_effects"])
    transparency_effects = set(policy["classification"]["transparency_effects"])

    if domain in high_domains and effects.intersection(high_effects):
        return {
            "classification": "alto_riesgo_posible",
            "rationale": "dominio de impacto alto con efecto que prioriza, ordena o influye en una decisión relevante",
        }
    if effects.intersection(transparency_effects) or as_bool(system["personal_data"]):
        return {
            "classification": "gobernanza_y_transparencia",
            "rationale": "uso con personas, contenido o datos que exige límites, instrucciones, trazas y revisión",
        }
    return {
        "classification": "gobernanza_interna",
        "rationale": "uso interno sin datos personales declarados ni efecto directo sobre acceso o derechos",
    }


def requirement_applies(requirement, system, classification):
    applies_to = requirement["applies_to"]
    high_risk = classification["classification"] == "alto_riesgo_posible"
    if applies_to == "all":
        return True
    if applies_to == "personal_data":
        return as_bool(system["personal_data"])
    if applies_to == "production":
        return system["production_stage"] == "production" or high_risk
    if applies_to == "high_risk_candidate":
        return high_risk
    if applies_to == "provider_high_risk":
        return high_risk and as_bool(system["role_provider"])
    if applies_to == "high_risk_deployer":
        return high_risk and as_bool(system["role_deployer"])
    return False


def evidence_index(rows):
    index = {}
    for row in rows:
        index[(row["system_id"], row["requirement_id"])] = row
    return index


def effective_status(evidence, policy, assessment_date):
    if not evidence:
        return "missing"
    status = evidence["status"]
    reviewed_age = age_days(evidence["reviewed_on"], assessment_date)
    if status == "accepted" and reviewed_age is not None and reviewed_age > policy["release_rules"]["stale_after_days"]:
        return "stale"
    return status


def evaluate(policy, systems, evidence_rows):
    assessment_date = parse_date(policy["assessment_date"]) or date.today()
    index = evidence_index(evidence_rows)
    requirements = policy["requirements"]
    register = []
    crosswalk = []
    decisions = {}

    for system in systems:
        classification = infer_classification(system, policy)
        register.append({
            **system,
            "role_provider": str(as_bool(system["role_provider"])).lower(),
            "role_deployer": str(as_bool(system["role_deployer"])).lower(),
            "personal_data": str(as_bool(system["personal_data"])).lower(),
            "special_category": str(as_bool(system["special_category"])).lower(),
            "initial_classification": classification["classification"],
            "classification_rationale": classification["rationale"],
        })

        blockers = []
        conditions = []
        closed = 0

        for requirement in requirements:
            if not requirement_applies(requirement, system, classification):
                continue
            evidence = index.get((system["system_id"], requirement["id"]))
            status = effective_status(evidence, policy, assessment_date)
            if status == "accepted":
                gate_status = "cerrado"
                closed += 1
            elif status in policy["release_rules"]["condition_statuses"]:
                gate_status = "condición"
                conditions.append(requirement["id"])
            elif requirement["blocker_if_missing"]:
                gate_status = "bloqueante"
                blockers.append(requirement["id"])
            else:
                gate_status = "condición"
                conditions.append(requirement["id"])

            crosswalk.append({
                "system_id": system["system_id"],
                "system_name": system["name"],
                "initial_classification": classification["classification"],
                "framework": requirement["framework"],
                "requirement_id": requirement["id"],
                "requirement_label": requirement["label"],
                "question": requirement["question"],
                "expected_artifact": requirement["artifact"],
                "evidence_path": evidence["path"] if evidence else "",
                "evidence_owner": evidence["owner"] if evidence else requirement["owner_role"],
                "evidence_version": evidence["version"] if evidence else "",
                "reviewed_on": evidence["reviewed_on"] if evidence else "",
                "evidence_status": status,
                "gate_status": gate_status,
                "notes": evidence["notes"] if evidence else "sin evidencia registrada",
            })

        if blockers:
            decision = policy["release_rules"]["decision_if_blocked"]
        elif conditions:
            decision = policy["release_rules"]["decision_if_conditioned"]
        else:
            decision = policy["release_rules"]["decision_if_ready"]

        decisions[system["system_id"]] = {
            "system_name": system["name"],
            "decision": decision,
            "blockers": blockers,
            "conditions": conditions,
            "closed_requirements": closed,
            "classification": classification["classification"],
            "rationale": classification["rationale"],
        }

    return register, crosswalk, decisions


def rows_for_system(crosswalk, system_id):
    return [row for row in crosswalk if row["system_id"] == system_id]


def render_gap_matrix(register, crosswalk, decisions):
    lines = [
        "# Matriz de huecos de cumplimiento",
        "",
        "Este informe no decide por el equipo legal. Sirve para que ingeniería vea qué evidencia existe, cuál falta y qué gate se deriva de los datos cargados.",
        "",
        "| Sistema | Clasificación inicial | Decisión | Cerrados | Condiciones | Bloqueantes |",
        "|---|---|---|---:|---:|---:|",
    ]
    for system in register:
        decision = decisions[system["system_id"]]
        lines.append(
            "| {name} | `{classification}` | `{decision}` | {closed} | {conditions} | {blockers} |".format(
                name=system["name"],
                classification=decision["classification"],
                decision=decision["decision"],
                closed=decision["closed_requirements"],
                conditions=len(decision["conditions"]),
                blockers=len(decision["blockers"]),
            )
        )

    for system in register:
        system_id = system["system_id"]
        decision = decisions[system_id]
        lines.extend([
            "",
            f"## {system['name']}",
            "",
            f"- `system_id`: `{system_id}`.",
            f"- Clasificación inicial: `{decision['classification']}`.",
            f"- Motivo: {decision['rationale']}.",
            f"- Gate: `{decision['decision']}`.",
            "",
            "| Requisito | Estado | Evidencia | Owner | Qué hacer |",
            "|---|---|---|---|---|",
        ])
        for row in rows_for_system(crosswalk, system_id):
            if row["gate_status"] == "cerrado":
                action = "mantener versión y fecha de revisión"
            elif row["gate_status"] == "bloqueante":
                action = "cerrar antes de avanzar de fase"
            else:
                action = "cerrar condición y repetir gate"
            lines.append(
                "| `{req}` | `{status}` | `{path}` | `{owner}` | {action} |".format(
                    req=row["requirement_id"],
                    status=row["gate_status"],
                    path=row["evidence_path"] or row["expected_artifact"],
                    owner=row["evidence_owner"],
                    action=action,
                )
            )
    lines.append("")
    return "\n".join(lines)


def select_primary_system(register, decisions):
    high_risk = [system for system in register if decisions[system["system_id"]]["classification"] == "alto_riesgo_posible"]
    return high_risk[0] if high_risk else register[0]


def render_technical_file(primary, crosswalk, decisions, policy):
    rows = rows_for_system(crosswalk, primary["system_id"])
    lines = [
        f"# Technical file mínimo · {primary['name']}",
        "",
        "Este documento es un esqueleto operativo inspirado en Annex IV. Debe completarse con documentación real antes de una revisión formal.",
        "",
        "## 1. Identidad y alcance",
        "",
        f"- `system_id`: `{primary['system_id']}`.",
        f"- Owner: `{primary['owner']}`.",
        f"- Fecha de revisión: `{policy['assessment_date']}`.",
        f"- Versión de modelo: `{primary['model_id']}`.",
        f"- Versión de prompt: `{primary['prompt_version']}`.",
        f"- Versión de índice RAG: `{primary['rag_index_version']}`.",
        f"- Versión de política de tools: `{primary['tool_policy_version']}`.",
        "",
        "## 2. Finalidad prevista",
        "",
        f"{primary['intended_purpose']}. Efecto declarado: `{primary['effect']}`. Autonomía: `{primary['autonomy']}`.",
        "",
        "## 3. Clasificación inicial",
        "",
        f"- Resultado: `{decisions[primary['system_id']]['classification']}`.",
        f"- Motivo: {decisions[primary['system_id']]['rationale']}.",
        "- Esta clasificación debe validarse con asesoría competente antes de producción regulada.",
        "",
        "## 4. Arquitectura y componentes",
        "",
        "| Componente | Versión | Qué revisar |",
        "|---|---|---|",
        f"| Modelo | `{primary['model_id']}` | proveedor, región, contrato, límites y cambios de versión |",
        f"| Prompt | `{primary['prompt_version']}` | instrucciones, salidas, límites y pruebas de regresión |",
        f"| RAG | `{primary['rag_index_version']}` | linaje, ACL, vigencia, reindexado y calidad de recuperación |",
        f"| Tools | `{primary['tool_policy_version']}` | scopes, aprobación, egress, idempotencia y trazas |",
        "",
        "## 5. Datos y privacidad",
        "",
        f"- Datos personales declarados: `{primary['personal_data']}`.",
        f"- Categorías especiales declaradas: `{primary['special_category']}`.",
        "- Revisar linaje, minimización, retención, derechos y transferencias antes de publicar.",
        "",
        "## 6. Evidencias enlazadas",
        "",
        "| Marco | Requisito | Estado | Evidencia |",
        "|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['framework']} | `{row['requirement_id']}` | `{row['gate_status']}` | `{row['evidence_path'] or row['expected_artifact']}` |"
        )

    lines.extend([
        "",
        "## 7. Criterio de salida",
        "",
        f"Gate actual: `{decisions[primary['system_id']]['decision']}`.",
        "",
        "Para avanzar, todo requisito bloqueante debe tener evidencia aceptada, versionada y con owner. Las condiciones deben tener fecha de cierre y responsable.",
        "",
    ])
    return "\n".join(lines)


def render_aims_scope(register, decisions, policy):
    lines = [
        "# Alcance AIMS · ISO/IEC 42001",
        "",
        f"Fecha de corte: `{policy['source_cutoff']}`.",
        f"Política usada: `{policy['policy_version']}`.",
        "",
        "## Sistemas cubiertos",
        "",
        "| Sistema | Dominio | Fase | Owner | Clasificación inicial |",
        "|---|---|---|---|---|",
    ]
    for system in register:
        decision = decisions[system["system_id"]]
        lines.append(
            f"| {system['name']} | `{system['domain']}` | `{system['production_stage']}` | `{system['owner']}` | `{decision['classification']}` |"
        )
    lines.extend([
        "",
        "## Procesos incluidos",
        "",
        "- Intake de casos de uso y clasificación inicial.",
        "- Inventario de sistemas, owners y versiones vivas.",
        "- Gestión de riesgos y controles de IA.",
        "- Gobierno de datos, privacidad y retención.",
        "- Evals, gates de release, monitorización y registro postdespliegue.",
        "- Control de cambios de modelo, prompt, índice RAG, tools, política y proveedor.",
        "- Revisión interna periódica y acciones correctivas.",
        "",
        "## Límites explícitos",
        "",
        "- Este kit no sustituye revisión legal ni certificación formal.",
        "- El alcance cubre sistemas declarados en `data/ai_systems.csv`; cualquier sistema fuera del inventario debe incorporarse antes de una revisión completa.",
        "",
    ])
    return "\n".join(lines)


def render_change_control(register):
    lines = [
        "# Registro de control de cambios",
        "",
        "Cada cambio siguiente puede alterar clasificación, evidencias o gate. Debe registrarse antes de publicar.",
        "",
        "| Cambio | Por qué importa | Evidencia que debe reabrirse |",
        "|---|---|---|",
        "| Nuevo modelo o proveedor | Cambia comportamiento, región, contrato, logs y límites. | technical file, evals, privacidad, manifest. |",
        "| Nuevo prompt de sistema | Cambia instrucciones, formato, límites y decisiones de tool. | prompt diff, regresiones, appsec gate. |",
        "| Nuevo índice RAG | Cambia conocimiento recuperado, ACL y vigencia documental. | linaje, retrieval checks, trace sample. |",
        "| Nueva tool con efecto real | Cambia permisos, aprobación, trazas y operación. | tool contract, RACI, approval gate. |",
        "| Cambio de finalidad | Puede cambiar categoría AI Act y DPIA. | clasificación, alcance AIMS, risk register. |",
        "| Paso de piloto a producción | Cambia exposición, SLO, soporte y seguimiento. | audit gate, monitoring plan, operator manual. |",
        "",
        "## Aplicación a los sistemas del kit",
        "",
    ]
    for system in register:
        lines.append(
            f"- `{system['system_id']}`: reabrir gate si cambian `{system['model_id']}`, `{system['prompt_version']}`, `{system['rag_index_version']}` o `{system['tool_policy_version']}`."
        )
    lines.append("")
    return "\n".join(lines)


def providers_for_system(providers, system_id):
    return [row for row in providers if row["system_id"] == system_id]


def render_provider_due_diligence(register, providers):
    lines = [
        "# Due diligence técnica de terceros",
        "",
        "Este informe revisa proveedores que pueden ver datos, cambiar comportamiento, afectar disponibilidad o modificar una decisión operativa.",
        "",
        "| Sistema | Proveedor | Capa | Región | Datos enviados | Estado | Hueco principal |",
        "|---|---|---|---|---|---|---|",
    ]
    for system in register:
        for provider in providers_for_system(providers, system["system_id"]):
            gaps = []
            if provider["exit_plan"] == "missing":
                gaps.append("plan de salida")
            if provider["contract_artifact"] == "":
                gaps.append("contrato")
            if provider["logs_retention"] == "":
                gaps.append("retención de logs")
            if provider["status"] != "accepted":
                gaps.append(provider["notes"])
            gap = "; ".join(gaps) or "sin hueco principal"
            lines.append(
                "| {system} | {provider} | `{layer}` | `{region}` | `{data}` | `{status}` | {gap} |".format(
                    system=system["name"],
                    provider=provider["provider_name"],
                    layer=provider["service_layer"],
                    region=provider["region"],
                    data=provider["data_sent"],
                    status=provider["status"],
                    gap=gap,
                )
            )

    lines.extend([
        "",
        "## Checklist que debería cerrar el equipo",
        "",
        "- Confirmar región efectiva del servicio y si hay cambios por fallback.",
        "- Confirmar si el proveedor conserva prompts, salidas, documentos, embeddings o solo metadatos.",
        "- Revisar DPA, subprocesadores, periodo de retención, soporte y contacto operativo.",
        "- Probar plan de salida: export, borrado, reindexado y sustitución de proveedor.",
        "- Registrar cómo se notifican cambios de modelo, API, runtime o contrato.",
        "- Conectar cada proveedor con `technical_file`, `data_flow`, `recordkeeping_schema` y `change_control_record`.",
        "",
    ])
    return "\n".join(lines)


def maturity_level(row):
    if row["evidence_status"] == "missing":
        return 0, "promesa sin evidencia"
    if row["evidence_status"] in {"partial", "stale"}:
        return 2, "evidencia parcial o caducada"
    if row["evidence_status"] == "accepted" and row["evidence_version"] and row["reviewed_on"]:
        if row["evidence_path"].startswith("output/") or row["evidence_path"].startswith("../"):
            return 4, "evidencia versionada y regenerable"
        return 3, "evidencia versionada"
    return 1, "documento sin versionado suficiente"


def render_evidence_maturity(crosswalk):
    lines = [
        "# Modelo de madurez de evidencias",
        "",
        "| Nivel | Lectura |",
        "|---:|---|",
        "| 0 | Promesa: el requisito se conoce, pero no hay evidencia. |",
        "| 1 | Documento: existe algo, pero sin versión o fecha clara. |",
        "| 2 | Parcial: evidencia incompleta, caducada o condicionada. |",
        "| 3 | Versionada: artefacto con owner, versión y revisión. |",
        "| 4 | Regenerable: artefacto generado por pipeline o enlazado a salida reproducible. |",
        "",
        "## Resultado por requisito",
        "",
        "| Sistema | Requisito | Gate | Nivel | Lectura |",
        "|---|---|---|---:|---|",
    ]
    for row in crosswalk:
        level, label = maturity_level(row)
        lines.append(
            f"| {row['system_name']} | `{row['requirement_id']}` | `{row['gate_status']}` | {level} | {label} |"
        )
    lines.append("")
    return "\n".join(lines)


def render_policy_as_code_rules(policy):
    lines = [
        "# Reglas policy-as-code del gate",
        "",
        "Estas reglas explican la decisión del script. Pueden traducirse a CI, OPA, checks propios o un pipeline interno.",
        "",
        "```python",
        "PRIORIDAD = {",
        "    'publicar_con_seguimiento': 0,",
        "    'publicar_con_condiciones': 1,",
        "    'revisar_antes': 2,",
        "}",
        "",
        "def subir(decision_actual, decision_nueva):",
        "    if PRIORIDAD[decision_nueva] > PRIORIDAD[decision_actual]:",
        "        return decision_nueva",
        "    return decision_actual",
        "",
        "def decidir_gate(classification, personal_data, missing_requirements, evidence_age_days, provider_exit_missing):",
        "    decision = 'publicar_con_seguimiento'",
        "    if classification == 'alto_riesgo_posible' and 'AIACT_ART12_RECORD_KEEPING' in missing_requirements:",
        "        decision = subir(decision, 'revisar_antes')",
        "    if classification == 'alto_riesgo_posible' and 'AIACT_ART11_ANNEXIV_TECH_DOC' in missing_requirements:",
        "        decision = subir(decision, 'revisar_antes')",
        "    if personal_data and 'GDPR_DPIA' in missing_requirements:",
        "        decision = subir(decision, 'publicar_con_condiciones')",
        f"    if evidence_age_days is not None and evidence_age_days > {policy['release_rules']['stale_after_days']}:",
        "        decision = subir(decision, 'publicar_con_condiciones')",
        "    if provider_exit_missing:",
        "        decision = subir(decision, 'publicar_con_condiciones')",
        "    return decision",
        "",
        "```",
        "",
        "## Criterio de diseño",
        "",
        "- Las reglas bloqueantes deben ser pocas, explícitas y defendibles.",
        "- Las condiciones deben tener owner, fecha y evidencia esperada.",
        "- Cada excepción debe quedar documentada con `system_id`, versión y motivo.",
        "- Si cambia modelo, prompt, RAG, tool, finalidad o proveedor, se repite el gate.",
        "",
    ]
    return "\n".join(lines)


def render_ai_bom(register, providers, decisions, policy):
    lines = [
        "# AI-BOM operativo",
        "",
        "Este AI-BOM no es un inventario decorativo. Sirve para saber qué piezas vivas pueden cambiar el comportamiento de cada sistema de IA: modelo, prompt, RAG, tools, terceros, memoria, políticas y evidencias.",
        "",
        f"- Fecha de corte: `{policy['source_cutoff']}`.",
        f"- Politica: `{policy['policy_version']}`.",
        "",
    ]
    for system in register:
        decision = decisions[system["system_id"]]
        system_providers = providers_for_system(providers, system["system_id"])
        provider_names = "; ".join(provider["provider_name"] for provider in system_providers) or "sin terceros declarados"
        lines.extend([
            f"## {system['name']}",
            "",
            "| Pieza | Valor vivo | Por que importa |",
            "|---|---|---|",
            f"| `system_id` | `{system['system_id']}` | Une evidencias, logs, owners y decisión. |",
            f"| Modelo | `{system['model_id']}` | Cambiarlo exige repetir evals, privacidad y gate si afecta salida. |",
            f"| Prompt | `{system['prompt_version']}` | Cambia instrucciones, formato, criterios y límites. |",
            f"| RAG | `{system['rag_index_version']}` | Cambia documentos recuperados, ACL, citas y vigencia. |",
            f"| Tools | `{system['tool_policy_version']}` | Cambia acciones posibles, scopes, aprobaciones y trazas. |",
            f"| Terceros | {provider_names} | Pueden afectar datos, disponibilidad, contrato, region y salida. |",
            f"| Datos personales | `{system['personal_data']}` | Conecta con minimizacion, DPIA/EIPD, retención y derechos. |",
            f"| Decisión de gate | `{decision['decision']}` | Explica si puede avanzar, queda condicionado o debe revisarse antes. |",
            "",
            "### Checklist Zero Trust para agentes",
            "",
            "| Control | Pregunta de revisión | Evidencia esperada |",
            "|---|---|---|",
            "| Identidad | ¿El agente tiene identidad técnica propia por sistema y entorno? | `agent_id`, owner, entorno y traza. |",
            "| Credenciales | ¿La credencial caduca y tiene scopes limitados? | TTL, scopes, rotacion y registro de uso. |",
            "| Tools | ¿Solo ve tools necesarias para está finalidad? | allowlist, contrato de parámetros y approval si hay efecto real. |",
            "| Memoria | ¿La memoria tiene TTL, origen, hash y aislamiento? | política de memoria, purga y prueba de no cruce. |",
            "| Configuración | ¿La política activa está versionada y hasheada? | manifest, hash, PR o cambio aprobado. |",
            "| Reversibilidad | ¿Se puede revocar credencial, apagar tool o volver a versión anterior? | rollback probado y runbook. |",
            "",
        ])
    return "\n".join(lines)


def render_audit_gate(register, decisions):
    overall = "publicar_con_seguimiento"
    if any(item["decision"] == "revisar_antes" for item in decisions.values()):
        overall = "revisar_antes"
    elif any(item["decision"] == "publicar_con_condiciones" for item in decisions.values()):
        overall = "publicar_con_condiciones"

    lines = [
        "# Gate de auditoría",
        "",
        f"Decisión global: `{overall}`.",
        "",
        "| Sistema | Decisión | Bloqueantes | Condiciones |",
        "|---|---|---:|---:|",
    ]
    for system in register:
        decision = decisions[system["system_id"]]
        lines.append(
            f"| {system['name']} | `{decision['decision']}` | {len(decision['blockers'])} | {len(decision['conditions'])} |"
        )
    lines.extend([
        "",
        "## Lectura operativa",
        "",
    ])
    if overall == "revisar_antes":
        lines.append("No avanzar de fase en los sistemas con requisitos bloqueantes. El siguiente paso es cerrar evidencias, repetir el script y conservar el diff del paquete.")
    elif overall == "publicar_con_condiciones":
        lines.append("Avanzar solo con condiciones fechadas, owner asignado y monitorización explícita.")
    else:
        lines.append("Avanzar conservando manifest, trazas de muestra y revisión postdespliegue.")

    lines.extend([
        "",
        "## Checklist para defender el gate",
        "",
        "- Enseñar inventario y clasificación inicial.",
        "- Enseñar crosswalk requisito -> evidencia.",
        "- Abrir los huecos bloqueantes y explicar owner, fecha y criterio de cierre.",
        "- Confirmar que cada cambio relevante reabre revisión.",
        "- Guardar manifest como evidencia de la versión evaluada.",
        "",
    ])
    return "\n".join(lines), overall


def build_manifest(register, crosswalk, decisions, overall, policy, output_hashes):
    return {
        "package_id": "f9-c04-compliance-audit-pack",
        "generated_on": policy["assessment_date"],
        "source_cutoff": policy["source_cutoff"],
        "policy_version": policy["policy_version"],
        "overall_decision": overall,
        "systems": [
            {
                "system_id": system["system_id"],
                "name": system["name"],
                "owner": system["owner"],
                "classification": decisions[system["system_id"]]["classification"],
                "decision": decisions[system["system_id"]]["decision"],
            }
            for system in register
        ],
        "input_files": [
            "contracts/compliance_policy.json",
            "data/ai_systems.csv",
            "data/evidence_catalog.csv",
            "data/providers.csv"
        ],
        "output_files": [
            "output/ai_system_register.csv",
            "output/article_to_artifact_crosswalk.csv",
            "output/compliance_gap_matrix.md",
            "output/annex_iv_technical_file.md",
            "output/iso42001_aims_scope.md",
            "output/change_control_record.md",
            "output/audit_gate.md",
            "output/trace_evidence_sample.jsonl",
            "output/recordkeeping_schema.json",
            "output/provider_due_diligence_checklist.md",
            "output/ai_bom.md",
            "output/evidence_maturity_model.md",
            "output/policy_as_code_rules.md"
        ],
        "output_hashes_sha256": output_hashes,
        "counts": {
            "systems": len(register),
            "crosswalk_rows": len(crosswalk),
            "systems_with_blockers": sum(1 for item in decisions.values() if item["blockers"]),
            "systems_with_conditions": sum(1 for item in decisions.values() if item["conditions"]),
        }
    }


def build_trace_sample(register, decisions, policy):
    traces = []
    assessment = parse_date(policy["assessment_date"]) or date.today()
    retention_until = (assessment + timedelta(days=180)).isoformat()
    for index, system in enumerate(register, start=1):
        decision = decisions[system["system_id"]]
        traces.append({
            "event_id": f"f9c04_trace_{index:03d}",
            "event_type": "compliance_gate_evaluated",
            "timestamp": f"{policy['assessment_date']}T16:{20 + index:02d}:00Z",
            "system_id": system["system_id"],
            "policy_version": policy["policy_version"],
            "model_id": system["model_id"],
            "prompt_version": system["prompt_version"],
            "rag_index_version": system["rag_index_version"],
            "tool_policy_version": system["tool_policy_version"],
            "classification": decision["classification"],
            "decision": decision["decision"],
            "blockers": decision["blockers"],
            "conditions": decision["conditions"],
            "personal_data_stored": False,
            "retention_until": retention_until,
        })
    return traces


def write_trace_jsonl(path, traces):
    with path.open("w", encoding="utf-8") as handle:
        for trace in traces:
            handle.write(json.dumps(trace, ensure_ascii=False) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="Escribe salidas en output/")
    parser.add_argument("--fail-on-blocker", action="store_true", help="Devuelve código 2 si hay bloqueos")
    args = parser.parse_args()

    policy = load_json(POLICY)
    systems = load_csv(SYSTEMS)
    evidence_rows = load_csv(EVIDENCE)
    providers = load_csv(PROVIDERS)
    register, crosswalk, decisions = evaluate(policy, systems, evidence_rows)
    primary = select_primary_system(register, decisions)
    audit_gate_md, overall = render_audit_gate(register, decisions)

    if args.write:
        OUTPUT.mkdir(parents=True, exist_ok=True)
        write_csv(
            OUTPUT / "ai_system_register.csv",
            register,
            [
                "system_id",
                "name",
                "owner",
                "role_provider",
                "role_deployer",
                "domain",
                "intended_purpose",
                "effect",
                "autonomy",
                "personal_data",
                "special_category",
                "production_stage",
                "model_id",
                "prompt_version",
                "rag_index_version",
                "tool_policy_version",
                "review_date",
                "initial_classification",
                "classification_rationale",
            ],
        )
        write_csv(
            OUTPUT / "article_to_artifact_crosswalk.csv",
            crosswalk,
            [
                "system_id",
                "system_name",
                "initial_classification",
                "framework",
                "requirement_id",
                "requirement_label",
                "question",
                "expected_artifact",
                "evidence_path",
                "evidence_owner",
                "evidence_version",
                "reviewed_on",
                "evidence_status",
                "gate_status",
                "notes",
            ],
        )
        (OUTPUT / "compliance_gap_matrix.md").write_text(render_gap_matrix(register, crosswalk, decisions), encoding="utf-8")
        (OUTPUT / "annex_iv_technical_file.md").write_text(render_technical_file(primary, crosswalk, decisions, policy), encoding="utf-8")
        (OUTPUT / "iso42001_aims_scope.md").write_text(render_aims_scope(register, decisions, policy), encoding="utf-8")
        (OUTPUT / "change_control_record.md").write_text(render_change_control(register), encoding="utf-8")
        (OUTPUT / "audit_gate.md").write_text(audit_gate_md, encoding="utf-8")
        write_trace_jsonl(OUTPUT / "trace_evidence_sample.jsonl", build_trace_sample(register, decisions, policy))
        write_json(OUTPUT / "recordkeeping_schema.json", build_recordkeeping_schema(policy))
        (OUTPUT / "provider_due_diligence_checklist.md").write_text(render_provider_due_diligence(register, providers), encoding="utf-8")
        (OUTPUT / "ai_bom.md").write_text(render_ai_bom(register, providers, decisions, policy), encoding="utf-8")
        (OUTPUT / "evidence_maturity_model.md").write_text(render_evidence_maturity(crosswalk), encoding="utf-8")
        (OUTPUT / "policy_as_code_rules.md").write_text(render_policy_as_code_rules(policy), encoding="utf-8")
        hash_targets = [
            "ai_system_register.csv",
            "article_to_artifact_crosswalk.csv",
            "compliance_gap_matrix.md",
            "annex_iv_technical_file.md",
            "iso42001_aims_scope.md",
            "change_control_record.md",
            "audit_gate.md",
            "trace_evidence_sample.jsonl",
            "recordkeeping_schema.json",
            "provider_due_diligence_checklist.md",
            "ai_bom.md",
            "evidence_maturity_model.md",
            "policy_as_code_rules.md",
        ]
        output_hashes = {
            f"output/{name}": file_sha256(OUTPUT / name)
            for name in hash_targets
        }
        write_json(OUTPUT / "evidence_package_manifest.json", build_manifest(register, crosswalk, decisions, overall, policy, output_hashes))

    print(json.dumps({
        "overall_decision": overall,
        "systems": decisions,
        "wrote_output": args.write,
    }, ensure_ascii=False, indent=2))

    if args.fail_on_blocker and overall == "revisar_antes":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
