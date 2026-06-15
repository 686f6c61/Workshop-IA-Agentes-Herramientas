#!/usr/bin/env python3
import argparse
import csv
import json
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POLICY = ROOT / "contracts" / "final_governance_policy.json"
DEFAULT_FINDINGS = ROOT / "data" / "governance_findings.csv"
DEFAULT_COMPONENTS = ROOT / "data" / "release_components.csv"
DEFAULT_OUTPUT = ROOT / "output"


def read_json(path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def read_csv(path):
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def as_int(value):
    return int(str(value or "0"))


def component_index(components):
    return {row["system_id"]: row for row in components}


def severity_points(row, policy):
    return as_int(row["severity"]) * float(policy["layer_weights"].get(row["layer"], 1.0))


def decide(findings, policy):
    rules = policy["release_rules"]
    blockers = [row for row in findings if row["status"] == rules["block_status"]]
    reviews = [row for row in findings if row["status"] == rules["review_status"]]
    high_reviews = [
        row for row in reviews
        if as_int(row["severity"]) >= rules["high_severity_min"]
    ]
    missing_layers = sorted(set(policy["required_layers"]) - {row["layer"] for row in findings})
    if blockers or missing_layers:
        decision = "revisar_antes"
    elif len(high_reviews) > rules["max_open_review_high_severity"]:
        decision = "publicar_con_condiciones"
    elif reviews:
        decision = "publicar_con_condiciones"
    else:
        decision = "publicar_con_seguimiento"
    return {
        "decision": decision,
        "blocker_count": len(blockers),
        "review_count": len(reviews),
        "high_review_count": len(high_reviews),
        "missing_layers": missing_layers,
        "blockers": blockers,
        "reviews": reviews,
    }


def build_matrix(findings, components, policy):
    components_by_system = component_index(components)
    rows = []
    for item in findings:
        component = components_by_system.get(item["system_id"], {})
        rows.append({
            "system_id": item["system_id"],
            "system_name": component.get("name", ""),
            "stage": component.get("stage", ""),
            "layer": item["layer"],
            "chapter": item["chapter"],
            "requirement": item["requirement"],
            "status": item["status"],
            "severity": item["severity"],
            "weighted_points": round(severity_points(item, policy), 3),
            "owner": item["owner"],
            "evidence_path": item["evidence_path"],
            "action": item["action"],
            "due_days": item["due_days"],
            "model_id": component.get("model_id", ""),
            "prompt_version": component.get("prompt_version", ""),
            "rag_index_version": component.get("rag_index_version", ""),
            "tool_policy_version": component.get("tool_policy_version", ""),
        })
    return rows


def summarize_by_system(findings, components):
    systems = component_index(components)
    grouped = defaultdict(list)
    for row in findings:
        grouped[row["system_id"]].append(row)
    summary = []
    for system_id, rows in sorted(grouped.items()):
        counts = Counter(row["status"] for row in rows)
        summary.append({
            "system_id": system_id,
            "name": systems.get(system_id, {}).get("name", ""),
            "stage": systems.get(system_id, {}).get("stage", ""),
            "pass": counts.get("pass", 0),
            "review": counts.get("review", 0),
            "block": counts.get("block", 0),
            "max_severity": max(as_int(row["severity"]) for row in rows),
        })
    return summary


def render_decision(report):
    lines = [
        "# Decisión final de gobernanza",
        "",
        f"Decisión: `{report['decision']['decision']}`.",
        "",
        "## Lectura ejecutiva",
        "",
    ]
    if report["decision"]["decision"] == "revisar_antes":
        lines.append("No se debería avanzar de fase porque existe al menos una evidencia bloqueante o falta una capa obligatoria del paquete.")
    elif report["decision"]["decision"] == "publicar_con_condiciones":
        lines.append("Se podría avanzar solo con condiciones fechadas, owners claros y repeticion del gate antes de ampliar alcance.")
    else:
        lines.append("Se puede avanzar con seguimiento, conservando manifest, trazas y revisión periodica.")
    lines.extend([
        "",
        "## Resumen",
        "",
        f"- Bloqueantes: {report['decision']['blocker_count']}.",
        f"- En revisión: {report['decision']['review_count']}.",
        f"- Revisiones de severidad alta: {report['decision']['high_review_count']}.",
        f"- Capas ausentes: {', '.join(report['decision']['missing_layers']) or 'ninguna'}.",
        "",
        "## Sistemas",
        "",
        "| Sistema | Fase | Pass | Revision | Bloqueo | Severidad maxima |",
        "|---|---|---:|---:|---:|---:|",
    ])
    for row in report["system_summary"]:
        lines.append(
            f"| {row['name']} | `{row['stage']}` | {row['pass']} | {row['review']} | {row['block']} | {row['max_severity']} |"
        )
    lines.extend([
        "",
        "## Bloqueantes",
        "",
    ])
    if report["decision"]["blockers"]:
        for row in report["decision"]["blockers"]:
            lines.append(f"- `{row['system_id']}` · `{row['requirement']}`: {row['action']} · owner `{row['owner']}`.")
    else:
        lines.append("- No hay bloqueantes abiertos.")
    lines.extend([
        "",
        "## Condiciones principales",
        "",
    ])
    if report["decision"]["reviews"]:
        for row in report["decision"]["reviews"]:
            lines.append(f"- `{row['system_id']}` · `{row['requirement']}`: {row['action']} · {row['due_days']} días · owner `{row['owner']}`.")
    else:
        lines.append("- No hay condiciones abiertas.")
    lines.extend([
        "",
        "## Decisión profesional",
        "",
        "La decisión se basa en evidencias por capa. Si cambia modelo, prompt, índice RAG, tools, finalidad, proveedor o fase, hay que repetir este gate.",
        "",
    ])
    return "\n".join(lines)


def render_remediation(report):
    open_items = [row for row in report["matrix"] if row["status"] in {"block", "review"}]
    open_items = sorted(open_items, key=lambda row: (row["status"] != "block", -as_int(row["severity"]), as_int(row["due_days"])))
    lines = [
        "# Plan de remediacion",
        "",
        "| Prioridad | Sistema | Capa | Requisito | Estado | Owner | Plazo | Accion |",
        "|---:|---|---|---|---|---|---:|---|",
    ]
    for index, row in enumerate(open_items, start=1):
        lines.append(
            f"| {index} | `{row['system_id']}` | `{row['layer']}` | `{row['requirement']}` | `{row['status']}` | `{row['owner']}` | {row['due_days']} | {row['action']} |"
        )
    lines.extend([
        "",
        "## Criterio de cierre",
        "",
        "Un item no se cierra por comentario verbal. Se cierra cuando existe evidencia versionada, owner, fecha y salida del gate repetida.",
        "",
    ])
    return "\n".join(lines)


def render_evidence_index(report):
    lines = [
        "# Índice del paquete de evidencias",
        "",
        "| Sistema | Capa | Requisito | Evidencia | Versiones vivas |",
        "|---|---|---|---|---|",
    ]
    for row in report["matrix"]:
        versions = f"modelo={row['model_id']} · prompt={row['prompt_version']} · rag={row['rag_index_version']} · tools={row['tool_policy_version']}"
        lines.append(
            f"| `{row['system_id']}` | `{row['layer']}` | `{row['requirement']}` | `{row['evidence_path']}` | {versions} |"
        )
    lines.append("")
    return "\n".join(lines)


def resolve_evidence_path(value):
    raw = str(value or "").strip()
    if not raw:
        return None
    candidate = ROOT / raw
    return candidate.resolve()


def build_source_evidence_rows(report):
    rows = []
    for row in report["matrix"]:
        resolved = resolve_evidence_path(row["evidence_path"])
        exists = bool(resolved and resolved.exists())
        if "recordkeeping_contract" in row["evidence_path"] and row["status"] == "pass":
            note = "archivo presente; verificar que el contrato está conectado a export real de trazas"
        elif row["status"] == "pass" and exists:
            note = "evidencia presente; revisar calidad y vigencia"
        elif row["status"] == "pass" and not exists:
            note = "estado pass sin archivo local visible; revisar ruta o repositorio externo"
        elif row["status"] == "block":
            note = "evidencia insuficiente para avanzar aunque exista contrato técnico"
        else:
            note = "condición abierta; necesita cierre con owner y nuevo gate"
        rows.append({
            "system_id": row["system_id"],
            "layer": row["layer"],
            "requirement": row["requirement"],
            "status": row["status"],
            "owner": row["owner"],
            "evidence_path": row["evidence_path"],
            "exists": str(exists).lower(),
            "note": note,
        })
    return rows


def render_source_evidence_review(report):
    rows = build_source_evidence_rows(report)
    missing_pass = [row for row in rows if row["status"] == "pass" and row["exists"] == "false"]
    lines = [
        "# Revision de evidencias fuente",
        "",
        "Este informe comprueba que las rutas declaradas en la matriz apuntan a artefactos reales dentro del kit o a salidas generadas por capítulos anteriores. No decide calidad legal; obliga a que la conversación técnica tenga archivos concretos delante.",
        "",
        f"- Evidencias revisadas: {len(rows)}.",
        f"- Evidencias en `pass` sin archivo local visible: {len(missing_pass)}.",
        "",
        "| Sistema | Capa | Requisito | Estado | Evidencia | Existe | Lectura |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| `{row['system_id']}` | `{row['layer']}` | `{row['requirement']}` | `{row['status']}` | `{row['evidence_path']}` | `{row['exists']}` | {row['note']} |"
        )
    lines.extend([
        "",
        "## Uso en una revisión",
        "",
        "Primero se mira el estado del gate. Después se abre la evidencia. Una evidencia existe, pero aún puede ser insuficiente: por ejemplo, un contrato de trazas no cierra record-keeping si todavía no hay export real conectado al pipeline.",
        "",
    ])
    return "\n".join(lines)


def render_technical_decision_memo(report):
    decision = report["decision"]
    blocker_rows = decision["blockers"]
    review_rows = decision["reviews"]
    lines = [
        "# Memo técnico de decisión",
        "",
        f"Decisión recomendada: `{decision['decision']}`.",
        "",
        "## Motivo",
        "",
    ]
    if blocker_rows:
        primary = blocker_rows[0]
        lines.append(
            f"El primer bloqueo es `{primary['requirement']}` en `{primary['system_id']}`. Owner `{primary['owner']}` debe ejecutar: {primary['action']}."
        )
    elif review_rows:
        lines.append("No hay bloqueos, pero quedan condiciones abiertas. La publicación solo debería avanzar con alcance limitado, owner y fecha de nuevo gate.")
    else:
        lines.append("No hay bloqueos ni condiciones abiertas. Se puede avanzar con seguimiento y conservando evidencias.")
    lines.extend([
        "",
        "## Condiciones abiertas",
        "",
        "| Sistema | Capa | Requisito | Owner | Plazo |",
        "|---|---|---|---|---:|",
    ])
    for row in review_rows:
        lines.append(
            f"| `{row['system_id']}` | `{row['layer']}` | `{row['requirement']}` | `{row['owner']}` | {row['due_days']} |"
        )
    if not review_rows:
        lines.append("| - | - | - | - | - |")
    lines.extend([
        "",
        "## Recomendación operativa",
        "",
        "Repetir el gate si cambia modelo, prompt, RAG, tool, política, memoria, proveedor, finalidad o fase. Conservar esta decisión, el diff de hallazgos y el `ci_gate.json` como evidencia del criterio aplicado.",
        "",
    ])
    return "\n".join(lines)


def render_risk_acceptance(report):
    lines = [
        "# Registro de aceptación de riesgo residual",
        "",
        "Este registro solo aplica a condiciones que no bloquean. Un bloqueo no se acepta: se cierra o se mantiene la decisión `revisar_antes`.",
        "",
        "| Sistema | Requisito | Severidad | Owner que debe aceptar | Condición |",
        "|---|---|---:|---|---|",
    ]
    review_rows = [row for row in report["matrix"] if row["status"] == "review"]
    for row in review_rows:
        lines.append(
            f"| `{row['system_id']}` | `{row['requirement']}` | {row['severity']} | `{row['owner']}` | {row['action']} |"
        )
    if not review_rows:
        lines.append("| - | - | - | - | Sin condiciones abiertas. |")
    lines.append("")
    return "\n".join(lines)


def zero_trust_profile(requirement):
    profiles = {
        "agent_identity_and_short_lived_credentials": {
            "agent_boundary": "identidad y credencial",
            "identity_model": "agent_id único por sistema y entorno",
            "credential_scope": "token corto con scopes de lectura y preparación",
            "tool_boundary": "sin tools de escritura directa",
            "memory_boundary": "sin memoria compartida entre sesiones",
            "engineering_check": "revisar TTL, rotación, owner y traza de uso de credencial",
        },
        "least_agency_tool_boundary": {
            "agent_boundary": "menor capacidad de actuación",
            "identity_model": "identidad de agente separada de usuario y servicio",
            "credential_scope": "solo scopes necesarios para prepare, no execute",
            "tool_boundary": "allowlist de tools y validación de parámetros",
            "memory_boundary": "memoria de tarea con fuente trazable",
            "engineering_check": "probar que una tool no autorizada no aparece ni se ejecuta",
        },
        "memory_ttl_and_source_integrity": {
            "agent_boundary": "memoria y contexto",
            "identity_model": "usuario, sesion y agente separados",
            "credential_scope": "sin permisos extra por usar memoria",
            "tool_boundary": "RAG con ACL antes de similitud",
            "memory_boundary": "TTL, hash de origen, purga y atribucion de fuente",
            "engineering_check": "crear muestra before/after de purga y verificar hashes",
        },
        "repo_scoped_agent_identity": {
            "agent_boundary": "repositorio y entorno",
            "identity_model": "agent_id por repo, rama y entorno",
            "credential_scope": "scopes por repositorio",
            "tool_boundary": "tools limitadas a repo permitido",
            "memory_boundary": "sin memoria cruzada entre repositorios",
            "engineering_check": "intentar leer repo no permitido y comprobar bloqueo",
        },
    }
    return profiles.get(requirement, {
        "agent_boundary": "limite no clasificado",
        "identity_model": "declarar identidad técnica",
        "credential_scope": "declarar scopes y caducidad",
        "tool_boundary": "declarar allowlist de tools",
        "memory_boundary": "declarar aislamiento y TTL",
        "engineering_check": "convertir el requisito en prueba reproducible",
    })


def build_zero_trust_matrix(report):
    rows = []
    for row in report["matrix"]:
        if row["layer"] != "zero_trust_agents":
            continue
        profile = zero_trust_profile(row["requirement"])
        rows.append({
            "system_id": row["system_id"],
            "system_name": row["system_name"],
            "stage": row["stage"],
            "requirement": row["requirement"],
            "status": row["status"],
            "severity": row["severity"],
            "owner": row["owner"],
            "agent_boundary": profile["agent_boundary"],
            "identity_model": profile["identity_model"],
            "credential_scope": profile["credential_scope"],
            "tool_boundary": profile["tool_boundary"],
            "memory_boundary": profile["memory_boundary"],
            "engineering_check": profile["engineering_check"],
            "evidence_path": row["evidence_path"],
            "action": row["action"],
            "due_days": row["due_days"],
        })
    return rows


def render_agent_boundary_review(report):
    rows = build_zero_trust_matrix(report)
    open_rows = [row for row in rows if row["status"] in {"block", "review"}]
    lines = [
        "# Revision Zero Trust de agentes",
        "",
        "Esta revisión convierte el principio de menor capacidad de actuación en preguntas verificables. Un agente no debería recibir identidad, credenciales, memoria o tools por comodidad: cada capacidad tiene que tener alcance, evidencia y una prueba.",
        "",
        f"- Controles revisados: {len(rows)}.",
        f"- Controles abiertos: {len(open_rows)}.",
        "",
        "## Matriz resumida",
        "",
        "| Sistema | Requisito | Estado | Identidad | Credencial | Tools | Memoria | Prueba de ingeniería |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| `{row['system_id']}` | `{row['requirement']}` | `{row['status']}` | {row['identity_model']} | {row['credential_scope']} | {row['tool_boundary']} | {row['memory_boundary']} | {row['engineering_check']} |"
        )
    lines.extend([
        "",
        "## Lectura profesional",
        "",
    ])
    if open_rows:
        for row in open_rows:
            lines.append(
                f"- `{row['system_id']}` mantiene abierto `{row['requirement']}`. Owner `{row['owner']}` debe aportar `{row['evidence_path']}` y ejecutar: {row['action']}."
            )
    else:
        lines.append("- No quedan controles Zero Trust abiertos para agentes en este paquete.")
    lines.extend([
        "",
        "## Criterio de cierre",
        "",
        "Un control de agente se cierra cuando la capacidad queda reducida en runtime y existe evidencia reproducible. No basta con documentar la intencion: debe verse en policy-as-code, contrato de tool, TTL de credencial, traza y salida del gate.",
        "",
    ])
    return "\n".join(lines)


def render_executive_brief(report):
    return "\n".join([
        "# Resumen ejecutivo",
        "",
        f"Decisión: `{report['decision']['decision']}`.",
        "",
        f"El paquete revisa {len(report['matrix'])} controles distribuidos en riesgo, privacidad, seguridad de aplicaciónes LLM, Zero Trust para agentes, cumplimiento y operacion.",
        f"Hay {report['decision']['blocker_count']} bloqueo(s) y {report['decision']['review_count']} condición(es).",
        "",
        "Lectura: el sistema de admisiones concentra la mayor parte de la decisión. Mientras falte record-keeping exportable, no se puede defender una publicación de ese flujo.",
        "",
        "Siguiente paso: cerrar el bloqueo, repetir el gate y conservar el nuevo manifest como evidencia.",
        "",
    ])


def build_trace(report, policy):
    return {
        "event_id": "f9_final_governance_gate_001",
        "event_type": "final_governance_gate",
        "timestamp": f"{policy['assessment_date']}T18:00:00Z",
        "policy_version": policy["policy_version"],
        "decision": report["decision"]["decision"],
        "blocker_count": report["decision"]["blocker_count"],
        "review_count": report["decision"]["review_count"],
        "systems": [row["system_id"] for row in report["system_summary"]],
        "personal_data_stored": False,
    }


def write_jsonl(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def build_report(policy, findings, components):
    matrix = build_matrix(findings, components, policy)
    decision = decide(findings, policy)
    system_summary = summarize_by_system(findings, components)
    return {
        "policy_version": policy["policy_version"],
        "generated_on": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "decision": decision,
        "system_summary": system_summary,
        "matrix": matrix,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    parser.add_argument("--findings", type=Path, default=DEFAULT_FINDINGS)
    parser.add_argument("--components", type=Path, default=DEFAULT_COMPONENTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--fail-on-blocker", action="store_true")
    args = parser.parse_args()

    policy = read_json(args.policy)
    findings = read_csv(args.findings)
    components = read_csv(args.components)
    report = build_report(policy, findings, components)

    if args.write:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        write_json(args.output_dir / "governance_report.json", report)
        write_csv(args.output_dir / "control_evidence_matrix.csv", report["matrix"])
        write_csv(args.output_dir / "source_evidence_matrix.csv", build_source_evidence_rows(report))
        write_csv(args.output_dir / "zero_trust_agent_matrix.csv", build_zero_trust_matrix(report))
        (args.output_dir / "governance_release_decision.md").write_text(render_decision(report), encoding="utf-8")
        (args.output_dir / "technical_decision_memo.md").write_text(render_technical_decision_memo(report), encoding="utf-8")
        (args.output_dir / "remediation_plan.md").write_text(render_remediation(report), encoding="utf-8")
        (args.output_dir / "evidence_package_index.md").write_text(render_evidence_index(report), encoding="utf-8")
        (args.output_dir / "source_evidence_review.md").write_text(render_source_evidence_review(report), encoding="utf-8")
        (args.output_dir / "agent_boundary_review.md").write_text(render_agent_boundary_review(report), encoding="utf-8")
        (args.output_dir / "risk_acceptance_record.md").write_text(render_risk_acceptance(report), encoding="utf-8")
        (args.output_dir / "executive_brief.md").write_text(render_executive_brief(report), encoding="utf-8")
        write_json(args.output_dir / "ci_gate.json", {
            "decision": report["decision"]["decision"],
            "blocker_count": report["decision"]["blocker_count"],
            "review_count": report["decision"]["review_count"],
            "policy_version": policy["policy_version"],
        })
        write_jsonl(args.output_dir / "trace_sample.jsonl", [build_trace(report, policy)])

    print(json.dumps({
        "decision": report["decision"]["decision"],
        "blocker_count": report["decision"]["blocker_count"],
        "review_count": report["decision"]["review_count"],
        "wrote_output": args.write,
    }, ensure_ascii=False, indent=2))

    if args.fail_on_blocker and report["decision"]["decision"] == "revisar_antes":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
