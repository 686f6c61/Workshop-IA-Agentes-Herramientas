#!/usr/bin/env python3
import argparse
import csv
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCENARIO = ROOT / "data" / "routing_scenario.json"
DEFAULT_CONTRACT = ROOT / "contracts" / "bandit_policy_contract.json"
DEFAULT_OUTPUT = ROOT / "output"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def expand_rounds(scenario):
    expanded = []
    repeat = int(scenario.get("repeat", 1))
    template = scenario["rounds"]
    for cycle in range(repeat):
        for item in template:
            row = dict(item)
            row["round"] = cycle * len(template) + int(item["round"])
            row["request_id"] = f"req_{row['round']:03d}"
            expanded.append(row)
    return expanded


def best_action(row):
    allowed = row["allowed_actions"]
    return max(allowed, key=lambda action: row["reward_by_action"][action])


def observed_mean(action, totals, counts):
    return totals[action] / counts[action] if counts[action] else 0.0


def action_probability_for_deterministic(action, allowed):
    return 1.0 if action in allowed else 0.0


def estimate_thompson_probability(allowed, alpha, beta, selected, rng, samples):
    wins = Counter()
    for _ in range(samples):
        drawn = {
            action: rng.betavariate(alpha[action], beta[action])
            for action in allowed
        }
        wins[max(allowed, key=lambda action: drawn[action])] += 1
    return wins[selected] / samples


def choose_action(policy, row, counts, totals, alpha, beta, round_index, contract, rng):
    allowed = list(row["allowed_actions"])
    slice_name = row["slice"]
    stable_action = contract["stable_action_by_slice"].get(slice_name)
    if slice_name in contract["no_exploration_slices"] and stable_action in allowed:
        return stable_action, "stable_slice_policy", action_probability_for_deterministic(stable_action, allowed), False

    untried = [action for action in allowed if counts[action] == 0]
    if untried:
        selected = untried[0]
        return selected, "initial_exploration", 1 / len(untried), True

    policy_id = policy["policy_id"]
    if policy_id == "greedy":
        selected = max(allowed, key=lambda action: observed_mean(action, totals, counts))
        return selected, "best_observed_mean", 1.0, False

    if policy_id == "epsilon_greedy":
        epsilon = float(policy.get("epsilon", 0.1))
        greedy = max(allowed, key=lambda action: observed_mean(action, totals, counts))
        period = max(2, round(1 / epsilon))
        if (round_index + 1) % period == 0:
            selected = min(allowed, key=lambda action: counts[action])
            return selected, "scheduled_exploration", 1 / len(allowed), selected != greedy
        probability = (1 - epsilon) + (epsilon / len(allowed))
        return greedy, "best_observed_mean", probability, False

    if policy_id == "ucb":
        c = float(policy.get("c", 0.8))
        total_pulls = sum(counts.values())

        def score(action):
            mean = observed_mean(action, totals, counts)
            bonus = c * math.sqrt(math.log(total_pulls + 1) / counts[action])
            return mean + bonus

        selected = max(allowed, key=score)
        greedy = max(allowed, key=lambda action: observed_mean(action, totals, counts))
        return selected, "ucb_score", 1.0, selected != greedy

    if policy_id == "thompson_sampling":
        draws = {action: rng.betavariate(alpha[action], beta[action]) for action in allowed}
        selected = max(allowed, key=lambda action: draws[action])
        probability = estimate_thompson_probability(
            allowed,
            alpha,
            beta,
            selected,
            rng,
            int(policy.get("posterior_samples", 200)),
        )
        greedy = max(allowed, key=lambda action: observed_mean(action, totals, counts))
        return selected, "posterior_sample", round(probability, 4), selected != greedy

    raise ValueError(f"Unsupported policy_id: {policy_id}")


def simulate_policy(scenario, contract, policy):
    rng = random.Random(int(contract["seed"]) + sum(ord(ch) for ch in policy["policy_id"]))
    rounds = expand_rounds(scenario)
    counts = Counter()
    totals = Counter()
    costs = Counter()
    alpha = defaultdict(lambda: 1.0)
    beta = defaultdict(lambda: 1.0)
    trace = []
    exploration_count = 0
    sensitive_exploration_count = 0
    cumulative_reward = 0.0
    cumulative_regret = 0.0

    for index, row in enumerate(rounds):
        action, reason, probability, exploratory = choose_action(
            policy,
            row,
            counts,
            totals,
            alpha,
            beta,
            index,
            contract,
            rng,
        )
        reward = float(row["reward_by_action"][action])
        cost = float(scenario["actions"][action]["cost"])
        best = best_action(row)
        best_reward = float(row["reward_by_action"][best])
        regret = best_reward - reward
        success = reward >= float(contract["success_threshold"])

        counts[action] += 1
        totals[action] += reward
        costs[action] += cost
        if success:
            alpha[action] += 1
        else:
            beta[action] += 1
        cumulative_reward += reward
        cumulative_regret += regret
        exploration_count += int(exploratory)
        sensitive_exploration_count += int(exploratory and row["slice"] in contract["no_exploration_slices"])

        trace.append({
            "round": row["round"],
            "request_id": row["request_id"],
            "policy_id": policy["policy_id"],
            "context": {
                "slice": row["slice"],
            },
            "slice": row["slice"],
            "allowed_actions": row["allowed_actions"],
            "action": action,
            "action_probability": round(probability, 4),
            "reason": reason,
            "selection_reason": reason,
            "exploratory": exploratory,
            "reward": round(reward, 4),
            "cost": round(cost, 4),
            "best_action": best,
            "best_reward": round(best_reward, 4),
            "instant_regret": round(regret, 4),
            "cumulative_reward": round(cumulative_reward, 4),
            "cumulative_regret": round(cumulative_regret, 4),
        })

    total_rounds = len(rounds)
    return {
        "policy_id": policy["policy_id"],
        "cumulative_reward": round(cumulative_reward, 4),
        "regret": round(cumulative_regret, 4),
        "exploration_share": round(exploration_count / total_rounds, 4),
        "sensitive_exploration_count": sensitive_exploration_count,
        "average_cost": round(sum(costs.values()) / total_rounds, 4),
        "action_counts": dict(sorted(counts.items())),
        "action_share": {action: round(counts[action] / total_rounds, 4) for action in sorted(scenario["actions"])},
        "observed_means": {action: round(observed_mean(action, totals, counts), 4) for action in sorted(scenario["actions"])},
        "trace": trace,
    }


def evaluate_gate(row, contract):
    gate = contract["gate"]
    checks = {
        "min_cumulative_reward": row["cumulative_reward"] >= gate["min_cumulative_reward"],
        "max_regret": row["regret"] <= gate["max_regret"],
        "max_exploration_share": row["exploration_share"] <= gate["max_exploration_share"],
        "max_sensitive_exploration_count": row["sensitive_exploration_count"] <= gate["max_sensitive_exploration_count"],
        "max_average_cost": row["average_cost"] <= gate["max_average_cost"],
        "required_trace_events": len(row["trace"]) >= gate["required_trace_events"],
    }
    return checks, all(checks.values())


def build_report(scenario, contract):
    policies = []
    traces = []
    for policy in contract["policies"]:
        result = simulate_policy(scenario, contract, policy)
        checks, gate_ok = evaluate_gate(result, contract)
        compact = {key: value for key, value in result.items() if key != "trace"}
        compact["gate_checks"] = checks
        compact["gate_ok"] = gate_ok
        policies.append(compact)
        traces.extend(result["trace"])

    eligible = [row for row in policies if row["gate_ok"]]
    status = "pass" if eligible else "review"
    selected = max(
        eligible or policies,
        key=lambda row: (row["gate_ok"], row["cumulative_reward"], -row["regret"], -row["average_cost"]),
    )
    if not eligible:
        status = "review"

    return {
        "scenario_id": scenario["scenario_id"],
        "status": status,
        "selected_policy": selected["policy_id"],
        "rounds": len(expand_rounds(scenario)),
        "contract_version": contract["contract_version"],
        "policies": policies,
    }, traces


def build_shadow_report(report, traces, contract):
    selected_policy = report["selected_policy"]
    candidate_trace = [row for row in traces if row["policy_id"] == selected_policy]
    selected_policy_row = next(row for row in report["policies"] if row["policy_id"] == selected_policy)
    action_counts = Counter(row["action"] for row in candidate_trace)
    no_exploration_slices = set(contract["no_exploration_slices"])
    sensitive_rows = [row for row in candidate_trace if row["slice"] in no_exploration_slices]
    stable_matches = 0
    for row in sensitive_rows:
        stable_action = contract["stable_action_by_slice"].get(row["slice"])
        stable_matches += int(row["action"] == stable_action)

    rollout_steps = [
        {"step": 1, "traffic_share": 0.05, "duration": "24h", "decision": "manual_review"},
        {"step": 2, "traffic_share": 0.10, "duration": "48h", "decision": "manual_review"},
        {"step": 3, "traffic_share": 0.25, "duration": "72h", "decision": "manual_review"},
    ]
    readiness_checks = {
        "status_passes_gate": report["status"] == "pass",
        "action_probability_logged": all("action_probability" in row for row in candidate_trace),
        "selection_reason_logged": all("selection_reason" in row for row in candidate_trace),
        "no_exploration_slices_use_stable_action": stable_matches == len(sensitive_rows),
        "max_regret_ok": selected_policy_row["gate_checks"]["max_regret"],
        "max_average_cost_ok": selected_policy_row["gate_checks"]["max_average_cost"],
        "trace_volume_ok": selected_policy_row["gate_checks"]["required_trace_events"],
    }
    return {
        "scenario_id": report["scenario_id"],
        "mode": "shadow_before_pilot",
        "selected_policy": selected_policy,
        "rounds": len(candidate_trace),
        "recommendations_by_action": dict(sorted(action_counts.items())),
        "sensitive_slice_rows": len(sensitive_rows),
        "sensitive_slice_stable_matches": stable_matches,
        "readiness_checks": readiness_checks,
        "pilot_guardrails": {
            "feature_flag_key": "rl_model_routing_policy",
            "baseline_variant": "stable",
            "candidate_variant": "bandit_candidate",
            "fallback_action": "modelo_fuerte",
            "rollout_steps": rollout_steps,
            "stop_conditions": [
                "regret_window_gt_contract",
                "average_cost_gt_contract",
                "quality_below_contract",
                "missing_trace_or_reward",
                "unexpected_traffic_shift",
            ],
        },
    }


def write_outputs(report, traces, output_dir, contract):
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "bandit_validation_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (output_dir / "bandit_trace.jsonl").write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in traces) + "\n", encoding="utf-8")
    with (output_dir / "policy_scorecard.csv").open("w", encoding="utf-8", newline="") as handle:
        fieldnames = ["policy_id", "gate_ok", "cumulative_reward", "regret", "exploration_share", "sensitive_exploration_count", "average_cost"]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in report["policies"]:
            writer.writerow({field: row[field] for field in fieldnames})
    (output_dir / "policy_decision.md").write_text(render_decision(report), encoding="utf-8")
    shadow_report = build_shadow_report(report, traces, contract)
    (output_dir / "shadow_replay_report.json").write_text(json.dumps(shadow_report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def render_decision(report):
    selected = next(row for row in report["policies"] if row["policy_id"] == report["selected_policy"])
    lines = [
        "# Decisión de política bandit",
        "",
        f"Estado: `{report['status']}`",
        f"Política seleccionada: `{report['selected_policy']}`",
        f"Rondas simuladas: {report['rounds']}",
        "",
        "| Política | Gate | Recompensa | Regret | Exploración | Coste medio |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in report["policies"]:
        lines.append(
            f"| `{row['policy_id']}` | `{row['gate_ok']}` | {row['cumulative_reward']} | {row['regret']} | {row['exploration_share']} | {row['average_cost']} |"
        )
    lines.extend([
        "",
        "## Lectura",
        "",
    ])
    if report["status"] == "pass":
        lines.append(
            f"`{selected['policy_id']}` pasa los gates y puede proponerse como piloto limitado con feature flag, trazas y rollback."
        )
    else:
        lines.append(
            "Ninguna política pasa todos los gates. La decisión correcta es revisar reward, límites o escenario antes de mover tráfico."
        )
    lines.extend([
        "",
        "## Condiciones antes de producción",
        "",
        "1. Registrar `action_probability`, contexto, reward y razón de selección en cada ronda.",
        "2. Mantener política estable de reserva para rollback.",
        "3. Revisar regret y coste por ventana.",
        "4. No explorar en slices marcados por contrato.",
        "5. Guardar `bandit_trace.jsonl` para evaluación offline posterior.",
        "",
    ])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", type=Path, default=DEFAULT_SCENARIO)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    scenario = read_json(args.scenario)
    contract = read_json(args.contract)
    report, traces = build_report(scenario, contract)
    if args.write:
        write_outputs(report, traces, args.output, contract)
    print(f"status={report['status']}")
    print(f"selected_policy={report['selected_policy']}")
    print(f"rounds={report['rounds']}")


if __name__ == "__main__":
    main()
