#!/usr/bin/env python3
import argparse
import itertools
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMPONENT_INDEX = {"hour": 0, "room": 1}


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def as_tuple(value):
    return tuple(value)


def normalize_assignment(assignment):
    return {key: as_tuple(value) for key, value in assignment.items()}


def component(value, name):
    return value[COMPONENT_INDEX[name]]


def raw_candidate_count(model):
    total = 1
    for values in model["domains"].values():
        total *= len(values)
    return total


def is_unary_domain_filter(constraint):
    return constraint["type"] == "component_equals" and len(constraint["scope"]) == 1


def value_passes_unary(value, constraint):
    return component(value, constraint["component"]) == constraint["value"]


def pruned_domains(model):
    domains = {var: [as_tuple(value) for value in values] for var, values in model["domains"].items()}
    for constraint in model["hard_constraints"]:
        if not is_unary_domain_filter(constraint):
            continue
        variable = constraint["variable"]
        domains[variable] = [
            value for value in domains[variable] if value_passes_unary(value, constraint)
        ]
    return domains


def candidate_count(domains):
    total = 1
    for values in domains.values():
        total *= len(values)
    return total


def check_constraint(assignment, constraint):
    ctype = constraint["type"]
    if ctype == "component_equals":
        value = assignment[constraint["variable"]]
        ok = component(value, constraint["component"]) == constraint["value"]
        detail = f"{constraint['variable']}={value}, esperado {constraint['component']}={constraint['value']}"
    elif ctype == "component_not_equals":
        left = assignment[constraint["left"]]
        right = assignment[constraint["right"]]
        ok = component(left, constraint["component"]) != component(right, constraint["component"])
        detail = f"{constraint['left']}={left}, {constraint['right']}={right}"
    elif ctype == "all_different_values":
        values = [assignment[variable] for variable in constraint["scope"]]
        ok = len(set(values)) == len(values)
        detail = ", ".join(f"{variable}={assignment[variable]}" for variable in constraint["scope"])
    else:
        raise ValueError(f"restricción desconocida: {ctype}")
    return ok, detail


def failures_for(assignment, constraints):
    failures = []
    for constraint in constraints:
        ok, detail = check_constraint(assignment, constraint)
        if not ok:
            failures.append(
                {
                    "id": constraint["id"],
                    "arity": len(constraint["scope"]),
                    "detail": detail,
                    "explain": constraint["explain"],
                }
            )
    return failures


def preference_cost(assignment, preferences):
    total = 0
    details = []
    for preference in preferences:
        value = assignment[preference["variable"]]
        ok = component(value, preference["component"]) == preference["value"]
        penalty = 0 if ok else preference["penalty"]
        total += penalty
        details.append(
            {
                "id": preference["id"],
                "satisfied": ok,
                "penalty": penalty,
                "detail": f"{preference['variable']}={value}, preferido {preference['component']}={preference['value']}",
                "explain": preference["explain"],
            }
        )
    return total, details


def enumerate_solutions(model, domains):
    variables = list(model["variables"])
    values_by_variable = [domains[variable] for variable in variables]
    solutions = []
    failure_counter = Counter()
    tested = 0
    for values in itertools.product(*values_by_variable):
        tested += 1
        assignment = dict(zip(variables, values))
        failures = failures_for(assignment, model["hard_constraints"])
        if failures:
            for failure in failures:
                failure_counter[failure["id"]] += 1
            continue
        cost, preferences = preference_cost(assignment, model["soft_preferences"])
        solutions.append(
            {
                "assignment": {key: list(value) for key, value in assignment.items()},
                "cost": cost,
                "preferences": preferences,
            }
        )
    solutions.sort(key=lambda row: (row["cost"], json.dumps(row["assignment"], sort_keys=True)))
    return tested, solutions, failure_counter


def validate_candidates(model):
    rows = []
    for name, assignment in model["candidate_schedules"].items():
        normalized = normalize_assignment(assignment)
        failures = failures_for(normalized, model["hard_constraints"])
        cost, preferences = preference_cost(normalized, model["soft_preferences"])
        rows.append(
            {
                "name": name,
                "assignment": {key: list(value) for key, value in normalized.items()},
                "valid": not failures,
                "failures": failures,
                "cost": cost if not failures else None,
                "preferences": preferences if not failures else [],
            }
        )
    return rows


def assignment_text(assignment):
    return ", ".join(f"{key}=({value[0]}, {value[1]})" for key, value in assignment.items())


def render_markdown(model, raw_count, domains, pruned_count, tested, solutions, failure_counter, candidates):
    best = solutions[0] if solutions else None
    lines = [
        "# Decisión: auditoría de modelo CSP",
        "",
        f"Modelo: `{model['name']}`.",
        "",
        "## Variables y dominios",
        "",
        "| Variable | Dominio original | Dominio podado |",
        "|---|---:|---:|",
    ]
    for variable in model["variables"]:
        lines.append(
            f"| {variable} | {len(model['domains'][variable])} | {len(domains[variable])} |"
        )

    lines.extend(
        [
            "",
            "## Tamaño del espacio",
            "",
            f"- Candidatos brutos: {raw_count}.",
            f"- Candidatos tras podar dominios unarios: {pruned_count}.",
            f"- Candidatos evaluados después de podar: {tested}.",
            f"- Soluciones válidas: {len(solutions)}.",
            "",
            "## Restricciones",
            "",
            "| Restricción | Aridad | Tipo | Explicación |",
            "|---|---:|---|---|",
        ]
    )
    for constraint in model["hard_constraints"]:
        lines.append(
            f"| {constraint['id']} | {len(constraint['scope'])} | {constraint['type']} | {constraint['explain']} |"
        )

    lines.extend(
        [
            "",
            "## Soluciones válidas",
            "",
            "| Solución | Coste blando |",
            "|---|---:|",
        ]
    )
    for row in solutions:
        lines.append(f"| {assignment_text(row['assignment'])} | {row['cost']} |")

    lines.extend(["", "## Mejor solución", ""])
    if best:
        lines.append(f"**{assignment_text(best['assignment'])}** con coste {best['cost']}.")
    else:
        lines.append("No hay solución válida.")

    lines.extend(
        [
            "",
            "## Rechazos por restricción",
            "",
            "| Restricción | Candidatos rechazados |",
            "|---|---:|",
        ]
    )
    for constraint_id, count in failure_counter.most_common():
        lines.append(f"| {constraint_id} | {count} |")

    lines.extend(
        [
            "",
            "## Candidatos manuales",
            "",
            "| Candidato | Estado | Coste | Motivo |",
            "|---|---|---:|---|",
        ]
    )
    for row in candidates:
        if row["valid"]:
            status = "válido"
            cost = row["cost"]
            reason = "cumple reglas duras"
        else:
            status = "rechazado"
            cost = ""
            reason = "; ".join(f"{failure['id']}: {failure['detail']}" for failure in row["failures"])
        lines.append(f"| {row['name']} | {status} | {cost} | {reason} |")

    lines.extend(
        [
            "",
            "## Lectura técnica",
            "",
            "- La poda unaria reduce el espacio antes de probar combinaciones completas.",
            "- Las restricciones binarias y globales explican por qué se rechaza cada candidato.",
            "- Las preferencias blandas solo ordenan soluciones que ya cumplen las reglas duras.",
            "- Si una restricción aparece como causa de muchos rechazos, conviene revisar si está bien modelada o si el dominio debería limpiarse antes.",
        ]
    )
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--fail-on-invalid", action="store_true")
    args = parser.parse_args()

    model = load_json(ROOT / "data" / "course_schedule_model.json")
    policy = load_json(ROOT / "contracts" / "csp_model_policy.json")

    raw_count = raw_candidate_count(model)
    domains = pruned_domains(model)
    pruned_count = candidate_count(domains)
    tested, solutions, failure_counter = enumerate_solutions(model, domains)
    candidates = validate_candidates(model)

    report = {
        "model": model["name"],
        "raw_candidates": raw_count,
        "pruned_candidates": pruned_count,
        "tested_after_pruning": tested,
        "pruned_domains": {key: [list(value) for value in values] for key, values in domains.items()},
        "solutions": solutions,
        "best_solution": solutions[0] if solutions else None,
        "rejections_by_constraint": dict(failure_counter),
        "candidate_checks": candidates,
    }

    output_dir = ROOT / "output"
    if args.write:
        output_dir.mkdir(exist_ok=True)
        (output_dir / "csp_model_report.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (output_dir / "csp_model_decision.md").write_text(
            render_markdown(model, raw_count, domains, pruned_count, tested, solutions, failure_counter, candidates) + "\n",
            encoding="utf-8",
        )

    errors = []
    if raw_count != policy["expected_raw_candidates"]:
        errors.append("tamaño bruto inesperado")
    if pruned_count != policy["expected_pruned_candidates"]:
        errors.append("tamaño podado inesperado")
    if len(solutions) != policy["expected_valid_solutions"]:
        errors.append("número de soluciones inesperado")
    best = solutions[0] if solutions else None
    if not best or best["assignment"] != policy["expected_best_solution"]:
        errors.append("mejor solución inesperada")
    if not best or best["cost"] != policy["expected_best_cost"]:
        errors.append("coste de mejor solución inesperado")
    for variable, expected_size in policy["expected_pruned_domains"].items():
        if len(domains[variable]) != expected_size:
            errors.append(f"dominio podado inesperado para {variable}")

    print(f"candidatos_brutos: {raw_count}")
    print(f"candidatos_podados: {pruned_count}")
    print(f"soluciones: {len(solutions)}")
    print(f"errores_gate: {len(errors)}")
    print(f"salida: {output_dir if args.write else 'no escrita'}")

    if args.fail_on_invalid and errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(2)


if __name__ == "__main__":
    main()
