import argparse
import json
import sys
from pathlib import Path


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, payload):
    Path(path).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def includes_all(values, required):
    return set(required).issubset(set(values or []))


def add(checks, section, passes, weight, detail, next_action):
    checks.append({
        "section": section,
        "passes": passes,
        "weight": weight,
        "earned": weight if passes else 0,
        "detail": detail,
        "next_action": next_action if not passes else "ok",
    })


def build_report(manifest, policy):
    weights = policy["weights"]
    checks = []

    add(
        checks,
        "identity",
        all(manifest.get(key) for key in ["service", "release", "owner"]),
        weights["identity"],
        {"required": ["service", "release", "owner"]},
        "definir servicio, release y owner",
    )

    slo = manifest.get("slo", {})
    add(
        checks,
        "slo",
        all(key in slo for key in ["latency_p95_ms", "availability", "contract_fail_rate_max", "cost_p95_eur", "review_queue_age_p95_minutes"]),
        weights["slo"],
        {"observed": sorted(slo)},
        "añadir coste p95 y edad máxima de cola de revisión",
    )

    obs = manifest.get("observability", {})
    obs_passes = (
        includes_all(obs.get("required_attributes"), policy["required_trace_attributes"])
        and includes_all(obs.get("dashboards"), policy["required_dashboards"])
        and includes_all(obs.get("alerts"), policy["required_alerts"])
    )
    add(
        checks,
        "observability",
        obs_passes,
        weights["observability"],
        {
            "attributes": obs.get("required_attributes", []),
            "dashboards": obs.get("dashboards", []),
            "alerts": obs.get("alerts", []),
        },
        "completar atributos de traza, dashboards y alertas",
    )

    rollback = manifest.get("rollback", {})
    add(
        checks,
        "rollback",
        all(key in rollback for key in ["last_known_good", "rollback_command", "rollback_tested_at", "max_rollback_minutes"]),
        weights["rollback"],
        {"observed": sorted(rollback)},
        "añadir comando probado, fecha de prueba y tiempo máximo de rollback",
    )

    evalops = manifest.get("evalops", {})
    add(
        checks,
        "evalops",
        includes_all(evalops.get("datasets"), policy["required_eval_datasets"]) and all(key in evalops for key in ["release_gate", "baseline_release", "candidate_release"]),
        weights["evalops"],
        {"datasets": evalops.get("datasets", []), "release_gate": evalops.get("release_gate")},
        "añadir datasets de regresión, muestra de producción, baseline y candidate",
    )

    incident = manifest.get("incident", {})
    add(
        checks,
        "incident",
        all(key in incident for key in ["runbook", "oncall", "severity_matrix", "update_cadence_minutes"]),
        weights["incident"],
        {"observed": sorted(incident)},
        "añadir matriz de severidad y cadencia de comunicación",
    )

    continuity = manifest.get("continuity", {})
    add(
        checks,
        "continuity",
        all(key in continuity for key in ["rto_minutes", "rpo_minutes", "fallback_routes", "continuity_drill"]) and bool(continuity.get("fallback_routes")),
        weights["continuity"],
        {"observed": sorted(continuity)},
        "añadir RPO, rutas de fallback y drill de continuidad",
    )

    handoff = manifest.get("handoff", {})
    card = handoff.get("approval_card_template", {})
    add(
        checks,
        "handoff",
        bool(handoff.get("queues")) and includes_all(card.keys(), policy["required_handoff_fields"]),
        weights["handoff"],
        {"queues": handoff.get("queues", []), "approval_fields": sorted(card)},
        "añadir tarjeta de aprobación con campos mínimos",
    )

    earned = sum(item["earned"] for item in checks)
    total = sum(item["weight"] for item in checks)
    score = round(earned / total, 4)
    thresholds = policy["gate_thresholds"]
    gate = "ready" if score >= thresholds["ready"] else "ready_with_conditions" if score >= thresholds["ready_with_conditions"] else "not_ready"
    return {
        "service": manifest.get("service"),
        "release": manifest.get("release"),
        "score": score,
        "gate": gate,
        "passed_weight": earned,
        "total_weight": total,
        "checks": checks,
        "next_actions": [item["next_action"] for item in checks if not item["passes"]],
    }


def render_decision(report):
    lines = [
        "# Decisión de readiness operacional",
        "",
        f"Servicio: `{report['service']}`.",
        f"Release: `{report['release']}`.",
        f"Gate: **{report['gate']}**.",
        f"Score: `{report['score']}`.",
        "",
        "## Checks",
        "",
        "| Sección | Estado | Peso | Siguiente acción |",
        "|---|---|---:|---|",
    ]
    for item in report["checks"]:
        state = "pasa" if item["passes"] else "falta"
        lines.append(f"| `{item['section']}` | {state} | {item['earned']} / {item['weight']} | {item['next_action']} |")
    lines.extend([
        "",
        "## Decisión",
        "",
    ])
    if report["gate"] == "ready":
        lines.append("Publicaría la release si el gate de EvalOps también compara baseline contra candidate el mismo día.")
    elif report["gate"] == "ready_with_conditions":
        lines.append("Permitiría solo canary pequeño con condiciones escritas y owner para cada hueco.")
    else:
        lines.append("No publicaría. Primero completaría manifiesto, observabilidad, rollback, continuidad y handoff.")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default="contracts/readiness_manifest_incomplete.json")
    parser.add_argument("--policy", default="contracts/readiness_policy.json")
    parser.add_argument("--output", default="output/operational_readiness.json")
    parser.add_argument("--decision-output", default="output/readiness_decision.md")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--fail-on-not-ready", action="store_true")
    args = parser.parse_args()

    report = build_report(read_json(args.manifest), read_json(args.policy))
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if args.write:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        write_json(args.output, report)
        Path(args.decision_output).write_text(render_decision(report), encoding="utf-8")
    if args.fail_on_not_ready and report["gate"] == "not_ready":
        sys.exit(2)


if __name__ == "__main__":
    main()
