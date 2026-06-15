#!/usr/bin/env python3
import argparse
import json
import math
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = ROOT / "data" / "bandit_rewards.json"
DEFAULT_CONTRACT = ROOT / "contracts" / "refuerzo_lab_contract.json"
DEFAULT_OUTPUT = ROOT / "output"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def reward_for(data, arm, pull_index):
    rewards = data["arms"][arm]["rewards"]
    return float(rewards[pull_index % len(rewards)])


def best_possible_reward(data):
    means = {
        arm: sum(values["rewards"]) / len(values["rewards"])
        for arm, values in data["arms"].items()
    }
    best_arm = max(means, key=means.get)
    return best_arm, means[best_arm], means


def choose(policy, arms, counts, totals, round_index, data):
    untried = [arm for arm in arms if counts[arm] == 0]
    if untried:
        return untried[0], "initial_exploration"

    if policy["policy_id"] == "greedy":
        return max(arms, key=lambda arm: totals[arm] / counts[arm]), "best_observed_mean"

    if policy["policy_id"] == "epsilon_greedy":
        epsilon = float(policy.get("epsilon", 0.1))
        exploration_period = max(2, round(1 / epsilon))
        if (round_index + 1) % exploration_period == 0:
            return min(arms, key=lambda arm: counts[arm]), "scheduled_exploration"
        return max(arms, key=lambda arm: totals[arm] / counts[arm]), "best_observed_mean"

    if policy["policy_id"] == "ucb":
        c = float(policy.get("c", 0.8))
        total_pulls = sum(counts.values())
        def ucb_score(arm):
            mean = totals[arm] / counts[arm]
            bonus = c * math.sqrt(math.log(total_pulls + 1) / counts[arm])
            return mean + bonus
        return max(arms, key=ucb_score), "ucb_score"

    raise ValueError(f"politica no soportada: {policy['policy_id']}")


def simulate_policy(data, policy):
    arms = list(data["arms"])
    rounds = int(data["rounds"])
    counts = Counter()
    totals = Counter()
    trace = []
    best_arm, best_mean, means = best_possible_reward(data)

    for round_index in range(rounds):
        arm, reason = choose(policy, arms, counts, totals, round_index, data)
        reward = reward_for(data, arm, counts[arm])
        counts[arm] += 1
        totals[arm] += reward
        trace.append({
            "round": round_index + 1,
            "policy_id": policy["policy_id"],
            "action": arm,
            "reason": reason,
            "reward": round(reward, 4),
            "cumulative_reward": round(sum(totals.values()), 4),
            "regret": round(best_mean * (round_index + 1) - sum(totals.values()), 4)
        })

    cumulative = sum(totals.values())
    regret = best_mean * rounds - cumulative
    return {
        "policy_id": policy["policy_id"],
        "cumulative_reward": round(cumulative, 4),
        "regret": round(regret, 4),
        "action_counts": dict(counts),
        "action_share": {arm: round(counts[arm] / rounds, 4) for arm in arms},
        "observed_means": {arm: round(totals[arm] / counts[arm], 4) if counts[arm] else 0 for arm in arms},
        "best_reference_arm": best_arm,
        "true_means": {arm: round(value, 4) for arm, value in means.items()},
        "trace": trace
    }


def render_decision(report):
    chosen = report["selected_policy"]
    rows = {row["policy_id"]: row for row in report["policies"]}
    selected = rows[chosen]
    lines = [
        "# Decisión de política bandit",
        "",
        f"Decisión: `piloto_limitado`.",
        f"Política seleccionada: `{chosen}`.",
        "",
        "| Política | Recompensa acumulada | Regret | Revisión humana |",
        "|---|---:|---:|---:|",
    ]
    for row in report["policies"]:
        lines.append(
            f"| `{row['policy_id']}` | {row['cumulative_reward']} | {row['regret']} | {row['action_share'].get('revision_humana', 0)} |"
        )
    lines.extend([
        "",
        "## Motivo",
        "",
        (
            f"`{chosen}` alcanza recompensa acumulada `{selected['cumulative_reward']}`, "
            f"regret `{selected['regret']}` y mantiene revisión humana en "
            f"`{selected['action_share'].get('revision_humana', 0)}` del tráfico simulado."
        ),
        "",
        "## Límites de piloto",
        "",
        "- Activar solo en solicitudes de baja criticidad.",
        "- Mantener política fija de reserva y runbook de rollback.",
        "- Cortar exploración si el regret de ventana supera el umbral.",
        "- Guardar traza de ronda, acción, recompensa y razón de selección.",
        "",
    ])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--fail-on-gate", action="store_true")
    args = parser.parse_args()

    data = read_json(args.data)
    contract = read_json(args.contract)
    results = [simulate_policy(data, policy) for policy in data["policies"]]
    gate = contract["bandit_gate"]
    eligible = [
        row for row in results
        if row["cumulative_reward"] >= gate["min_cumulative_reward"]
        and row["regret"] <= gate["max_regret"]
        and row["action_share"].get("revision_humana", 0) <= gate["max_human_review_share"]
        and len(row["trace"]) >= gate["required_trace_events"]
    ]
    selected = max(eligible, key=lambda row: (row["cumulative_reward"], -row["regret"])) if eligible else max(results, key=lambda row: row["cumulative_reward"])
    report = {
        "scenario_id": data["scenario_id"],
        "gate_ok": bool(eligible),
        "selected_policy": selected["policy_id"],
        "policies": [{k: v for k, v in row.items() if k != "trace"} for row in results]
    }
    trace = []
    for row in results:
        trace.extend(row["trace"])

    if args.write:
        write_json(args.output_dir / "bandit_policy_report.json", report)
        (args.output_dir / "bandit_trace.jsonl").write_text(
            "\n".join(json.dumps(row, ensure_ascii=False) for row in trace) + "\n",
            encoding="utf-8"
        )
        (args.output_dir / "bandit_policy_decision.md").write_text(render_decision(report), encoding="utf-8")
    print(json.dumps({"gate_ok": report["gate_ok"], "selected_policy": report["selected_policy"]}, ensure_ascii=False, indent=2))
    if args.fail_on_gate and not report["gate_ok"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
