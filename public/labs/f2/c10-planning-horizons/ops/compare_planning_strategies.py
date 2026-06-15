#!/usr/bin/env python3
import argparse
import itertools
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def applicable(action, state):
    return set(action["pre"]).issubset(state)


def apply_action(action, state):
    return (state - set(action["delete"])) | set(action["add"])


def h(state, goal):
    return len(set(goal) - state)


def valid_sequence(actions, initial, goal, sequence):
    state = set(initial)
    trace = [{"step": 0, "state": sorted(state)}]
    by_name = {action["name"]: action for action in actions}
    for step, name in enumerate(sequence, start=1):
        action = by_name[name]
        if not applicable(action, state):
            return False, state, trace
        state = apply_action(action, state)
        trace.append({"step": step, "action": name, "state": sorted(state)})
    return set(goal).issubset(state), state, trace


def heuristic_plan(case, initial=None):
    actions = case["actions"]
    goal = set(case["goal"])
    start = set(case["initial"] if initial is None else initial)
    frontier = [(h(start, goal), 0, start, [])]
    visited = {frozenset(start)}
    expansions = 0

    while frontier:
        frontier.sort(key=lambda item: (item[0] + item[1], item[0], item[1]))
        _, cost, state, path = frontier.pop(0)
        expansions += 1
        if goal.issubset(state):
            return path, cost, expansions
        for action in actions:
            if not applicable(action, state):
                continue
            next_state = apply_action(action, state)
            frozen = frozenset(next_state)
            if frozen in visited:
                continue
            visited.add(frozen)
            frontier.append((h(next_state, goal), cost + action["cost"], next_state, path + [action["name"]]))
    return None, None, expansions


def horizon_checks(case, max_horizon):
    names = [action["name"] for action in case["actions"]]
    checks = []
    for k in range(1, max_horizon + 1):
        found = None
        for sequence in itertools.product(names, repeat=k):
            ok, _, _ = valid_sequence(case["actions"], case["initial"], case["goal"], sequence)
            if ok:
                found = list(sequence)
                break
        checks.append({"horizon": k, "status": "SAT" if found else "UNSAT", "plan": found})
    return checks


def apply_observation(state, observation):
    return (state - set(observation["remove"])) | set(observation["add"])


def build_report(case, policy):
    plan, cost, expansions = heuristic_plan(case)
    checks = horizon_checks(case, policy["max_horizon"])
    by_name = {action["name"]: action for action in case["actions"]}
    state_after_first = apply_action(by_name[plan[0]], set(case["initial"])) if plan else set(case["initial"])
    observed_state = apply_observation(state_after_first, case["observation_after_first_step"])
    replan, replan_cost, replan_expansions = heuristic_plan(case, observed_state)
    first_sat = next((item["horizon"] for item in checks if item["status"] == "SAT"), None)
    return {
        "heuristic_plan": plan,
        "heuristic_cost": cost,
        "heuristic_expansions": expansions,
        "horizon_checks": checks,
        "first_sat_horizon": first_sat,
        "observed_state_after_first_step": sorted(observed_state),
        "replan_after_observation": replan,
        "replan_cost": replan_cost,
        "replan_expansions": replan_expansions
    }


def write_markdown(report):
    lines = [
        "# Heurística, horizonte y replanificación",
        "",
        f"Plan heurístico: `{report['heuristic_plan']}` con coste `{report['heuristic_cost']}`.",
        f"Primer horizonte SAT: `k={report['first_sat_horizon']}`.",
        "",
        "| k | Estado | Plan |",
        "|---:|---|---|",
    ]
    for check in report["horizon_checks"]:
        lines.append(f"| {check['horizon']} | {check['status']} | `{check['plan']}` |")
    lines.extend([
        "",
        "## Observación y replanificación",
        "",
        f"Estado observado tras el primer paso: `{report['observed_state_after_first_step']}`.",
        f"Replan: `{report['replan_after_observation']}`.",
        "",
        "Si la observación contradice lo esperado, insistir no es planificar. Hay que replanificar o escalar.",
    ])
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--fail-on-invalid", action="store_true")
    args = parser.parse_args()

    case = load_json("data/planning_horizon_case.json")
    policy = load_json("contracts/planning_horizon_policy.json")
    report = build_report(case, policy)
    valid = report["first_sat_horizon"] == policy["expected_first_sat_horizon"]
    if policy["require_replan_after_observation"]:
        valid = valid and report["replan_after_observation"] is None
    report["gate_valid"] = valid

    if args.write:
        (ROOT / "output").mkdir(exist_ok=True)
        (ROOT / "output/planning_horizon_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        (ROOT / "output/planning_horizon_decision.md").write_text(write_markdown(report), encoding="utf-8")

    print(json.dumps(report, indent=2, ensure_ascii=False))
    if args.fail_on_invalid and not valid:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

