#!/usr/bin/env python3
import argparse
import csv
import json
import re
import unicodedata
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "contracts" / "appsec_policy.json"
SCENARIOS_PATH = ROOT / "data" / "scenarios.jsonl"
DOCUMENTS_PATH = ROOT / "data" / "documents.jsonl"
MARKET_TOOLS_PATH = ROOT / "data" / "market_tools.csv"
OUTPUT = ROOT / "output"


def load_json(path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_jsonl(path):
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def load_csv(path):
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def normalize(value):
    text = str(value or "").strip().lower()
    return "".join(
        char for char in unicodedata.normalize("NFKD", text)
        if not unicodedata.combining(char)
    )


def domain_from_email(email):
    if "@" not in email:
        return ""
    return email.rsplit("@", 1)[1].lower()


def domain_from_url(url):
    return urlparse(url).netloc.lower()


def tool_by_name(policy):
    return {tool["name"]: tool for tool in policy["tools"]}


def role_scopes(policy, role):
    return set(policy["roles"].get(role, {}).get("scopes", []))


def pattern_ok(pattern, value):
    return re.match(pattern, str(value or "")) is not None


def validate_schema(tool, arguments):
    schema = tool["schema"]
    blockers = []
    warnings = []
    required = set(schema.get("required", []))
    present = set(arguments)
    missing = sorted(required - present)
    extras = sorted(present - set(schema.get("properties", {})))

    for field in missing:
        blockers.append(f"falta campo obligatorio en tool: {field}")
    if schema.get("additionalProperties") is False:
        for field in extras:
            blockers.append(f"campo extra no permitido en tool: {field}")

    for field, rules in schema.get("properties", {}).items():
        if field not in arguments:
            continue
        value = arguments[field]
        expected_type = rules.get("type")
        if expected_type == "string" and not isinstance(value, str):
            blockers.append(f"{field} debe ser string")
            continue
        if expected_type == "boolean" and not isinstance(value, bool):
            blockers.append(f"{field} debe ser boolean")
            continue
        if "enum" in rules and value not in rules["enum"]:
            blockers.append(f"{field} fuera de catalogo: {value}")
        if "maxLength" in rules and isinstance(value, str) and len(value) > int(rules["maxLength"]):
            blockers.append(f"{field} supera maxLength={rules['maxLength']}")
        if "pattern" in rules and isinstance(value, str) and not pattern_ok(rules["pattern"], value):
            blockers.append(f"{field} no cumple pattern {rules['pattern']}")
        if rules.get("format") == "email" and isinstance(value, str) and "@" not in value:
            blockers.append(f"{field} no parece email")
        if rules.get("format") == "url" and isinstance(value, str) and not urlparse(value).scheme:
            blockers.append(f"{field} no parece URL")

    if not blockers and warnings:
        warnings.append("schema valido con advertencias")
    return blockers, warnings


def contains_instruction_like_text(policy, text):
    text_norm = normalize(text)
    return [
        pattern
        for pattern in policy["rag"]["instruction_like_patterns"]
        if normalize(pattern) in text_norm
    ]


def evaluate_rag(policy, scenario, documents):
    blockers = []
    warnings = []
    checks = []
    role = scenario["user_role"]
    purpose = scenario["purpose"]
    uses_untrusted_blocks = bool(scenario.get("context_template_uses_untrusted_blocks", True))

    for doc_id in scenario.get("retrieved_doc_ids", []):
        doc = documents.get(doc_id)
        if not doc:
            blockers.append(f"documento no encontrado en índice: {doc_id}")
            checks.append({"doc_id": doc_id, "decision": "block", "reason": "missing"})
            continue

        doc_blockers = []
        doc_warnings = []
        if policy["rag"].get("require_acl_before_similarity") and role not in doc.get("allowed_roles", []):
            doc_blockers.append("rol sin ACL para documento")
        if policy["rag"].get("require_active_document") and doc.get("status") != "active":
            doc_blockers.append(f"documento no activo: {doc.get('status')}")
        if policy["rag"].get("require_allowed_purpose") and purpose not in doc.get("allowed_purposes", []):
            doc_blockers.append("finalidad no permitida para documento")

        instruction_patterns = contains_instruction_like_text(policy, doc.get("content_excerpt", ""))
        if instruction_patterns and doc.get("trust_label") != "trusted_policy":
            doc_warnings.append("contenido externo contiene texto con forma de orden")
            if not uses_untrusted_blocks:
                doc_blockers.append("contenido externo sin bloque delimitado de no confianza")

        blockers.extend([f"{doc_id}: {item}" for item in doc_blockers])
        warnings.extend([f"{doc_id}: {item}" for item in doc_warnings])
        checks.append(
            {
                "doc_id": doc_id,
                "title": doc.get("title"),
                "source_type": doc.get("source_type"),
                "trust_label": doc.get("trust_label"),
                "status": doc.get("status"),
                "role": role,
                "purpose": purpose,
                "decision": "block" if doc_blockers else "allow",
                "notes": doc_blockers + doc_warnings,
            }
        )

    return blockers, warnings, checks


def approval_needed(tool, arguments):
    rule = tool.get("approval_required")
    if rule is True:
        return True
    if rule == "when_send_or_personal_data":
        return arguments.get("send_mode") == "send" or bool(arguments.get("contains_personal_data"))
    return False


def evaluate_tool(policy, scenario):
    proposed = scenario.get("proposed_tool")
    if not proposed:
        return [], [], [], {"name": None, "decision": "not_requested"}

    tools = tool_by_name(policy)
    tool = tools.get(proposed.get("name"))
    if not tool:
        return [f"tool no declarada: {proposed.get('name')}"], [], [], {"name": proposed.get("name"), "decision": "block"}

    arguments = proposed.get("arguments", {})
    blockers, warnings = validate_schema(tool, arguments)
    approvals = []

    scopes = role_scopes(policy, scenario["user_role"])
    missing_scopes = sorted(set(tool["scope_required"]) - scopes)
    for scope in missing_scopes:
        blockers.append(f"scope ausente para rol {scenario['user_role']}: {scope}")

    if approval_needed(tool, arguments) and not scenario.get("approval_id"):
        approvals.append(f"{tool['name']} requiere aprobación explícita")

    if tool.get("egress") == "email_domain_allowlist":
        domain = domain_from_email(arguments.get("recipient", ""))
        allowed = set(policy["egress_policy"]["allowed_email_domains"])
        if domain not in allowed:
            blockers.append(f"dominio de correo no permitido: {domain}")

    if tool.get("egress") == "http_domain_allowlist":
        domain = domain_from_url(arguments.get("url", ""))
        allowed = set(policy["egress_policy"]["allowed_http_domains"])
        if domain not in allowed:
            blockers.append(f"dominio HTTP no permitido: {domain}")

    if tool["effect"] in {"state_change", "external_send"} and arguments.get("send_mode") == "send":
        if "idempotency_key" in tool["schema"].get("properties", {}) and not arguments.get("idempotency_key"):
            blockers.append("falta idempotency_key para efecto real")

    tool_trace = {
        "name": tool["name"],
        "capability": tool["capability"],
        "effect": tool["effect"],
        "scope_required": tool["scope_required"],
        "decision": "block" if blockers else ("needs_approval" if approvals else "allow"),
    }
    return blockers, warnings, approvals, tool_trace


def decide(blockers, approvals):
    if blockers:
        return "block"
    if approvals:
        return "needs_approval"
    return "allow"


def evaluate(policy, scenarios, documents):
    results = []
    traces = []
    for index, scenario in enumerate(scenarios, start=1):
        rag_blockers, rag_warnings, rag_checks = evaluate_rag(policy, scenario, documents)
        tool_blockers, tool_warnings, approvals, tool_trace = evaluate_tool(policy, scenario)
        blockers = rag_blockers + tool_blockers
        warnings = rag_warnings + tool_warnings
        decision = decide(blockers, approvals)
        expected = scenario.get("expected_decision")
        result = {
            "scenario_id": scenario["scenario_id"],
            "name": scenario["name"],
            "user_role": scenario["user_role"],
            "purpose": scenario["purpose"],
            "decision": decision,
            "expected_decision": expected,
            "matches_expected": decision == expected,
            "blockers": blockers,
            "approvals": approvals,
            "warnings": warnings,
            "rag_checks": rag_checks,
            "tool": tool_trace,
        }
        trace = {
            "run_id": f"f9c03_run_{index:03d}",
            "policy_version": policy["policy_version"],
            "scenario_id": scenario["scenario_id"],
            "user_role": scenario["user_role"],
            "retrieved_docs": [
                {
                    "doc_id": check["doc_id"],
                    "decision": check["decision"],
                    "trust_label": check.get("trust_label"),
                }
                for check in rag_checks
            ],
            "tool_decision": tool_trace,
            "policy_decision": decision,
            "evidence": [
                "tool_contract_matrix.csv",
                "rag_retrieval_checks.md",
                "appsec_gate_report.md",
            ],
        }
        results.append(result)
        traces.append(trace)
    return results, traces


def write_tool_matrix(policy):
    path = OUTPUT / "tool_contract_matrix.csv"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "tool",
                "capability",
                "effect",
                "scope_required",
                "approval_required",
                "egress",
                "required_fields",
            ],
        )
        writer.writeheader()
        for tool in policy["tools"]:
            writer.writerow(
                {
                    "tool": tool["name"],
                    "capability": tool["capability"],
                    "effect": tool["effect"],
                    "scope_required": ";".join(tool["scope_required"]),
                    "approval_required": tool["approval_required"],
                    "egress": tool["egress"],
                    "required_fields": ";".join(tool["schema"]["required"]),
                }
            )


def write_report(results):
    lines = [
        "# Gate de seguridad de aplicación LLM",
        "",
        "Este informe revisa escenarios de RAG y tools antes de publicar.",
        "",
        "| Escenario | Rol | Decisión | Esperado | Resultado |",
        "|---|---|---|---|---|",
    ]
    for result in results:
        ok = "OK" if result["matches_expected"] else "REVISAR"
        lines.append(
            f"| {result['scenario_id']} · {result['name']} | {result['user_role']} | "
            f"{result['decision']} | {result['expected_decision']} | {ok} |"
        )
    lines.extend(["", "## Detalle por escenario", ""])
    for result in results:
        lines.append(f"### {result['scenario_id']} · {result['name']}")
        lines.append("")
        lines.append(f"- Decisión: `{result['decision']}`")
        lines.append(f"- Esperado: `{result['expected_decision']}`")
        if not result["matches_expected"]:
            lines.append("- Diferencia crítica: la política no coincide con la expectativa del escenario. Antes de publicar, cambia contrato, ACL, egress, aprobación o test hasta que esta línea sea `OK`.")
        if result["blockers"]:
            lines.append("- Bloqueos:")
            for item in result["blockers"]:
                lines.append(f"  - {item}")
        if result["approvals"]:
            lines.append("- Aprobaciones requeridas:")
            for item in result["approvals"]:
                lines.append(f"  - {item}")
        if result["warnings"]:
            lines.append("- Advertencias:")
            for item in result["warnings"]:
                lines.append(f"  - {item}")
        if not result["blockers"] and not result["approvals"] and not result["warnings"]:
            lines.append("- Sin hallazgos para este escenario.")
        lines.append("")
    (OUTPUT / "appsec_gate_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_rag_checks(results):
    lines = [
        "# Checks de recuperación RAG",
        "",
        "| Escenario | Documento | Fuente | Confianza | Estado | Decisión | Notas |",
        "|---|---|---|---|---|---|---|",
    ]
    for result in results:
        for check in result["rag_checks"]:
            notes = "; ".join(check.get("notes", [])) or "sin notas"
            lines.append(
                f"| {result['scenario_id']} | {check.get('doc_id')} | {check.get('source_type', '')} | "
                f"{check.get('trust_label', '')} | {check.get('status', '')} | {check.get('decision')} | {notes} |"
            )
    (OUTPUT / "rag_retrieval_checks.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_market_tooling_review(rows):
    categories = {}
    for row in rows:
        categories.setdefault(row["category"], []).append(row)

    category_names = {
        "evaluation": "Evaluación offline y CI",
        "runtime": "Guardrails runtime",
        "gateway": "Gateways y proxies de IA",
        "observability": "Observabilidad y evals continuas",
        "authorization": "Policy-as-code y autorización",
    }

    lines = [
        "# Revisión de herramientas de mercado por capa",
        "",
        "Este documento no recomienda una compra automática. Ordena herramientas por la decisión técnica que cubren y por la evidencia que debería quedar si se usan.",
        "",
    ]

    for category, tools in categories.items():
        lines.append(f"## {category_names.get(category, category)}")
        lines.append("")
        lines.append("| Herramienta | Capa | Qué hace | Cuándo usarla | Límite de ingeniería | Evidencia |")
        lines.append("|---|---|---|---|---|---|")
        for tool in tools:
            lines.append(
                f"| [{tool['tool']}]({tool['url']}) | {tool['primary_layer']} | "
                f"{tool['what_it_does']} | {tool['when_to_use']} | "
                f"{tool['engineering_limit']} | {tool['evidence_to_collect']} |"
            )
        lines.append("")

    lines.extend(
        [
            "## Decisión mínima",
            "",
            "Para una aplicación LLM con RAG y tools, la combinación mínima razonable sería:",
            "",
            "1. Un gate offline con escenarios propios.",
            "2. Un control runtime para entradas, salidas o tool calls de mayor riesgo.",
            "3. Un gateway o proxy si hay varios equipos, modelos o presupuestos.",
            "4. Observabilidad con trazas de tool, RAG y policy versión.",
            "5. Autorización estructurada para acciones reales.",
            "",
            "Si falta el punto 5, el sistema puede parecer protegido, pero seguirá dejando la decisión de permisos demasiado cerca del texto generado.",
        ]
    )

    (OUTPUT / "market_tooling_review.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_day_to_day_playbook():
    lines = [
        "# Playbook diario para aplicaciones LLM con RAG y tools",
        "",
        "Este playbook convierte los ejemplos del capítulo en trabajo de PR, CI, revisión de arquitectura y operación.",
        "",
        "## PR que añade o cambia una tool",
        "",
        "| Check | Evidencia esperada |",
        "|---|---|",
        "| Capability nombrada | Acción real que la tool permite realizar. |",
        "| Effect declarado | `read`, `state_change`, `external_send`, `external_fetch` o equivalente. |",
        "| Schema estricto | Campos requeridos, tipos, enums, límites y extras rechazados. |",
        "| Scope requerido | Permisos que debe tener el rol antes de ejecutar. |",
        "| Approval | Condición clara para `needs_approval`. |",
        "| Egress | Dominios, métodos o destinos permitidos. |",
        "| Idempotencia | Clave o mecanismo para evitar duplicados. |",
        "| Traza | Campos que quedarán en logs operativos. |",
        "| Test | Escenario en `data/scenarios.jsonl` que falla si se rompe el contrato. |",
        "",
        "## Alta o cambio de documento RAG",
        "",
        "| Check | Evidencia esperada |",
        "|---|---|",
        "| `doc_id` estable | Identificador usado en trazas y citas. |",
        "| Owner | Equipo responsable de vigencia y retirada. |",
        "| ACL | Roles o grupos que pueden recuperar el documento. |",
        "| Finalidad | Usos permitidos del documento. |",
        "| Vigencia | `valid_from`, `valid_to`, `status` y reemplazos. |",
        "| Sensibilidad | Clasificación de datos y necesidad de redacción. |",
        "| Test de retrieval | Escenario que demuestra que rol no autorizado no recupera el chunk. |",
        "",
        "## Revisión de una respuesta problemática",
        "",
        "| Pregunta | Campo que buscaría |",
        "|---|---|",
        "| ¿Qué política estaba activa? | `policy_version` |",
        "| ¿Qué plantilla construyó el contexto? | `prompt_version` |",
        "| ¿Qué documentos entraron? | `retrieved_docs` |",
        "| ¿Qué documentos se bloquearon? | `blocked_docs` o decisión equivalente |",
        "| ¿Qué tool propuso el modelo? | `tool_call` |",
        "| ¿Qué decidió la aplicación? | `tool_decision` y `policy_decision` |",
        "| ¿Hubo aprobación? | `approval_id` |",
        "| ¿Qué validación falló? | `output_validation` |",
        "",
        "## Gate mínimo antes de publicar",
        "",
        "1. Ejecutar `python3 ops/run_appsec_gate.py --write`.",
        "2. Revisar `output/appsec_gate_report.md`.",
        "3. Corregir bloqueos no esperados.",
        "4. Revisar `output/tool_contract_matrix.csv` con arquitectura.",
        "5. Revisar `output/rag_retrieval_checks.md` con owner del corpus.",
        "6. Revisar `output/market_tooling_review.md` antes de incorporar producto externo.",
        "7. Guardar `output/trace_sample.jsonl` como contrato mínimo de observabilidad.",
        "",
        "## Qué no dejaría como decisión del modelo",
        "",
        "- Permisos de usuario.",
        "- ACL de documentos.",
        "- Destinos externos permitidos.",
        "- Ejecución de acciones sensibles.",
        "- Retención de trazas.",
        "- Aprobación de cambios de estado.",
        "- Selección de datos personales que pueden conservarse.",
    ]
    (OUTPUT / "day_to_day_playbook.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_jsonl(path, rows):
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="Escribe artefactos en output/")
    parser.add_argument("--fail-on-blocker", action="store_true", help="Devuelve código 1 si hay bloqueos")
    args = parser.parse_args()

    policy = load_json(POLICY_PATH)
    scenarios = load_jsonl(SCENARIOS_PATH)
    documents = {doc["doc_id"]: doc for doc in load_jsonl(DOCUMENTS_PATH)}
    market_tools = load_csv(MARKET_TOOLS_PATH)
    results, traces = evaluate(policy, scenarios, documents)
    blockers = sum(1 for result in results if result["decision"] == "block")
    approvals = sum(1 for result in results if result["decision"] == "needs_approval")

    summary = {
        "policy_version": policy["policy_version"],
        "scenario_count": len(results),
        "blocker_count": blockers,
        "approval_count": approvals,
        "mismatch_count": sum(1 for result in results if not result["matches_expected"]),
        "all_expected_decisions_matched": all(result["matches_expected"] for result in results),
        "results": results,
    }

    if args.write:
        OUTPUT.mkdir(exist_ok=True)
        write_json(OUTPUT / "appsec_gate.json", summary)
        write_jsonl(OUTPUT / "trace_sample.jsonl", traces)
        write_tool_matrix(policy)
        write_report(results)
        write_rag_checks(results)
        write_market_tooling_review(market_tools)
        write_day_to_day_playbook()

    print(json.dumps({k: summary[k] for k in summary if k != "results"}, indent=2, ensure_ascii=False))

    if args.fail_on_blocker and blockers:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
