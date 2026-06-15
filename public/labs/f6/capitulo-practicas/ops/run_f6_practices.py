#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output"


def ok(name, passed, detail):
    return {"name": name, "passed": bool(passed), "detail": detail}


def status(checks):
    return "valid" if all(item["passed"] for item in checks) else "invalid"


def emit(chapter, report):
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / f"{chapter}_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    lines = [
        f"# Decisión {chapter.upper()}: {report['title']}",
        "",
        f"Estado: `{report['status']}`.",
        "",
        "## Evidencias",
        "",
    ]
    for item in report["checks"]:
        mark = "OK" if item["passed"] else "FALLO"
        lines.append(f"- {mark}: {item['name']}. {item['detail']}")
    lines.extend(["", "## Decisión", "", report["decision"], ""])
    (OUTPUT / f"{chapter}_decision.md").write_text("\n".join(lines), encoding="utf-8")


def c01():
    artifact = {
        "files": ["AGENTS.md", "SHOULD.md", "manifest.yaml", "release_gate.py", "decision.md"],
        "agents_md": {"commands": ["npm test", "python3 scripts/audit_book_publication.py"], "evidence_required": True},
        "should": {"must": 4, "should": 3, "may": 2},
        "manifest": {"owner": "equipo-ia", "rollback": "v1.4.2", "slo": "p95<=4s"},
    }
    checks = [
        ok("archivos mínimos", len(artifact["files"]) >= 5, "El kit no se queda en una nota suelta."),
        ok("AGENTS.md operativo", artifact["agents_md"]["evidence_required"], "Pide comandos y evidencia."),
        ok("SHOULD.md verificable", artifact["should"]["must"] >= 3, "Separa obligaciones y expectativas."),
        ok("rollback declarado", bool(artifact["manifest"]["rollback"]), "Hay versión conocida de vuelta."),
    ]
    return report("Kit operativo inicial", artifact, checks, "El capítulo deja una base operable: instrucciones, comportamiento esperado, manifest, gate y decisión.")


def c02():
    states = ["queued", "running", "needs_review", "completed", "failed", "cancelled"]
    contract = {"idempotency_key": True, "retry_policy": "exponential_backoff", "max_queue_age_s": 300, "dead_letter_queue": True}
    checks = [
        ok("estados explícitos", {"queued", "running", "completed", "failed"}.issubset(states), "La run no vive como string libre."),
        ok("idempotencia", contract["idempotency_key"], "Los retries no duplican efectos."),
        ok("DLQ", contract["dead_letter_queue"], "Hay lugar para mensajes no procesables."),
        ok("edad máxima de cola", contract["max_queue_age_s"] <= 300, "La cola no es memoria eterna."),
    ]
    return report("Contrato de runtime", {"states": states, "contract": contract}, checks, "El runtime se puede implementar y probar: estados, cola, retries, idempotencia y error quedan explícitos.")


def c03():
    scenario = {"prompt_tokens": 1800, "output_tokens": 450, "rps": 3.0, "ttft_ms": 700, "decode_tps": 55}
    prefill_s = scenario["prompt_tokens"] / 9000
    decode_s = scenario["output_tokens"] / scenario["decode_tps"]
    service_s = round(prefill_s + decode_s + scenario["ttft_ms"] / 1000, 2)
    workers = 64
    capacity_rps = round(workers / service_s, 2)
    checks = [
        ok("servicio calculado", service_s > 0, f"Tiempo estimado por request: {service_s}s."),
        ok("capacidad suficiente", capacity_rps >= scenario["rps"], f"Capacidad estimada: {capacity_rps} rps."),
        ok("margen visible", capacity_rps / scenario["rps"] >= 2, "Hay margen antes de saturar."),
        ok("tokens separados", scenario["prompt_tokens"] > scenario["output_tokens"], "Se distinguen prefill y decode."),
    ]
    return report("Estimación de capacidad", {"scenario": scenario, "service_s": service_s, "workers": workers, "capacity_rps": capacity_rps}, checks, "La capacidad inicial es defendible, pero exige medir p95 real después del despliegue.")


def c04():
    telemetry = {
        "slis": ["availability", "latency_p95", "groundedness_pass_rate", "cost_per_success", "queue_age_p95"],
        "slo": {"availability": 0.995, "latency_p95_ms": 4000, "groundedness_pass_rate": 0.97},
        "error_budget": {"window_days": 30, "allowed_bad_minutes": 216},
        "redaction": ["email", "student_id", "prompt_free_text"],
    }
    checks = [
        ok("SLIs útiles", len(telemetry["slis"]) >= 5, "Mide calidad, coste y operación."),
        ok("SLO medible", telemetry["slo"]["latency_p95_ms"] > 0, "No es frase de marketing."),
        ok("presupuesto de error", telemetry["error_budget"]["allowed_bad_minutes"] > 0, "Hay margen cuantificado."),
        ok("redacción", "prompt_free_text" in telemetry["redaction"], "Observabilidad sin fuga de datos."),
    ]
    return report("Contrato de telemetría", telemetry, checks, "La telemetría permite decidir: disponibilidad, latencia, groundedness, coste, cola y privacidad quedan conectados.")


def c05():
    routes = [
        {"task": "faq_policy", "primary": "rag_fast", "fallback": "rag_safe", "budget_eur": 0.03},
        {"task": "student_balance", "primary": "tool_sql", "fallback": "human_review", "budget_eur": 0.02},
        {"task": "complex_case", "primary": "agent_supervised", "fallback": "human_review", "budget_eur": 0.12},
    ]
    checks = [
        ok("fallback por ruta", all(r["fallback"] for r in routes), "Toda ruta tiene degradación."),
        ok("presupuesto por tarea", all(r["budget_eur"] > 0 for r in routes), "El router no decide gratis."),
        ok("dato sensible a humano", next(r for r in routes if r["task"] == "student_balance")["fallback"] == "human_review", "Privacidad y revisión conectan."),
        ok("agente solo en caso complejo", next(r for r in routes if r["task"] == "complex_case")["primary"] == "agent_supervised", "No se usa agente por reflejo."),
    ]
    return report("Política de routing", {"routes": routes}, checks, "La política enruta por tarea, coste, riesgo y fallback; no por preferencia de proveedor.")


def c06():
    scorecard = {"contract": 1.0, "evals": 0.96, "latency": 0.94, "cost": 0.98, "rollback": 1.0, "observability": 0.95}
    gates = {"min_all": 0.93, "must_have_rollback": True}
    blocked = [k for k, v in scorecard.items() if v < gates["min_all"]]
    checks = [
        ok("scorecard completa", len(scorecard) >= 6, "El release mira más que accuracy."),
        ok("sin bloqueos", not blocked, f"Bloqueos: {blocked}."),
        ok("rollback obligatorio", gates["must_have_rollback"] and scorecard["rollback"] == 1.0, "No se publica sin vuelta atrás."),
        ok("observabilidad pasa", scorecard["observability"] >= gates["min_all"], "El cambio deja evidencia."),
    ]
    return report("Gate de release", {"scorecard": scorecard, "gates": gates, "blocked": blocked}, checks, "La versión puede pasar a canary: cumple contrato, evals, latencia, coste, rollback y observabilidad.")


def c07():
    rollout = [
        {"stage": "shadow", "traffic": 0.0, "gate": "no_side_effects"},
        {"stage": "canary", "traffic": 0.05, "gate": "slo_and_eval_pass"},
        {"stage": "ramp", "traffic": 0.25, "gate": "no_p1_regression"},
        {"stage": "rollback", "traffic": 0.0, "gate": "known_good_version"},
    ]
    checks = [
        ok("shadow sin efecto", rollout[0]["gate"] == "no_side_effects", "Se observa antes de impactar."),
        ok("canary pequeño", rollout[1]["traffic"] <= 0.05, "Exposición limitada."),
        ok("ramp con gate", rollout[2]["gate"] == "no_p1_regression", "Subir tráfico exige evidencia."),
        ok("rollback definido", rollout[-1]["stage"] == "rollback", "Hay ruta de vuelta."),
    ]
    return report("Rollout progresivo", {"rollout": rollout}, checks, "El cambio progresa por evidencia: shadow, canary, ramp y rollback tienen gates separados.")


def c08():
    queue = {
        "items": [
            {"id": "rev-1", "risk": "privacy", "age_min": 12, "owner": "guardia"},
            {"id": "rev-2", "risk": "external_effect", "age_min": 31, "owner": "responsable"},
        ],
        "slo_minutes": 45,
        "degraded_mode": "disable_persistent_actions",
    }
    checks = [
        ok("cola con owner", all(item["owner"] for item in queue["items"]), "No hay revisión anónima."),
        ok("SLO cumple", max(item["age_min"] for item in queue["items"]) <= queue["slo_minutes"], "La revisión tiene tiempo objetivo."),
        ok("modo degradado", bool(queue["degraded_mode"]), "Si la cola cae, el sistema sabe qué apagar."),
        ok("riesgos clasificados", {i["risk"] for i in queue["items"]} == {"privacy", "external_effect"}, "La revisión depende del riesgo."),
    ]
    return report("Cola de revisión humana", queue, checks, "La revisión humana queda operable: owner, SLO, riesgo y modo degradado están escritos.")


def c09():
    incident = {
        "symptoms": ["latency_p95_high", "groundedness_drop"],
        "mitigations": ["route_to_safe_model", "lower_canary", "freeze_release"],
        "postmortem": {"impact": "20 min degradados", "owner": "equipo-ia", "actions": 3},
        "regression_case": {"id": "reg-incident-001", "added_to_evalops": True},
    }
    checks = [
        ok("síntomas concretos", len(incident["symptoms"]) >= 2, "No se diagnostica con sensaciones."),
        ok("mitigación ejecutable", "freeze_release" in incident["mitigations"], "Puede detener cambios."),
        ok("postmortem con acciones", incident["postmortem"]["actions"] >= 2, "La mejora queda asignada."),
        ok("caso de regresión", incident["regression_case"]["added_to_evalops"], "El fallo entra en EvalOps."),
    ]
    return report("Incidencia a mejora continua", incident, checks, "La incidencia produce mitigación, postmortem y un caso de regresión; no se queda en relato.")


def report(title, artifact, checks, decision):
    return {"title": title, "artifact": artifact, "checks": checks, "status": status(checks), "decision": decision}


BUILDERS = {
    "c01": c01,
    "c02": c02,
    "c03": c03,
    "c04": c04,
    "c05": c05,
    "c06": c06,
    "c07": c07,
    "c08": c08,
    "c09": c09,
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--chapter", choices=sorted(BUILDERS))
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--fail-on-invalid", action="store_true")
    args = parser.parse_args()

    selected = sorted(BUILDERS) if args.all or not args.chapter else [args.chapter]
    summary = {}
    invalid = []
    for chapter in selected:
        item = BUILDERS[chapter]()
        item["chapter"] = chapter
        summary[chapter] = item["status"]
        if args.write:
            emit(chapter, item)
        if item["status"] != "valid":
            invalid.append(chapter)

    if args.write:
        OUTPUT.mkdir(parents=True, exist_ok=True)
        (OUTPUT / "all_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    if invalid and args.fail_on_invalid:
        raise SystemExit(f"Prácticas inválidas: {', '.join(invalid)}")


if __name__ == "__main__":
    main()
