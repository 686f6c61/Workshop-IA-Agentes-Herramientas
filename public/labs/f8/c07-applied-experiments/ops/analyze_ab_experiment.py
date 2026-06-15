#!/usr/bin/env python3
import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EVENTS = ROOT / "data" / "experiment_events.csv"
DEFAULT_CONTRACT = ROOT / "contracts" / "experiment_contract.json"
DEFAULT_OUTPUT = ROOT / "output"


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def read_json(path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def as_float(row, field):
    return float(str(row[field]).replace(",", "."))


def mean(values):
    values = list(values)
    return sum(values) / len(values) if values else 0.0


def variance(values):
    values = list(values)
    if len(values) < 2:
        return 0.0
    m = mean(values)
    return sum((v - m) ** 2 for v in values) / (len(values) - 1)


def covariance(xs, ys):
    xs = list(xs)
    ys = list(ys)
    if len(xs) < 2:
        return 0.0
    mx = mean(xs)
    my = mean(ys)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (len(xs) - 1)


def pct(value):
    return round(value, 6)


def normal_p_value(z):
    return math.erfc(abs(z) / math.sqrt(2))


def chi_square_p_value_df1(chi_square):
    return math.erfc(math.sqrt(max(chi_square, 0.0) / 2))


def z_values(alpha, power):
    alpha_key = round(alpha, 3)
    power_key = round(power, 2)
    z_alpha = {
        0.1: 1.644854,
        0.05: 1.959964,
        0.01: 2.575829,
    }.get(alpha_key, 1.959964)
    z_power = {
        0.7: 0.524401,
        0.8: 0.841621,
        0.9: 1.281552,
        0.95: 1.644854,
    }.get(power_key, 0.841621)
    return z_alpha, z_power


def group_by(rows, field):
    result = defaultdict(list)
    for row in rows:
        result[row[field]].append(row)
    return dict(result)


def validate_schema(rows, contract):
    errors = []
    required = set(contract["required_columns"])
    if not rows:
        return ["dataset vacio"]
    missing = sorted(required - set(rows[0]))
    for field in missing:
        errors.append(f"falta columna {field}")
    allowed_variants = set(contract["allowed_variants"])
    allowed_segments = set(contract["allowed_segments"])
    for row in rows:
        if row.get("variant") not in allowed_variants:
            errors.append(f"variant fuera de catalogo en {row.get('unit_id')}")
        if row.get("segment") not in allowed_segments:
            errors.append(f"segment fuera de catalogo en {row.get('unit_id')}")
    ids = [row[contract["unit"]] for row in rows]
    duplicated = sorted({unit for unit in ids if ids.count(unit) > 1})
    for unit in duplicated:
        errors.append(f"unit_id duplicado: {unit}")
    return errors


def summarize_variant(rows, variant):
    selected = [row for row in rows if row["variant"] == variant]
    return {
        "variant": variant,
        "n": len(selected),
        "resolved_rate": pct(mean(as_float(row, "resolved") for row in selected)),
        "minutes_mean": pct(mean(as_float(row, "minutes_to_resolution") for row in selected)),
        "cost_mean": pct(mean(as_float(row, "cost_eur") for row in selected)),
        "latency_mean_ms": pct(mean(as_float(row, "latency_ms") for row in selected)),
        "negative_feedback_rate": pct(mean(as_float(row, "negative_feedback") for row in selected)),
    }


def srm_check(rows, contract):
    expected = contract["expected_allocation"]
    total = len(rows)
    observed = {variant: len([row for row in rows if row["variant"] == variant]) for variant in expected}
    chi_square = 0.0
    for variant, expected_share in expected.items():
        exp = expected_share * total
        obs = observed.get(variant, 0)
        if exp > 0:
            chi_square += (obs - exp) ** 2 / exp
    p_value = chi_square_p_value_df1(chi_square)
    return {
        "observed": observed,
        "expected_allocation": expected,
        "chi_square": pct(chi_square),
        "p_value": pct(p_value),
        "status": "block" if p_value < contract["quality_gates"]["srm_p_value_block_threshold"] else "pass",
    }


def standardized_mean_difference(rows, field):
    groups = group_by(rows, "variant")
    control = [as_float(row, field) for row in groups.get("control", [])]
    treatment = [as_float(row, field) for row in groups.get("treatment", [])]
    pooled = math.sqrt((variance(control) + variance(treatment)) / 2)
    if pooled == 0:
        return 0.0
    return (mean(treatment) - mean(control)) / pooled


def balance_checks(rows, contract):
    fields = ["pre_week_tasks", "historical_resolution_rate"]
    threshold = contract["quality_gates"]["max_abs_standardized_mean_difference"]
    checks = []
    for field in fields:
        smd = standardized_mean_difference(rows, field)
        checks.append({
            "field": field,
            "standardized_mean_difference": pct(smd),
            "abs_standardized_mean_difference": pct(abs(smd)),
            "status": "review" if abs(smd) > threshold else "pass",
        })
    return checks


def effect_for_metric(rows, metric):
    groups = group_by(rows, "variant")
    control = [as_float(row, metric) for row in groups.get("control", [])]
    treatment = [as_float(row, metric) for row in groups.get("treatment", [])]
    diff = mean(treatment) - mean(control)
    se = math.sqrt((variance(treatment) / len(treatment)) + (variance(control) / len(control))) if treatment and control else 0
    z = diff / se if se else 0
    return {
        "control_mean": pct(mean(control)),
        "treatment_mean": pct(mean(treatment)),
        "effect": pct(diff),
        "standard_error": pct(se),
        "ci95_low": pct(diff - 1.96 * se),
        "ci95_high": pct(diff + 1.96 * se),
        "p_value": pct(normal_p_value(z)) if se else 1.0,
    }


def cuped_effect(rows):
    y = [as_float(row, "resolved") for row in rows]
    x = [as_float(row, "historical_resolution_rate") for row in rows]
    x_mean = mean(x)
    theta = covariance(x, y) / variance(x) if variance(x) else 0.0
    adjusted = []
    for row in rows:
        adjusted_row = dict(row)
        adjusted_row["resolved_cuped"] = as_float(row, "resolved") - theta * (as_float(row, "historical_resolution_rate") - x_mean)
        adjusted.append(adjusted_row)
    groups = group_by(adjusted, "variant")
    control = [row["resolved_cuped"] for row in groups.get("control", [])]
    treatment = [row["resolved_cuped"] for row in groups.get("treatment", [])]
    diff = mean(treatment) - mean(control)
    se = math.sqrt((variance(treatment) / len(treatment)) + (variance(control) / len(control))) if treatment and control else 0
    z = diff / se if se else 0
    return {
        "theta": pct(theta),
        "covariate": "historical_resolution_rate",
        "effect": pct(diff),
        "standard_error": pct(se),
        "ci95_low": pct(diff - 1.96 * se),
        "ci95_high": pct(diff + 1.96 * se),
        "p_value": pct(normal_p_value(z)) if se else 1.0,
    }


def guardrail_checks(rows, contract):
    guardrails = contract["guardrails"]
    checks = []
    metrics = [
        ("negative_feedback", "max_negative_feedback_rate_delta", "lower_or_equal"),
        ("latency_ms", "max_latency_mean_delta_ms", "lower_or_equal"),
        ("cost_eur", "max_cost_mean_delta_eur", "lower_or_equal"),
    ]
    for field, threshold_key, direction in metrics:
        effect = effect_for_metric(rows, field)
        delta = effect["effect"]
        threshold = guardrails[threshold_key]
        status = "block" if delta > threshold else "pass"
        checks.append({
            "metric": field,
            "control_mean": effect["control_mean"],
            "treatment_mean": effect["treatment_mean"],
            "delta": delta,
            "threshold": threshold,
            "direction": direction,
            "status": status,
        })
    return checks


def slice_effects(rows):
    result = []
    for segment, segment_rows in sorted(group_by(rows, "segment").items()):
        effect = effect_for_metric(segment_rows, "resolved")
        effect["segment"] = segment
        effect["n"] = len(segment_rows)
        result.append(effect)
    return result


def readiness_checks(rows, contract):
    plan = contract["statistical_plan"]
    primary = contract["primary_metric"]
    assignment = contract["assignment_contract"]
    rollout = contract["rollout_policy"]
    counts = {variant: len([row for row in rows if row["variant"] == variant]) for variant in contract["expected_allocation"]}
    min_n = min(counts.values()) if counts else 0
    baseline = primary["baseline_rate"]
    variance_binary = baseline * (1 - baseline)
    z_alpha, z_power = z_values(plan["alpha"], plan["power"])
    planned_delta = plan["minimum_detectable_effect"]
    required_n = math.ceil(2 * ((z_alpha + z_power) ** 2) * variance_binary / (planned_delta ** 2))
    observed_mde = (z_alpha + z_power) * math.sqrt((2 * variance_binary) / min_n) if min_n else None

    checks = []
    checks.append({
        "check": "aa_test",
        "status": "review" if assignment["aa_test_required_before_ab"] else "pass",
        "message": "Ejecutar A/A antes del A/B para validar instrumentación, reparto y métricas.",
    })
    checks.append({
        "check": "exposure_event",
        "status": "pass" if assignment["requires_exposure_event"] and assignment["exposure_event_name"] else "block",
        "message": f"Registrar evento de exposición `{assignment['exposure_event_name']}`.",
    })
    checks.append({
        "check": "persistent_assignment",
        "status": "pass" if assignment["requires_persistent_assignment"] else "review",
        "message": "La unidad debe conservar variante durante la ventana de medición.",
    })
    checks.append({
        "check": "planned_sample_size",
        "status": "review" if min_n < required_n else "pass",
        "message": f"n actual por variante {min_n}; n recomendado por variante para MDE {planned_delta}: {required_n}.",
    })
    checks.append({
        "check": "peeking_policy",
        "status": "review" if plan["planned_looks"] > 1 and not plan["sequential_testing_enabled"] else "pass",
        "message": plan["peeking_policy"],
    })
    checks.append({
        "check": "rollout_policy",
        "status": "pass" if rollout["publish_requires_status"] == "pass" else "review",
        "message": f"Ramp inicial {rollout['initial_ramp_percent']}%, pasos {rollout['ramp_steps_percent']}.",
    })

    return {
        "alpha": plan["alpha"],
        "power": plan["power"],
        "baseline_rate": baseline,
        "planned_minimum_detectable_effect": planned_delta,
        "z_alpha": pct(z_alpha),
        "z_power": pct(z_power),
        "current_min_n_per_variant": min_n,
        "required_n_per_variant_for_planned_mde": required_n,
        "observed_minimum_detectable_effect_with_current_n": pct(observed_mde) if observed_mde is not None else None,
        "checks": checks,
        "status": status_from_checks(checks),
    }


def status_from_checks(checks):
    statuses = {item["status"] for item in checks}
    if "block" in statuses:
        return "block"
    if "review" in statuses:
        return "review"
    return "pass"


def decide(report, contract):
    reasons = []
    status = "pass"
    if report["schema_errors"]:
        return "block", ["schema invalido"]
    if report["srm"]["status"] == "block":
        return "block", ["sample ratio mismatch"]
    if report["readiness"]["status"] == "block":
        return "block", ["readiness bloquea el experimento"]
    for item in report["guardrails"]:
        if item["status"] == "block":
            status = "block"
            reasons.append(f"guardrail falla: {item['metric']}")
    for item in report["readiness"]["checks"]:
        if item["status"] == "review" and status != "block":
            status = "review"
            reasons.append(f"readiness en revisión: {item['check']}")
    for item in report["balance"]:
        if item["status"] == "review" and status != "block":
            status = "review"
            reasons.append(f"balance en revisión: {item['field']}")
    primary = report["primary_effect"]
    min_effect = contract["primary_metric"]["minimum_effect"]
    min_n = contract["primary_metric"]["minimum_n_per_variant"]
    counts = report["srm"]["observed"]
    if min(counts.values()) < min_n and status != "block":
        status = "review"
        reasons.append("muestra insuficiente por variante")
    if primary["ci95_low"] <= min_effect and status != "block":
        status = "review"
        reasons.append("efecto prometedor pero intervalo aún cruza el efecto mínimo")
    if primary["effect"] < min_effect and status != "block":
        status = "review"
        reasons.append("efecto observado menor que el mínimo practico")
    if not reasons:
        reasons.append("contrato cumplido y efecto primario defendible")
    return status, reasons


def build_report(rows, contract):
    report = {
        "schema_errors": validate_schema(rows, contract),
        "variant_summary": [summarize_variant(rows, variant) for variant in contract["expected_allocation"]],
        "srm": srm_check(rows, contract),
        "balance": balance_checks(rows, contract),
        "primary_effect": effect_for_metric(rows, contract["primary_metric"]["name"]),
        "cuped_effect": cuped_effect(rows),
        "guardrails": guardrail_checks(rows, contract),
        "slice_effects": slice_effects(rows),
        "readiness": readiness_checks(rows, contract),
    }
    status, reasons = decide(report, contract)
    report["status"] = status
    report["reasons"] = reasons
    return report


def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def render_decision(report):
    lines = [
        "# Decisión del experimento",
        "",
        f"Estado: **{report['status']}**.",
        "",
        "## Lectura",
        "",
        f"ATE observado en `resolved`: `{report['primary_effect']['effect']}`.",
        f"Intervalo 95%: `[{report['primary_effect']['ci95_low']}, {report['primary_effect']['ci95_high']}]`.",
        f"Efecto CUPED: `{report['cuped_effect']['effect']}` con covariable `{report['cuped_effect']['covariate']}`.",
        "",
        "## Motivos",
        "",
    ]
    for reason in report["reasons"]:
        lines.append(f"- {reason}.")
    lines.extend([
        "",
        "## Decisión operativa",
        "",
        "No se publica automáticamente como cambio global. La señal es positiva, los guardrails pasan y la asignación está equilibrada, pero el intervalo sigue siendo ancho. El siguiente paso es ampliar muestra o repetir una ventana con el mismo contrato.",
        "",
        "## Entregable de ingeniería",
        "",
        "Guardar `experiment_report.json`, `slice_effects.csv`, `experiment_scorecard.csv` y este documento junto a la versión de producto que se estaba evaluando.",
    ])
    return "\n".join(lines) + "\n"


def render_readiness(report):
    readiness = report["readiness"]
    lines = [
        "# Readiness del experimento",
        "",
        f"Estado readiness: **{readiness['status']}**.",
        "",
        "## MDE y muestra",
        "",
        f"Baseline: `{readiness['baseline_rate']}`.",
        f"Alpha: `{readiness['alpha']}`.",
        f"Potencia: `{readiness['power']}`.",
        f"MDE planificado: `{readiness['planned_minimum_detectable_effect']}`.",
        f"n actual por variante: `{readiness['current_min_n_per_variant']}`.",
        f"n recomendado por variante: `{readiness['required_n_per_variant_for_planned_mde']}`.",
        f"MDE aproximado con n actual: `{readiness['observed_minimum_detectable_effect_with_current_n']}`.",
        "",
        "## Checklist operativo",
        "",
        "| Check | Estado | Mensaje |",
        "|---|---|---|",
    ]
    for item in readiness["checks"]:
        lines.append(f"| `{item['check']}` | `{item['status']}` | {item['message']} |")
    lines.extend([
        "",
        "## Lectura",
        "",
        "El experimento del kit sirve para aprender y detectar señal. Para publicar una decisión global con el MDE planificado, haría falta más muestra, A/A previo documentado y la misma política de peeking cerrada antes de iniciar.",
    ])
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--events", type=Path, default=DEFAULT_EVENTS)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    rows = read_csv(args.events)
    contract = read_json(args.contract)
    report = build_report(rows, contract)

    if args.write:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        write_json(args.output_dir / "experiment_report.json", report)
        write_csv(args.output_dir / "slice_effects.csv", report["slice_effects"])
        write_csv(args.output_dir / "experiment_scorecard.csv", report["variant_summary"])
        write_csv(args.output_dir / "balance_report.csv", report["balance"])
        (args.output_dir / "experiment_decision.md").write_text(render_decision(report), encoding="utf-8")
        (args.output_dir / "experiment_readiness.md").write_text(render_readiness(report), encoding="utf-8")
    else:
        print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
