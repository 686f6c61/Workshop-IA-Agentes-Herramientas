#!/usr/bin/env python3
import argparse
import csv
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTRACT = ROOT / "contracts" / "policy_serving_contract.json"
DEFAULT_REFERENCE = ROOT / "data" / "reference_window.json"
DEFAULT_CURRENT = ROOT / "data" / "current_window_ok.json"
DEFAULT_PLAN = ROOT / "data" / "release_plan.json"
DEFAULT_OUTPUT = ROOT / "output"


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def distribution(rows, key_name, count_name):
    total = sum(float(row[count_name]) for row in rows)
    if total == 0:
        return {}
    return {row[key_name]: float(row[count_name]) / total for row in rows}


def population_stability_index(reference_dist, current_dist, epsilon=1e-6):
    keys = sorted(set(reference_dist) | set(current_dist))
    score = 0.0
    for key in keys:
        reference_value = max(reference_dist.get(key, 0.0), epsilon)
        current_value = max(current_dist.get(key, 0.0), epsilon)
        score += (current_value - reference_value) * math.log(current_value / reference_value)
    return round(score, 6)


def slices_by_name(window):
    return {row["slice"]: row for row in window["slices"]}


def evaluate_slices(reference, current, contract):
    reference_slices = slices_by_name(reference)
    current_slices = slices_by_name(current)
    rows = []

    for slice_name in sorted(set(reference_slices) | set(current_slices)):
        reference_row = reference_slices.get(slice_name)
        current_row = current_slices.get(slice_name)
        if reference_row is None or current_row is None:
            rows.append({
                "slice": slice_name,
                "status": "block",
                "reason": "slice_missing",
                "requests": 0 if current_row is None else current_row["requests"],
                "reward_mean": "" if current_row is None else current_row["reward_mean"],
                "reward_delta": "",
                "case_pass_rate": "" if current_row is None else current_row["case_pass_rate"],
                "evidence_pass_rate": "" if current_row is None else current_row["evidence_pass_rate"],
                "p95_latency_ms": "" if current_row is None else current_row["p95_latency_ms"],
                "tool_error_rate": "" if current_row is None else current_row["tool_error_rate"],
                "fallback_rate": "" if current_row is None else current_row["fallback_rate"],
            })
            continue

        reward_delta = round(current_row["reward_mean"] - reference_row["reward_mean"], 6)
        failures = []
        if abs(reward_delta) > contract["max_reward_delta"]:
            failures.append("reward_delta")
        if current_row["reward_mean"] < contract["min_reward_mean"]:
            failures.append("reward_mean")
        if current_row["case_pass_rate"] < contract["min_case_pass_rate"]:
            failures.append("case_pass_rate")
        if current_row["evidence_pass_rate"] < contract["min_evidence_pass_rate"]:
            failures.append("evidence_pass_rate")
        if current_row["p95_latency_ms"] > contract["max_p95_latency_ms"]:
            failures.append("p95_latency_ms")
        if current_row["tool_error_rate"] > contract["max_tool_error_rate"]:
            failures.append("tool_error_rate")
        if current_row["fallback_rate"] > contract["max_fallback_rate"]:
            failures.append("fallback_rate")

        rows.append({
            "slice": slice_name,
            "status": "pass" if not failures else "block",
            "reason": ";".join(failures) if failures else "ok",
            "requests": current_row["requests"],
            "reward_mean": current_row["reward_mean"],
            "reward_delta": reward_delta,
            "case_pass_rate": current_row["case_pass_rate"],
            "evidence_pass_rate": current_row["evidence_pass_rate"],
            "p95_latency_ms": current_row["p95_latency_ms"],
            "tool_error_rate": current_row["tool_error_rate"],
            "fallback_rate": current_row["fallback_rate"],
        })
    return rows


def evaluate_rollout(plan, contract):
    stage_names = [stage["name"] for stage in plan.get("stages", [])]
    rows = []
    required = set(contract["required_stages"])
    present = set(stage_names)
    for stage in plan.get("stages", []):
        failures = []
        if stage["name"] not in required:
            failures.append("unexpected_stage")
        if stage.get("min_duration_minutes", 0) < 120 and stage["name"] != "shadow":
            failures.append("duration_too_short")
        if len(stage.get("exit_criteria", [])) < 3:
            failures.append("exit_criteria_too_weak")
        rows.append({
            "stage": stage["name"],
            "traffic_pct": stage.get("traffic_pct", ""),
            "min_duration_minutes": stage.get("min_duration_minutes", ""),
            "exit_criteria_count": len(stage.get("exit_criteria", [])),
            "status": "pass" if not failures else "block",
            "reason": ";".join(failures) if failures else "ok",
        })

    for missing in sorted(required - present):
        rows.append({
            "stage": missing,
            "traffic_pct": "",
            "min_duration_minutes": "",
            "exit_criteria_count": 0,
            "status": "block",
            "reason": "missing_required_stage",
        })
    return rows


def evaluate_plan(plan, contract):
    failures = []
    if not plan.get("fallback_policy_version"):
        failures.append("missing_fallback_policy_version")
    rollback = plan.get("rollback", {})
    if rollback.get("ready") is not True:
        failures.append("rollback_not_ready")
    if rollback.get("max_minutes_to_restore", 9999) > 15:
        failures.append("restore_too_slow")
    if len(rollback.get("conditions", [])) < 3:
        failures.append("rollback_conditions_too_weak")

    trace_sample = plan.get("trace_sample", {})
    missing_trace_fields = [
        field for field in contract["required_trace_fields"]
        if field not in trace_sample
    ]
    for field in missing_trace_fields:
        failures.append(f"missing_trace_field:{field}")

    return {
        "status": "pass" if not failures else "block",
        "failures": failures,
        "missing_trace_fields": missing_trace_fields,
    }


def audit(contract, reference, current, plan):
    slice_rows = evaluate_slices(reference, current, contract)
    rollout_rows = evaluate_rollout(plan, contract)
    plan_report = evaluate_plan(plan, contract)

    slice_dist_reference = distribution(
        [{"slice": row["slice"], "count": row["requests"]} for row in reference["slices"]],
        "slice",
        "count",
    )
    slice_dist_current = distribution(
        [{"slice": row["slice"], "count": row["requests"]} for row in current["slices"]],
        "slice",
        "count",
    )
    action_dist_reference = distribution(reference["actions"], "action", "count")
    action_dist_current = distribution(current["actions"], "action", "count")

    slice_psi = population_stability_index(slice_dist_reference, slice_dist_current)
    action_psi = population_stability_index(action_dist_reference, action_dist_current)
    drift_failures = []
    if slice_psi > contract["max_population_stability_index"]:
        drift_failures.append("slice_population_stability_index")
    if action_psi > contract["max_population_stability_index"]:
        drift_failures.append("action_population_stability_index")

    status = "pass"
    if any(row["status"] != "pass" for row in slice_rows):
        status = "block"
    if any(row["status"] != "pass" for row in rollout_rows):
        status = "block"
    if plan_report["status"] != "pass":
        status = "block"
    if drift_failures:
        status = "block"

    return {
        "status": status,
        "reference_window_id": reference["window_id"],
        "current_window_id": current["window_id"],
        "policy_candidate_version": current.get("policy_candidate_version", plan.get("policy_candidate_version")),
        "reward_card_version": current["reward_card_version"],
        "diagnostics": {
            "slice_population_stability_index": slice_psi,
            "action_population_stability_index": action_psi,
            "blocked_slices": sum(1 for row in slice_rows if row["status"] != "pass"),
            "blocked_rollout_stages": sum(1 for row in rollout_rows if row["status"] != "pass"),
            "plan_status": plan_report["status"],
        },
        "drift_failures": drift_failures,
        "plan_report": plan_report,
        "slice_rows": slice_rows,
        "rollout_rows": rollout_rows,
    }


def render_decision(report):
    lines = [
        "# Decisión de serving",
        "",
        f"Estado: `{report['status']}`",
        f"Ventana actual: `{report['current_window_id']}`",
        f"Política candidata: `{report['policy_candidate_version']}`",
        "",
        "| Diagnóstico | Valor |",
        "|---|---:|",
    ]
    for key, value in report["diagnostics"].items():
        lines.append(f"| `{key}` | {value} |")

    lines.extend(["", "## Lectura", ""])
    if report["status"] == "pass":
        lines.append("La política puede avanzar al siguiente tramo del rollout con monitorización por slice y política de reserva disponible.")
    else:
        lines.append("La política no debería avanzar. Revisa slices bloqueados, drift de población, plan de rollout, trazas y preparación de rollback.")
    return "\n".join(lines) + "\n"


def render_runbook(report, plan):
    rollback = plan.get("rollback", {})
    lines = [
        "# Serving runbook",
        "",
        "## Antes de aumentar tráfico",
        "",
        "- Comprobar que `serving_decision.md` está en `pass`.",
        "- Revisar `drift_scorecard.csv` por slice, no solo el agregado.",
        "- Confirmar que la política de reserva está versionada y disponible.",
        "- Confirmar que la feature flag puede bajar exposición sin redesplegar.",
        "",
        "## Si el gate bloquea",
        "",
        f"- Decisión de rollback: `{rollback.get('decision', 'no_definida')}`.",
        f"- Tiempo máximo de restauración: `{rollback.get('max_minutes_to_restore', 'n/a')}` minutos.",
        "- Congelar el tramo actual y no aumentar tráfico.",
        "- Guardar reporte, ventana actual y plan usado.",
        "- Abrir revisión técnica con slices bloqueados y condiciones incumplidas.",
        "",
        "## Condiciones declaradas",
        "",
    ]
    for condition in rollback.get("conditions", []):
        lines.append(f"- `{condition}`")
    if not rollback.get("conditions"):
        lines.append("- No hay condiciones suficientes declaradas.")
    return "\n".join(lines) + "\n"


def write_csv(path, rows):
    if not rows:
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_outputs(output_dir, report, plan):
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "serving_audit_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (output_dir / "serving_decision.md").write_text(render_decision(report), encoding="utf-8")
    (output_dir / "serving_runbook.md").write_text(render_runbook(report, plan), encoding="utf-8")
    write_csv(output_dir / "drift_scorecard.csv", report["slice_rows"])
    write_csv(output_dir / "rollout_scorecard.csv", report["rollout_rows"])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT))
    parser.add_argument("--reference", default=str(DEFAULT_REFERENCE))
    parser.add_argument("--current", default=str(DEFAULT_CURRENT))
    parser.add_argument("--plan", default=str(DEFAULT_PLAN))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    contract = read_json(args.contract)
    reference = read_json(args.reference)
    current = read_json(args.current)
    plan = read_json(args.plan)
    report = audit(contract, reference, current, plan)

    if args.write:
        write_outputs(Path(args.output), report, plan)

    print(f"status={report['status']}")
    print(f"slice_psi={report['diagnostics']['slice_population_stability_index']}")
    print(f"action_psi={report['diagnostics']['action_population_stability_index']}")
    print(f"blocked_slices={report['diagnostics']['blocked_slices']}")
    print(f"blocked_rollout_stages={report['diagnostics']['blocked_rollout_stages']}")


if __name__ == "__main__":
    main()
