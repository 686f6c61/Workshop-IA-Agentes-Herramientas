#!/usr/bin/env python3
import argparse
import itertools
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMPONENT_INDEX = {"hour": 0, "room": 1}


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def as_tuple(value):
    return tuple(value)


def component(value, name):
    return value[COMPONENT_INDEX[name]]


def serial_assignment(assignment):
    return {key: list(value) for key, value in assignment.items()}


def serial_domains(domains):
    return {key: [list(value) for value in values] for key, values in domains.items()}


def candidate_count(domains):
    total = 1
    for values in domains.values():
        total *= len(values)
    return total


def check_constraint(assignment, constraint):
    scope = constraint["scope"]
    if any(variable not in assignment for variable in scope):
        return True, "pendiente"

    if constraint["type"] == "component_equals":
        value = assignment[constraint["variable"]]
        ok = component(value, constraint["component"]) == constraint["value"]
        detail = f"{constraint['variable']}={value}, esperado {constraint['component']}={constraint['value']}"
    elif constraint["type"] == "component_not_equals":
        left = assignment[constraint["left"]]
        right = assignment[constraint["right"]]
        ok = component(left, constraint["component"]) != component(right, constraint["component"])
        detail = f"{constraint['left']}={left}, {constraint['right']}={right}"
    elif constraint["type"] == "all_different_values":
        values = [assignment[variable] for variable in scope]
        ok = len(set(values)) == len(values)
        detail = ", ".join(f"{variable}={assignment[variable]}" for variable in scope)
    else:
        raise ValueError(f"restricción desconocida: {constraint['type']}")
    return ok, detail


def failures_for(assignment, constraints):
    failures = []
    for constraint in constraints:
        ok, detail = check_constraint(assignment, constraint)
        if not ok:
            failures.append({"id": constraint["id"], "detail": detail})
    return failures


def apply_unary_pruning(problem, events):
    domains = {var: [as_tuple(value) for value in values] for var, values in problem["domains"].items()}
    for constraint in problem["constraints"]:
        if constraint["type"] != "component_equals" or len(constraint["scope"]) != 1:
            continue
        variable = constraint["variable"]
        before = list(domains[variable])
        domains[variable] = [
            value
            for value in domains[variable]
            if component(value, constraint["component"]) == constraint["value"]
        ]
        removed = [value for value in before if value not in domains[variable]]
        events.append(
            {
                "event": "unary_prune",
                "constraint": constraint["id"],
                "variable": variable,
                "removed": [list(value) for value in removed],
                "remaining": [list(value) for value in domains[variable]],
            }
        )
    return domains


def forward_check(problem, domains, assignment, events, depth):
    reduced = {var: list(values) for var, values in domains.items()}
    total_removed = 0
    for variable in problem["variables"]:
        if variable in assignment:
            reduced[variable] = [assignment[variable]]
            continue
        before = list(reduced[variable])
        kept = []
        for value in before:
            trial = dict(assignment)
            trial[variable] = value
            if not failures_for(trial, problem["constraints"]):
                kept.append(value)
        removed = [value for value in before if value not in kept]
        if removed:
            total_removed += len(removed)
            events.append(
                {
                    "event": "forward_prune",
                    "depth": depth,
                    "variable": variable,
                    "removed": [list(value) for value in removed],
                    "assignment": serial_assignment(assignment),
                }
            )
        reduced[variable] = kept
    return reduced, total_removed


def choose_mrv(problem, domains, assignment):
    pending = [variable for variable in problem["variables"] if variable not in assignment]
    return min(pending, key=lambda variable: (len(domains[variable]), problem["variables"].index(variable)))


def backtrack(problem, assignment, domains, stats, events, depth=0):
    stats["nodes"] += 1
    stats["max_depth"] = max(stats["max_depth"], depth)

    if len(assignment) == len(problem["variables"]):
        events.append({"event": "solution", "depth": depth, "assignment": serial_assignment(assignment)})
        return [dict(assignment)]

    variable = choose_mrv(problem, domains, assignment)
    events.append(
        {
            "event": "choose_variable",
            "depth": depth,
            "variable": variable,
            "domain_size": len(domains[variable]),
            "assignment": serial_assignment(assignment),
        }
    )

    solutions = []
    for value in domains[variable]:
        trial = dict(assignment)
        trial[variable] = value
        failures = failures_for(trial, problem["constraints"])
        events.append(
            {
                "event": "try_value",
                "depth": depth,
                "variable": variable,
                "value": list(value),
                "assignment": serial_assignment(trial),
                "consistent": not failures,
                "failures": failures,
            }
        )
        if failures:
            stats["branches_cut"] += 1
            continue

        reduced, removed_count = forward_check(problem, domains, trial, events, depth + 1)
        stats["values_pruned_by_forward_checking"] += removed_count
        empty_domains = [var for var, values in reduced.items() if not values]
        if empty_domains:
            stats["branches_cut"] += 1
            events.append(
                {
                    "event": "empty_domain",
                    "depth": depth + 1,
                    "variables": empty_domains,
                    "assignment": serial_assignment(trial),
                }
            )
            continue

        solutions.extend(backtrack(problem, trial, reduced, stats, events, depth + 1))
    return solutions


def normalize_solution(solution):
    return {key: list(value) for key, value in solution.items()}


def render_markdown(problem, raw_count, pruned_count, stats, solutions, events):
    first_choice = next((event for event in events if event["event"] == "choose_variable"), None)
    lines = [
        "# Decisión: traza de backtracking CSP",
        "",
        f"Problema: `{problem['name']}`.",
        "",
        "## Métricas",
        "",
        "| Métrica | Valor |",
        "|---|---:|",
        f"| Candidatos brutos | {raw_count} |",
        f"| Candidatos tras poda unaria | {pruned_count} |",
        f"| Nodos visitados | {stats['nodes']} |",
        f"| Ramas cortadas | {stats['branches_cut']} |",
        f"| Valores podados por forward checking | {stats['values_pruned_by_forward_checking']} |",
        f"| Profundidad máxima | {stats['max_depth']} |",
        f"| Soluciones | {len(solutions)} |",
        "",
        "## Primera decisión MRV",
        "",
    ]
    if first_choice:
        lines.append(
            f"MRV elige `{first_choice['variable']}` porque su dominio tiene {first_choice['domain_size']} valores tras la poda inicial."
        )

    lines.extend(
        [
            "",
            "## Soluciones",
            "",
            "| Solución |",
            "|---|",
        ]
    )
    for solution in solutions:
        text = ", ".join(f"{key}=({value[0]}, {value[1]})" for key, value in solution.items())
        lines.append(f"| {text} |")

    sample_events = events[:8]
    lines.extend(["", "## Primeros eventos de la traza", "", "```jsonl"])
    for event in sample_events:
        lines.append(json.dumps(event, ensure_ascii=False))
    lines.append("```")

    lines.extend(
        [
            "",
            "## Lectura técnica",
            "",
            "- La poda unaria reduce el espacio antes de empezar el árbol.",
            "- MRV elige primero las variables con menos margen.",
            "- Forward checking corta valores futuros incompatibles con la asignación actual.",
            "- La traza permite explicar el comportamiento del solver sin depender de intuiciones.",
        ]
    )
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--fail-on-invalid", action="store_true")
    args = parser.parse_args()

    problem = load_json(ROOT / "data" / "backtracking_problem.json")
    policy = load_json(ROOT / "contracts" / "backtracking_policy.json")

    raw_domains = {var: [as_tuple(value) for value in values] for var, values in problem["domains"].items()}
    raw_count = candidate_count(raw_domains)
    events = []
    domains = apply_unary_pruning(problem, events)
    pruned_count = candidate_count(domains)
    stats = {
        "nodes": 0,
        "branches_cut": 0,
        "values_pruned_by_forward_checking": 0,
        "max_depth": 0,
    }
    solutions = backtrack(problem, {}, domains, stats, events)
    normalized_solutions = [normalize_solution(solution) for solution in solutions]

    report = {
        "problem": problem["name"],
        "raw_candidates": raw_count,
        "unary_pruned_candidates": pruned_count,
        "initial_domains": serial_domains(domains),
        "stats": stats,
        "solutions": normalized_solutions,
        "trace_events": len(events),
    }

    output_dir = ROOT / "output"
    if args.write:
        output_dir.mkdir(exist_ok=True)
        (output_dir / "backtracking_report.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (output_dir / "backtracking_trace.jsonl").write_text(
            "\n".join(json.dumps(event, ensure_ascii=False) for event in events) + "\n",
            encoding="utf-8",
        )
        (output_dir / "backtracking_decision.md").write_text(
            render_markdown(problem, raw_count, pruned_count, stats, normalized_solutions, events) + "\n",
            encoding="utf-8",
        )

    first_choice = next((event for event in events if event["event"] == "choose_variable"), {})
    errors = []
    if raw_count != policy["expected_raw_candidates"]:
        errors.append("candidatos brutos inesperados")
    if pruned_count != policy["expected_unary_pruned_candidates"]:
        errors.append("candidatos podados inesperados")
    if len(solutions) != policy["expected_solutions"]:
        errors.append("número de soluciones inesperado")
    if stats["nodes"] > policy["max_nodes_with_forward_checking"]:
        errors.append("demasiados nodos visitados")
    if first_choice.get("variable") != policy["expected_first_variable"]:
        errors.append("MRV eligió una primera variable inesperada")
    if len(events) < policy["minimum_trace_events"]:
        errors.append("traza demasiado corta")

    print(f"candidatos_brutos: {raw_count}")
    print(f"candidatos_podados: {pruned_count}")
    print(f"nodos: {stats['nodes']}")
    print(f"soluciones: {len(solutions)}")
    print(f"eventos_traza: {len(events)}")
    print(f"errores_gate: {len(errors)}")
    print(f"salida: {output_dir if args.write else 'no escrita'}")

    if args.fail_on_invalid and errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(2)


if __name__ == "__main__":
    main()
