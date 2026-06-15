#!/usr/bin/env python3
import argparse
import csv
import json
import random
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EVENTS = ROOT / "data" / "logged_policy_events.jsonl"
DEFAULT_CONTRACT = ROOT / "contracts" / "ope_contract.json"
DEFAULT_OUTPUT = ROOT / "output"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path):
    rows = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if line.strip():
            row = json.loads(line)
            row["_line"] = line_number
            rows.append(row)
    return rows


def validate_rows(rows, contract):
    errors = []
    required = contract["required_fields"]
    for row in rows:
        for field in required:
            if field not in row:
                errors.append(f"{row.get('event_id', 'line_' + str(row.get('_line')))} falta {field}")
        action = row.get("action")
        allowed = row.get("allowed_actions", [])
        if action and action not in allowed:
            errors.append(f"{row['event_id']} accion fuera de allowed_actions")
        behavior = float(row.get("behavior_action_probability", 0))
        target = float(row.get("target_action_probability", 0))
        if behavior <= 0:
            errors.append(f"{row.get('event_id')} behavior_action_probability debe ser > 0")
        if target < 0:
            errors.append(f"{row.get('event_id')} target_action_probability debe ser >= 0")
        target_probs = row.get("target_policy_probability_by_action", {})
        if target_probs:
            total = sum(float(value) for value in target_probs.values())
            if abs(total - 1.0) > 0.02:
                errors.append(f"{row['event_id']} target_policy_probability_by_action no suma 1")
    return errors


def direct_method(rows):
    values = []
    for row in rows:
        target_probs = row["target_policy_probability_by_action"]
        q_values = row["q_model_reward_by_action"]
        expected = sum(float(probability) * float(q_values[action]) for action, probability in target_probs.items())
        values.append(expected)
    return sum(values) / len(values)


def row_terms(row):
    behavior_probability = float(row["behavior_action_probability"])
    target_probability = float(row["target_action_probability"])
    reward = float(row["reward"])
    weight = target_probability / behavior_probability
    target_probs = row["target_policy_probability_by_action"]
    q_values = row["q_model_reward_by_action"]
    model_value = sum(float(probability) * float(q_values[action]) for action, probability in target_probs.items())
    q_logged = float(q_values[row["action"]])
    dr_term = model_value + weight * (reward - q_logged)
    return {
        "behavior_probability": behavior_probability,
        "target_probability": target_probability,
        "reward": reward,
        "weight": weight,
        "model_value": model_value,
        "q_logged": q_logged,
        "dr_term": dr_term,
    }


def effective_sample_size(weights):
    return (sum(weights) ** 2) / sum(weight * weight for weight in weights)


def percentile(values, probability):
    ordered = sorted(values)
    if not ordered:
        return 0.0
    index = min(len(ordered) - 1, max(0, round(probability * (len(ordered) - 1))))
    return ordered[index]


def bootstrap_interval(terms, contract):
    samples = int(contract.get("bootstrap_samples", 500))
    confidence = float(contract.get("confidence_level", 0.90))
    rng = random.Random(int(contract.get("bootstrap_seed", 41)))
    n = len(terms)
    draws = []
    for _ in range(samples):
        sample = [terms[rng.randrange(n)] for _ in range(n)]
        draws.append(sum(row["dr_term"] for row in sample) / n)
    alpha = (1 - confidence) / 2
    return {
        "estimator": "doubly_robust",
        "confidence_level": confidence,
        "samples": samples,
        "lower": round(percentile(draws, alpha), 6),
        "upper": round(percentile(draws, 1 - alpha), 6),
    }


def slice_diagnostics(rows, terms):
    grouped = defaultdict(list)
    for row, term in zip(rows, terms):
        grouped[row["context"]["slice"]].append((row, term))
    diagnostics = []
    for slice_name, items in sorted(grouped.items()):
        weights = [term["weight"] for _, term in items]
        support = sum(term["target_probability"] for _, term in items) / len(items)
        diagnostics.append({
            "slice": slice_name,
            "events": len(items),
            "doubly_robust": round(sum(term["dr_term"] for _, term in items) / len(items), 6),
            "ess_ratio": round(effective_sample_size(weights) / len(items), 6),
            "max_importance_weight": round(max(weights), 6),
            "logged_action_support": round(support, 6),
        })
    return diagnostics


def support_matrix(rows):
    grouped = defaultdict(lambda: {
        "events": 0,
        "observed_count": 0,
        "target_probability_mass": 0.0,
        "behavior_probability_mass": 0.0,
    })
    for row in rows:
        slice_name = row["context"]["slice"]
        for action in row["allowed_actions"]:
            key = (slice_name, action)
            grouped[key]["events"] += 1
            grouped[key]["target_probability_mass"] += float(row["target_policy_probability_by_action"].get(action, 0.0))
            if row["action"] == action:
                grouped[key]["observed_count"] += 1
                grouped[key]["behavior_probability_mass"] += float(row["behavior_action_probability"])
    matrix = []
    for (slice_name, action), values in sorted(grouped.items()):
        events = values["events"]
        matrix.append({
            "slice": slice_name,
            "action": action,
            "events": events,
            "observed_count": values["observed_count"],
            "target_probability_mass": round(values["target_probability_mass"] / events, 6),
            "observed_share": round(values["observed_count"] / events, 6),
            "has_observed_support": values["observed_count"] > 0,
        })
    return matrix


def evaluate(rows, contract):
    terms = [row_terms(row) for row in rows]
    weights = [term["weight"] for term in terms]
    rewards = [term["reward"] for term in terms]
    dr_terms = [term["dr_term"] for term in terms]
    logged_support_mass = sum(term["target_probability"] for term in terms)

    n = len(rows)
    ips = sum(weight * reward for weight, reward in zip(weights, rewards)) / n
    wis = sum(weight * reward for weight, reward in zip(weights, rewards)) / sum(weights)
    dm = direct_method(rows)
    dr = sum(dr_terms) / n
    ess = effective_sample_size(weights)
    ess_ratio = ess / n
    logged_action_support = logged_support_mass / n
    interval = bootstrap_interval(terms, contract)
    by_slice = slice_diagnostics(rows, terms)
    by_action_support = support_matrix(rows)
    unsupported_masses = [
        row["target_probability_mass"]
        for row in by_action_support
        if not row["has_observed_support"]
    ]
    max_unsupported_target_probability_mass = max(unsupported_masses or [0.0])

    estimates = {
        "direct_method": round(dm, 6),
        "ips": round(ips, 6),
        "wis": round(wis, 6),
        "doubly_robust": round(dr, 6),
    }
    diagnostics = {
        "events": n,
        "max_importance_weight": round(max(weights), 6),
        "min_importance_weight": round(min(weights), 6),
        "ess": round(ess, 6),
        "ess_ratio": round(ess_ratio, 6),
        "logged_action_support": round(logged_action_support, 6),
        "abs_ips_wis_gap": round(abs(ips - wis), 6),
        "abs_dm_dr_gap": round(abs(dm - dr), 6),
        "bootstrap_ci_lower": interval["lower"],
        "bootstrap_ci_upper": interval["upper"],
        "min_slice_events": min(row["events"] for row in by_slice),
        "max_unsupported_target_probability_mass": round(max_unsupported_target_probability_mass, 6),
    }
    checks = {
        "min_events": n >= contract["min_events"],
        "min_ess_ratio": ess_ratio >= contract["min_ess_ratio"],
        "max_importance_weight": max(weights) <= contract["max_importance_weight"],
        "max_abs_ips_wis_gap": abs(ips - wis) <= contract["max_abs_ips_wis_gap"],
        "max_abs_dm_dr_gap": abs(dm - dr) <= contract["max_abs_dm_dr_gap"],
        "min_logged_action_support": logged_action_support >= contract["min_logged_action_support"],
        "min_dr_estimate": dr >= contract["min_dr_estimate"],
        "min_dr_ci_lower_bound": interval["lower"] >= contract["min_dr_ci_lower_bound"],
        "min_slice_events": min(row["events"] for row in by_slice) >= contract["min_slice_events"],
        "max_unsupported_target_probability_mass": max_unsupported_target_probability_mass <= contract["max_unsupported_target_probability_mass"],
    }
    status = "pass" if all(checks.values()) else "block"
    return {
        "scenario_id": contract["scenario_id"],
        "contract_version": contract["contract_version"],
        "target_policy_id": contract["target_policy_id"],
        "behavior_policy_id": contract["behavior_policy_id"],
        "status": status,
        "estimates": estimates,
        "diagnostics": diagnostics,
        "confidence_interval": interval,
        "slice_diagnostics": by_slice,
        "support_matrix": by_action_support,
        "checks": checks,
    }, terms


def render_decision(report):
    if "estimates" not in report:
        return "# Decisión OPE\n\nEstado: `block`\n\nEl dataset no cumple el contrato mínimo de campos.\n"
    lines = [
        "# Decisión OPE",
        "",
        f"Estado: `{report['status']}`",
        f"Política histórica: `{report['behavior_policy_id']}`",
        f"Política candidata: `{report['target_policy_id']}`",
        "",
        "| Estimador | Valor |",
        "|---|---:|",
    ]
    for key, value in report["estimates"].items():
        lines.append(f"| `{key}` | {value} |")
    lines.extend([
        "",
        "| Diagnóstico | Valor |",
        "|---|---:|",
    ])
    for key, value in report["diagnostics"].items():
        lines.append(f"| `{key}` | {value} |")
    lines.extend([
        "",
        "## Intervalo de confianza",
        "",
        f"Estimador: `{report['confidence_interval']['estimator']}`",
        f"Confianza: `{report['confidence_interval']['confidence_level']}`",
        f"Intervalo bootstrap: `{report['confidence_interval']['lower']}` - `{report['confidence_interval']['upper']}`",
    ])
    lines.extend([
        "",
        "## Lectura",
        "",
    ])
    if report["status"] == "pass":
        lines.append(
            "La política candidata puede pasar a modo sombra o piloto muy limitado. No queda aprobada para producción amplia: OPE reduce riesgo, no sustituye medición online."
        )
    else:
        lines.append(
            "La política candidata no debe moverse a piloto. Hay poca cobertura, pesos extremos o desacuerdo entre estimadores; toca recoger mejor dato, limitar la política o revisar el modelo de recompensa."
        )
    lines.extend([
        "",
        "## Condiciones antes del siguiente paso",
        "",
        "1. Revisar eventos con pesos altos.",
        "2. Confirmar que cada evento incluye propensión histórica.",
        "3. Medir soporte por slice y acción.",
        "4. Comparar IPS, WIS, DM y DR; si se separan demasiado, no publicar.",
        "5. Revisar el límite inferior del intervalo bootstrap.",
        "6. Mantener política estable como fallback.",
        "",
    ])
    return "\n".join(lines)


def render_quality_card(report):
    if "estimates" not in report:
        return "# OPE quality card\n\nEstado: `block`\n\nFaltan campos obligatorios.\n"
    lines = [
        "# OPE quality card",
        "",
        f"Estado: `{report['status']}`",
        f"Política candidata: `{report['target_policy_id']}`",
        f"Política histórica: `{report['behavior_policy_id']}`",
        "",
        "## Lectura ejecutiva",
        "",
    ]
    if report["status"] == "pass":
        lines.append("El dataset permite una evaluación offline inicial. La siguiente fase razonable es modo sombra, no producción amplia.")
    else:
        lines.append("El dataset no permite avanzar. El siguiente trabajo es mejorar cobertura, reducir pesos extremos o revisar reward/modelo Q.")
    lines.extend([
        "",
        "## Evidencia mínima",
        "",
        "| Check | Resultado |",
        "|---|---:|",
    ])
    for key, value in report["checks"].items():
        lines.append(f"| `{key}` | `{value}` |")
    lines.extend([
        "",
        "## Slices",
        "",
        "| Slice | Eventos | DR | ESS ratio | Max weight | Soporte |",
        "|---|---:|---:|---:|---:|---:|",
    ])
    for row in report["slice_diagnostics"]:
        lines.append(
            f"| `{row['slice']}` | {row['events']} | {row['doubly_robust']} | {row['ess_ratio']} | {row['max_importance_weight']} | {row['logged_action_support']} |"
        )
    lines.extend([
        "",
        "## Decisión",
        "",
        "1. Si cualquier check queda en `False`, no hay piloto.",
        "2. Si el intervalo inferior cae bajo el umbral, mantener en modo sombra.",
        "3. Si una acción tiene masa candidata pero cero soporte observado, limitar la política o recoger datos.",
        "4. Si los estimadores discrepan, revisar propensiones, reward y modelo Q.",
        "",
    ])
    return "\n".join(lines)


def write_outputs(report, rows, terms, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "ope_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (output_dir / "ope_decision.md").write_text(render_decision(report), encoding="utf-8")
    (output_dir / "ope_quality_card.md").write_text(render_quality_card(report), encoding="utf-8")
    if "estimates" not in report:
        return
    with (output_dir / "importance_weights.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["event_id", "slice", "action", "behavior_probability", "target_probability", "weight", "reward"])
        writer.writeheader()
        for row, term in zip(rows, terms):
            writer.writerow({
                "event_id": row["event_id"],
                "slice": row["context"]["slice"],
                "action": row["action"],
                "behavior_probability": row["behavior_action_probability"],
                "target_probability": row["target_action_probability"],
                "weight": round(term["weight"], 6),
                "reward": row["reward"],
            })
    with (output_dir / "estimator_scorecard.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["metric", "value"])
        writer.writeheader()
        for key, value in report["estimates"].items():
            writer.writerow({"metric": key, "value": value})
        for key, value in report["diagnostics"].items():
            writer.writerow({"metric": key, "value": value})
    with (output_dir / "slice_diagnostics.csv").open("w", encoding="utf-8", newline="") as handle:
        fieldnames = ["slice", "events", "doubly_robust", "ess_ratio", "max_importance_weight", "logged_action_support"]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in report["slice_diagnostics"]:
            writer.writerow({field: row[field] for field in fieldnames})
    with (output_dir / "support_matrix.csv").open("w", encoding="utf-8", newline="") as handle:
        fieldnames = ["slice", "action", "events", "observed_count", "target_probability_mass", "observed_share", "has_observed_support"]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in report["support_matrix"]:
            writer.writerow({field: row[field] for field in fieldnames})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--events", type=Path, default=DEFAULT_EVENTS)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    contract = read_json(args.contract)
    rows = read_jsonl(args.events)
    errors = validate_rows(rows, contract)
    if errors:
        report = {
            "scenario_id": contract["scenario_id"],
            "contract_version": contract["contract_version"],
            "status": "block",
            "errors": errors,
        }
        terms = []
    else:
        report, terms = evaluate(rows, contract)

    if args.write:
        write_outputs(report, rows, terms, args.output)
    print(f"status={report['status']}")
    print(f"events={len(rows)}")
    if "estimates" in report:
        print(f"doubly_robust={report['estimates']['doubly_robust']}")


if __name__ == "__main__":
    main()
