#!/usr/bin/env python3
import argparse
import itertools
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def literal_value(literal, assignment):
    if literal.startswith("!"):
        return not assignment[literal[1:]]
    return assignment[literal]


def clause_value(clause, assignment):
    return any(literal_value(literal, assignment) for literal in clause)


def enumerate_sat(sat_case):
    variables = list(sat_case["variables"])
    rows = []
    models = []
    for values in itertools.product([False, True], repeat=len(variables)):
        assignment = dict(zip(variables, values))
        clause_results = [clause_value(clause, assignment) for clause in sat_case["clauses"]]
        row = {
            "assignment": assignment,
            "clause_results": clause_results,
            "satisfies": all(clause_results),
        }
        rows.append(row)
        if row["satisfies"]:
            models.append(assignment)
    return rows, models


def check_constraint(schedule, constraint):
    left = constraint["left"]
    if constraint["type"] == "not_equals":
        right = constraint["right"]
        ok = schedule[left] != schedule[right]
        detail = f"{left}={schedule[left]} y {right}={schedule[right]}"
    elif constraint["type"] == "equals_value":
        ok = schedule[left] == constraint["value"]
        detail = f"{left}={schedule[left]}, esperado {constraint['value']}"
    else:
        raise ValueError(f"restricción desconocida: {constraint['type']}")
    return ok, detail


def hard_failures(schedule, constraints):
    failures = []
    for constraint in constraints:
        ok, detail = check_constraint(schedule, constraint)
        if not ok:
            failures.append(
                {
                    "id": constraint["id"],
                    "detail": detail,
                    "explain": constraint["explain"],
                }
            )
    return failures


def preference_cost(schedule, preferences):
    total = 0
    details = []
    for preference in preferences:
        if preference["type"] != "prefer_value":
            raise ValueError(f"preferencia desconocida: {preference['type']}")
        left = preference["left"]
        ok = schedule[left] == preference["value"]
        penalty = 0 if ok else preference["penalty"]
        total += penalty
        details.append(
            {
                "id": preference["id"],
                "satisfied": ok,
                "penalty": penalty,
                "detail": f"{left}={schedule[left]}, preferido {preference['value']}",
                "explain": preference["explain"],
            }
        )
    return total, details


def enumerate_csp(csp_case):
    variables = list(csp_case["variables"])
    domains = [csp_case["domains"][variable] for variable in variables]
    solutions = []
    tested = 0
    for values in itertools.product(*domains):
        tested += 1
        schedule = dict(zip(variables, values))
        failures = hard_failures(schedule, csp_case["hard_constraints"])
        if failures:
            continue
        cost, preference_details = preference_cost(schedule, csp_case["soft_preferences"])
        solutions.append(
            {
                "assignment": schedule,
                "cost": cost,
                "preferences": preference_details,
            }
        )
    solutions.sort(key=lambda row: (row["cost"], tuple(row["assignment"][v] for v in variables)))
    return tested, solutions


def validate_candidates(csp_case):
    rows = []
    for name, schedule in csp_case["candidate_schedules"].items():
        failures = hard_failures(schedule, csp_case["hard_constraints"])
        cost, preferences = preference_cost(schedule, csp_case["soft_preferences"])
        rows.append(
            {
                "name": name,
                "assignment": schedule,
                "valid": not failures,
                "failures": failures,
                "cost": cost if not failures else None,
                "preferences": preferences if not failures else [],
            }
        )
    return rows


def bool_text(value):
    return "1" if value else "0"


def assignment_text(assignment):
    return ", ".join(f"{key}={value}" for key, value in assignment.items())


def render_markdown(case, sat_rows, sat_models, csp_tested, csp_solutions, candidates):
    best = csp_solutions[0] if csp_solutions else None
    lines = [
        "# Decisión: SAT y CSP verificables",
        "",
        "## SAT: campaña con aprobación legal",
        "",
        f"Asignaciones probadas: {len(sat_rows)}. Modelos encontrados: {len(sat_models)}.",
        "",
        "| Modelo | A email | B banner | C legal |",
        "|---:|---:|---:|---:|",
    ]
    for idx, model in enumerate(sat_models, start=1):
        lines.append(
            f"| {idx} | {bool_text(model['A'])} | {bool_text(model['B'])} | {bool_text(model['C'])} |"
        )

    lines.extend(
        [
            "",
            "## CSP: agenda con reglas duras y preferencias",
            "",
            f"Asignaciones probadas: {csp_tested}. Soluciones válidas: {len(csp_solutions)}.",
            "",
            "| Agenda válida | Coste blando |",
            "|---|---:|",
        ]
    )
    for row in csp_solutions:
        lines.append(f"| {assignment_text(row['assignment'])} | {row['cost']} |")

    lines.extend(["", "## Mejor agenda válida", ""])
    if best:
        lines.append(f"**{assignment_text(best['assignment'])}** con coste {best['cost']}.")
        lines.append("")
        lines.append("No gana por ser la única posible: gana porque cumple todas las reglas duras y además minimiza preferencias blandas.")
    else:
        lines.append("No existe agenda válida con las restricciones actuales.")

    lines.extend(
        [
            "",
            "## Validación de candidatos",
            "",
            "| Candidato | Estado | Coste | Explicación |",
            "|---|---|---:|---|",
        ]
    )
    for row in candidates:
        if row["valid"]:
            explanation = "cumple reglas duras"
            cost = row["cost"]
            status = "válido"
        else:
            explanation = "; ".join(f"{failure['id']}: {failure['detail']}" for failure in row["failures"])
            cost = ""
            status = "rechazado"
        lines.append(f"| {row['name']} | {status} | {cost} | {explanation} |")

    lines.extend(
        [
            "",
            "## Lectura técnica",
            "",
            "- SAT trabaja con interruptores. Aquí prueba 2^3 asignaciones y conserva las que satisfacen todas las cláusulas.",
            "- CSP trabaja con variables y dominios. Aquí prueba 3^3 agendas antes de filtrar restricciones duras.",
            "- Las preferencias blandas no hacen válida una agenda inválida: solo ordenan las que ya pasaron las reglas duras.",
            "- Este patrón es directamente trasladable a permisos, configuración de producto, turnos, reservas y validación de acciones de agentes.",
        ]
    )
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--fail-on-invalid", action="store_true")
    args = parser.parse_args()

    case = load_json(ROOT / "data" / "constraint_case.json")
    policy = load_json(ROOT / "contracts" / "constraint_policy.json")

    sat_rows, sat_models = enumerate_sat(case["sat"])
    csp_tested, csp_solutions = enumerate_csp(case["csp"])
    candidates = validate_candidates(case["csp"])

    report = {
        "sat": {
            "assignments_tested": len(sat_rows),
            "models": sat_models,
        },
        "csp": {
            "assignments_tested": csp_tested,
            "solutions": csp_solutions,
            "best": csp_solutions[0] if csp_solutions else None,
            "candidates": candidates,
        },
    }

    output_dir = ROOT / "output"
    if args.write:
        output_dir.mkdir(exist_ok=True)
        (output_dir / "constraint_report.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (output_dir / "constraint_decision.md").write_text(
            render_markdown(case, sat_rows, sat_models, csp_tested, csp_solutions, candidates) + "\n",
            encoding="utf-8",
        )

    errors = []
    if len(sat_rows) != policy["expected_sat_assignments_tested"]:
        errors.append("número inesperado de asignaciones SAT")
    if len(sat_models) != policy["expected_sat_models"]:
        errors.append("número inesperado de modelos SAT")
    if len(csp_solutions) < policy["minimum_csp_solutions"]:
        errors.append("demasiadas pocas soluciones CSP")

    best = csp_solutions[0] if csp_solutions else None
    if not best or best["assignment"] != policy["expected_best_schedule"]:
        errors.append("mejor agenda inesperada")
    if not best or best["cost"] != policy["expected_best_schedule_cost"]:
        errors.append("coste de mejor agenda inesperado")

    invalid = {row["name"] for row in candidates if not row["valid"]}
    for expected in policy["expected_invalid_candidates"]:
        if expected not in invalid:
            errors.append(f"candidato inválido no rechazado: {expected}")

    print(f"sat_asignaciones: {len(sat_rows)}")
    print(f"sat_modelos: {len(sat_models)}")
    print(f"csp_asignaciones: {csp_tested}")
    print(f"csp_soluciones: {len(csp_solutions)}")
    print(f"errores_gate: {len(errors)}")
    print(f"salida: {output_dir if args.write else 'no escrita'}")

    if args.fail_on_invalid and errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(2)


if __name__ == "__main__":
    main()
