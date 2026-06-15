#!/usr/bin/env python3
import argparse
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def estimate_nodes(branching_factor, depth):
    if branching_factor == 0:
        return 1
    if branching_factor == 1:
        return depth + 1
    return int((branching_factor ** (depth + 1) - 1) / (branching_factor - 1))


def validate_problem(problem, policy):
    states = set(problem.get("states", []))
    errors = []
    warnings = []

    if problem.get("initial_state") not in states:
        errors.append("initial_state no pertenece a states")

    for goal in problem.get("goals", []):
        if goal not in states:
            errors.append(f"meta fuera de states: {goal}")

    action_ids = set()
    for action in problem.get("actions", []):
        action_id = action.get("id")
        if not action_id:
            errors.append("acción sin id")
            continue
        if action_id in action_ids:
            errors.append(f"acción duplicada: {action_id}")
        action_ids.add(action_id)

        if action.get("from") not in states:
            errors.append(f"origen fuera de states en {action_id}: {action.get('from')}")
        if action.get("to") not in states:
            errors.append(f"destino fuera de states en {action_id}: {action.get('to')}")
        if "cost" not in action:
            errors.append(f"acción sin coste: {action_id}")
        elif policy["require_non_negative_costs"] and action["cost"] < 0:
            errors.append(f"coste negativo en {action_id}")

    adjacency = defaultdict(list)
    for action in problem.get("actions", []):
        adjacency[action.get("from")].append(action)

    branching_values = [len(adjacency[state]) for state in states]
    branching_factor = sum(branching_values) / len(branching_values) if branching_values else 0
    depth = problem.get("depth_estimate", policy["default_depth_estimate"])
    estimated = estimate_nodes(branching_factor, depth)

    if estimated > policy["max_estimated_nodes_warning"]:
        warnings.append("explosión combinatoria alta; necesita heurística, poda o redefinir estado")
    elif estimated > policy["max_estimated_nodes_ok"]:
        warnings.append("espacio manejable solo con cuidado; evita búsqueda ciega profunda")

    has_cycle = any(
        action.get("to") == other.get("from") and action.get("from") == other.get("to")
        for action in problem.get("actions", [])
        for other in problem.get("actions", [])
        if action.get("id") != other.get("id")
    )
    if has_cycle:
        warnings.append("hay ciclos; el algoritmo debe mantener visitados")

    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "branching_factor": round(branching_factor, 4),
        "depth_estimate": depth,
        "estimated_nodes": estimated,
        "has_cycle": has_cycle,
    }


def evaluate_plan(problem, plan):
    actions_by_id = {action["id"]: action for action in problem["actions"]}
    current = problem["initial_state"]
    path = [current]
    total_cost = 0
    errors = []

    for action_id in plan["actions"]:
        action = actions_by_id.get(action_id)
        if not action:
            errors.append(f"acción inexistente: {action_id}")
            break
        if action["from"] != current:
            errors.append(
                f"acción {action_id} requiere origen {action['from']}, pero el estado actual es {current}"
            )
            break
        current = action["to"]
        total_cost += action["cost"]
        path.append(current)

    reaches_goal = current in set(problem["goals"])
    if not reaches_goal and not errors:
        errors.append(f"el plan termina en {current}, que no pertenece a goals")

    repeated_states = sorted({state for state in path if path.count(state) > 1})
    return {
        "id": plan["id"],
        "actions": plan["actions"],
        "path": path,
        "cost": total_cost,
        "reaches_goal": reaches_goal,
        "valid": not errors,
        "errors": errors,
        "repeated_states": repeated_states,
    }


def render_markdown(problem, validation, plans):
    lines = [
        "# Decisión: contrato de búsqueda",
        "",
        f"Problema: `{problem['name']}`.",
        "",
        "| Elemento | Valor |",
        "|---|---|",
        f"| Estados | {len(problem['states'])} |",
        f"| Acciones | {len(problem['actions'])} |",
        f"| Estado inicial | `{problem['initial_state']}` |",
        f"| Metas | {', '.join(f'`{goal}`' for goal in problem['goals'])} |",
        f"| Factor de ramificación medio | {validation['branching_factor']} |",
        f"| Profundidad estimada | {validation['depth_estimate']} |",
        f"| Nodos estimados | {validation['estimated_nodes']} |",
        f"| Ciclos | {'sí' if validation['has_cycle'] else 'no'} |",
        "",
    ]

    status = "válido" if validation["valid"] else "inválido"
    messages = validation["errors"] + validation["warnings"]
    lines.extend(
        [
            "## Estado del modelo",
            "",
            f"Estado: **{status}**.",
            "",
        ]
    )
    if messages:
        for message in messages:
            lines.append(f"- {message}")
    else:
        lines.append("- Sin errores ni avisos relevantes.")

    lines.extend(
        [
            "",
            "## Planes candidatos",
            "",
            "| Plan | Camino | Coste | ¿Solución? | Observación |",
            "|---|---|---:|---|---|",
        ]
    )
    for plan in plans:
        observation = "; ".join(plan["errors"]) if plan["errors"] else "llega a meta"
        if plan["repeated_states"]:
            observation += f"; repite estados: {', '.join(plan['repeated_states'])}"
        lines.append(
            f"| `{plan['id']}` | {' -> '.join(plan['path'])} | {plan['cost']} | "
            f"{'sí' if plan['valid'] else 'no'} | {observation} |"
        )

    valid_plans = [plan for plan in plans if plan["valid"]]
    if valid_plans:
        best = min(valid_plans, key=lambda item: item["cost"])
        lines.extend(
            [
                "",
                "## Decisión",
                "",
                f"El mejor plan candidato válido es `{best['id']}` con coste {best['cost']}.",
                "",
                "Esta conclusión no demuestra optimalidad global: solo compara los planes candidatos. Para demostrar optimalidad necesitas ejecutar un algoritmo con garantías, como UCS o A* con una heurística admisible.",
            ]
        )
    else:
        lines.extend(["", "## Decisión", "", "No hay planes candidatos válidos. Primero corrige el modelo o añade planes ejecutables."])

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--fail-on-invalid", action="store_true")
    args = parser.parse_args()

    problem = load_json(ROOT / "data" / "search_problem.json")
    policy = load_json(ROOT / "contracts" / "search_policy.json")
    validation = validate_problem(problem, policy)
    plans = [evaluate_plan(problem, plan) for plan in problem.get("candidate_plans", [])]
    report = {"problem": problem["name"], "validation": validation, "plans": plans}

    output_dir = ROOT / "output"
    if args.write:
        output_dir.mkdir(exist_ok=True)
        (output_dir / "search_model_report.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (output_dir / "search_model_decision.md").write_text(
            render_markdown(problem, validation, plans) + "\n",
            encoding="utf-8",
        )

    invalid_plans = [plan for plan in plans if not plan["valid"]]
    print(f"modelo_valido: {validation['valid']}")
    print(f"planes: {len(plans)}")
    print(f"planes_invalidos: {len(invalid_plans)}")
    print(f"salida: {output_dir if args.write else 'no escrita'}")

    if args.fail_on_invalid and not validation["valid"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
