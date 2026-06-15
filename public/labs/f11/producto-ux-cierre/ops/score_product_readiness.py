#!/usr/bin/env python3
import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def as_float(row, key):
    return float(row[key])


def yes(value):
    return str(value).strip().lower() in {"yes", "true", "1", "si", "sí"}


def clamp(value, low=0.0, high=1.0):
    return max(low, min(high, value))


def load_policy(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_candidates(path):
    with Path(path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def score_candidate(candidate, policy):
    thresholds = policy["thresholds"]
    weights = policy["weights"]
    evidence_items = set(candidate["evidence_items"].split("|"))
    required_evidence = set(policy["required_evidence"])

    task_success = as_float(candidate, "task_success")
    groundedness = as_float(candidate, "groundedness")
    abstention = as_float(candidate, "abstention")
    latency = as_float(candidate, "latency_p95_ms")
    cost = as_float(candidate, "cost_per_task_eur")
    trace_coverage = as_float(candidate, "trace_coverage")
    ops_readiness = as_float(candidate, "ops_readiness")
    ux_recovery = as_float(candidate, "ux_recovery_score")
    expected_value = as_float(candidate, "expected_value_eur")

    value_score = clamp(task_success * expected_value / 1.0)
    quality_score = (clamp(groundedness / thresholds["min_groundedness"]) + clamp(abstention / thresholds["min_abstention"])) / 2
    cost_score = clamp(thresholds["max_cost_per_task_eur"] / max(cost, 0.01))
    operations_score = (clamp(trace_coverage / thresholds["min_trace_coverage"]) + clamp(ops_readiness / thresholds["min_ops_readiness"])) / 2
    governance_score = 1.0 if yes(candidate["privacy_evidence"]) and required_evidence.issubset(evidence_items) else 0.45
    ux_score = clamp(ux_recovery / thresholds["min_ux_recovery_score"])

    weighted = (
        value_score * weights["value"]
        + quality_score * weights["quality"]
        + cost_score * weights["cost"]
        + operations_score * weights["operations"]
        + governance_score * weights["governance"]
        + ux_score * weights["ux"]
    )

    blockers = []
    conditions = []

    checks = [
        ("task_success", task_success, thresholds["min_task_success"], ">="),
        ("groundedness", groundedness, thresholds["min_groundedness"], ">="),
        ("abstention", abstention, thresholds["min_abstention"], ">="),
        ("trace_coverage", trace_coverage, thresholds["min_trace_coverage"], ">="),
        ("ops_readiness", ops_readiness, thresholds["min_ops_readiness"], ">="),
        ("ux_recovery_score", ux_recovery, thresholds["min_ux_recovery_score"], ">="),
        ("cost_per_task_eur", cost, thresholds["max_cost_per_task_eur"], "<="),
        ("latency_p95_ms", latency, thresholds["max_latency_p95_ms"], "<="),
    ]

    for name, observed, expected, operator in checks:
        passed = observed >= expected if operator == ">=" else observed <= expected
        if not passed:
            severity = "blocker" if name in {"task_success", "groundedness", "abstention", "ux_recovery_score"} else "condition"
            item = {
                "metric": name,
                "observed": observed,
                "expected": expected,
                "operator": operator,
                "severity": severity,
            }
            if severity == "blocker":
                blockers.append(item)
            else:
                conditions.append(item)

    missing_evidence = sorted(required_evidence - evidence_items)
    if missing_evidence or not yes(candidate["privacy_evidence"]):
        blockers.append({
            "metric": "evidence",
            "observed": sorted(evidence_items),
            "expected": sorted(required_evidence),
            "missing": missing_evidence,
            "severity": "blocker",
        })

    score = round(weighted, 1)
    if blockers:
        decision = "do_not_pilot"
    elif score >= thresholds["min_readiness_score"] and not conditions:
        decision = "pilot_limited"
    else:
        decision = "pilot_with_conditions"

    useful_margin = round(task_success * expected_value - cost, 3)

    return {
        "feature_id": candidate["feature_id"],
        "title": candidate["title"],
        "decision": decision,
        "readiness_score": score,
        "scores": {
            "value": round(value_score, 3),
            "quality": round(quality_score, 3),
            "cost": round(cost_score, 3),
            "operations": round(operations_score, 3),
            "governance": round(governance_score, 3),
            "ux": round(ux_score, 3),
        },
        "blockers": blockers,
        "conditions": conditions,
        "unit_economics": {
            "expected_value_eur": expected_value,
            "task_success": task_success,
            "cost_per_task_eur": cost,
            "useful_margin_eur": useful_margin,
        },
        "recommended_scope": recommended_scope(candidate, decision),
    }


def recommended_scope(candidate, decision):
    if decision == "pilot_limited":
        return "Piloto limitado a tareas con evidencia documental recuperable, revisión de casos incompletos y rollback operativo."
    if decision == "pilot_with_conditions":
        return "Preparar piloto solo cuando se cierren condiciones y se repita el gate."
    return "No pasar a piloto; usar alternativa sin IA o rediseñar alcance."


def write_outputs(results, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    best = sorted(results, key=lambda item: item["readiness_score"], reverse=True)[0]

    (output_dir / "product_readiness_report.json").write_text(
        json.dumps({"candidates": results, "selected_candidate": best["feature_id"]}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    with (output_dir / "unit_economics.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["feature_id", "expected_value_eur", "task_success", "cost_per_task_eur", "useful_margin_eur"])
        writer.writeheader()
        for item in results:
            row = {"feature_id": item["feature_id"], **item["unit_economics"]}
            writer.writerow(row)

    (output_dir / "metric_tree.md").write_text(metric_tree(best), encoding="utf-8")
    (output_dir / "product_release_decision.md").write_text(decision_markdown(best), encoding="utf-8")
    (output_dir / "final_product_packet.md").write_text(final_packet(best), encoding="utf-8")


def decision_markdown(best):
    return f"""# Decisión de producto

Función recomendada: `{best['feature_id']}`.

Decisión: `{best['decision']}`.

Score de readiness: {best['readiness_score']}.

## Alcance

{best['recommended_scope']}

## Condiciones

{format_items(best['conditions'])}

## Bloqueos

{format_items(best['blockers'])}

## Por qué no basta una demo

La decisión combina valor, calidad, coste, trazas, privacidad, operación y recuperación. Si cualquiera de esas capas falta, el piloto no demuestra producto; solo demuestra que el modelo genera una respuesta.
"""


def metric_tree(best):
    return f"""# Árbol de métricas

## Métrica norte

Tareas de matrícula resueltas con evidencia suficiente y sin escalado innecesario.

## Guardrails

| Capa | Métrica | Valor observado |
|---|---:|---:|
| Valor | margen útil por tarea | {best['unit_economics']['useful_margin_eur']} EUR |
| Calidad | score combinado | {best['scores']['quality']} |
| Coste | score de coste | {best['scores']['cost']} |
| Operación | score operativo | {best['scores']['operations']} |
| Gobernanza | score de evidencia | {best['scores']['governance']} |
| UX | score de recuperación | {best['scores']['ux']} |

## Lectura

No medimos solo uso. Medimos si una tarea termina con evidencia, coste razonable, trazas, privacidad y posibilidad de recuperación.
"""


def final_packet(best):
    return f"""# Paquete final de producto

## Resumen

La función `{best['feature_id']}` queda con decisión `{best['decision']}` y score {best['readiness_score']}.

## Evidencia mínima

- Brief de producto con alternativa sin IA.
- Árbol de métricas.
- Snapshot de evaluación.
- Unidad económica.
- Revisión de privacidad.
- Contrato de trazas.
- Plan de rollback.
- Caminos de recuperación UX.

## Decisión operativa

{best['recommended_scope']}
"""


def format_items(items):
    if not items:
        return "- Ninguno."
    lines = []
    for item in items:
        metric = item.get("metric", "evidence")
        lines.append(f"- `{metric}`: observado `{item.get('observed')}`, esperado `{item.get('operator', '')} {item.get('expected', '')}`.")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--policy", default=ROOT / "contracts/product_ai_release_policy.json")
    parser.add_argument("--candidates", default=ROOT / "data/feature_candidates.csv")
    parser.add_argument("--output-dir", default=ROOT / "output")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--fail-on-blocker", action="store_true")
    args = parser.parse_args()

    policy = load_policy(args.policy)
    candidates = load_candidates(args.candidates)
    results = [score_candidate(candidate, policy) for candidate in candidates]
    if args.write:
        write_outputs(results, Path(args.output_dir))

    print(json.dumps({"candidates": results}, indent=2, ensure_ascii=False))
    if args.fail_on_blocker and any(result["decision"] == "do_not_pilot" for result in results):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
