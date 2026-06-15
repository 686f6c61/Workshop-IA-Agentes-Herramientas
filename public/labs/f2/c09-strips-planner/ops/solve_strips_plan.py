#!/usr/bin/env python3
import argparse
import json
from collections import deque
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def applicable(action, state):
    return set(action["pre"]).issubset(state)


def apply_action(action, state):
    return (state - set(action["delete"])) | set(action["add"])


def action_map(actions):
    return {action["name"]: action for action in actions}


def validate_plan(problem, plan_names):
    state = set(problem["initial_state"])
    actions = action_map(problem["actions"])
    trace = [{"step": 0, "action": None, "state": sorted(state)}]

    for step, name in enumerate(plan_names, start=1):
        action = actions.get(name)
        if not action:
            return False, f"accion_desconocida:{name}", trace
        missing = sorted(set(action["pre"]) - state)
        if missing:
            return False, f"precondiciones_no_satisfechas:{name}:{','.join(missing)}", trace
        state = apply_action(action, state)
        trace.append({"step": step, "action": name, "state": sorted(state)})

    goal = set(problem["goal"])
    if not goal.issubset(state):
        return False, f"objetivo_no_cumplido:{','.join(sorted(goal - state))}", trace
    return True, "ok", trace


def solve_bfs(problem, max_depth):
    initial = set(problem["initial_state"])
    goal = set(problem["goal"])
    frontier = deque([(initial, [])])
    visited = {frozenset(initial)}
    expansions = 0

    while frontier:
        state, path = frontier.popleft()
        expansions += 1
        if goal.issubset(state):
            return path, state, expansions
        if len(path) >= max_depth:
            continue
        for action in problem["actions"]:
            if not applicable(action, state):
                continue
            next_state = apply_action(action, state)
            frozen = frozenset(next_state)
            if frozen in visited:
                continue
            visited.add(frozen)
            frontier.append((next_state, path + [action["name"]]))
    return None, None, expansions


def build_report(problem, policy):
    plan, final_state, expansions = solve_bfs(problem, policy["max_plan_length"])
    candidates = []
    for candidate in problem["candidate_plans"]:
        ok, reason, trace = validate_plan(problem, candidate)
        candidates.append({
            "plan": candidate,
            "valid": ok,
            "reason": reason,
            "trace": trace
        })
    solved_ok, reason, trace = validate_plan(problem, plan or [])
    return {
        "plan": plan,
        "valid": solved_ok,
        "reason": reason,
        "final_state": sorted(final_state) if final_state else [],
        "expansions": expansions,
        "candidate_plans": candidates,
        "trace": trace
    }


def write_markdown(report):
    lines = [
        "# Plan STRIPS mínimo",
        "",
        f"Plan encontrado: `{report['plan']}`.",
        f"Estado final: `{report['final_state']}`.",
        f"Expansiones BFS: `{report['expansions']}`.",
        "",
        "## Planes candidatos",
        "",
        "| Plan | Válido | Motivo |",
        "|---|---:|---|",
    ]
    for candidate in report["candidate_plans"]:
        lines.append(
            f"| `{candidate['plan']}` | {'sí' if candidate['valid'] else 'no'} | `{candidate['reason']}` |"
        )
    lines.extend([
        "",
        "## Decisión",
        "",
        "Un plan no se valida por sonar razonable. Se valida porque cada acción es aplicable en el estado donde aparece y porque el estado final contiene el objetivo.",
    ])
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--fail-on-invalid", action="store_true")
    args = parser.parse_args()

    problem = load_json("data/planning_problem.json")
    policy = load_json("contracts/planning_policy.json")
    report = build_report(problem, policy)
    invalid_candidates = [c for c in report["candidate_plans"] if not c["valid"]]
    valid = report["valid"] and all(fact in report["final_state"] for fact in policy["required_goal_facts"])
    if policy["require_invalid_candidate"]:
        valid = valid and bool(invalid_candidates)
    report["gate_valid"] = valid

    if args.write:
        (ROOT / "output").mkdir(exist_ok=True)
        (ROOT / "output/strips_plan_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        (ROOT / "output/strips_plan_decision.md").write_text(write_markdown(report), encoding="utf-8")

    print(json.dumps(report, indent=2, ensure_ascii=False))
    if args.fail_on_invalid and not valid:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

