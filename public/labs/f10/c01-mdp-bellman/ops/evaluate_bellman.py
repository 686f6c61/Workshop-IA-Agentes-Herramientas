#!/usr/bin/env python3
import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = ROOT / "data" / "support_mdp.json"
DEFAULT_CONTRACT = ROOT / "contracts" / "bellman_contract.json"
DEFAULT_OUTPUT = ROOT / "output"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def validate_mdp(mdp, contract):
    errors = []
    states = set(mdp["states"])
    terminal = set(mdp["terminal_states"])
    non_terminal = states - terminal
    if len(non_terminal) < contract["min_non_terminal_states"]:
        errors.append("demasiados pocos estados no terminales")
    for state in terminal:
        if state in mdp.get("actions", {}):
            errors.append(f"estado terminal con acciones: {state}")
    for state, actions in mdp["actions"].items():
        if state not in states:
            errors.append(f"estado con acciones no declarado: {state}")
        for action in actions:
            transitions = mdp["transitions"].get(state, {}).get(action)
            if not transitions:
                errors.append(f"faltan transiciones para {state}.{action}")
                continue
            probability_mass = sum(float(row.get("probability", 0)) for row in transitions)
            if abs(probability_mass - contract["gate"]["require_probability_mass"]) > contract["gate"]["max_probability_error"]:
                errors.append(f"probabilidad no suma 1 en {state}.{action}: {probability_mass}")
            for row in transitions:
                for field in contract["required_transition_fields"]:
                    if field not in row:
                        errors.append(f"falta {field} en {state}.{action}")
                if row.get("next_state") not in states:
                    errors.append(f"siguiente estado no declarado en {state}.{action}: {row.get('next_state')}")
    return errors


def q_value(state, action, mdp, values, gamma):
    total = 0.0
    for row in mdp["transitions"][state][action]:
        total += float(row["probability"]) * (float(row["reward"]) + gamma * values[row["next_state"]])
    return total


def value_iteration(mdp, contract):
    gamma = float(contract["gamma"])
    values = {state: 0.0 for state in mdp["states"]}
    terminal = set(mdp["terminal_states"])
    iterations = []
    for iteration in range(1, int(contract["max_iterations"]) + 1):
        updated = values.copy()
        max_delta = 0.0
        for state in mdp["states"]:
            if state in terminal:
                continue
            candidates = [q_value(state, action, mdp, values, gamma) for action in mdp["actions"][state]]
            updated[state] = max(candidates)
            max_delta = max(max_delta, abs(updated[state] - values[state]))
        values = updated
        iterations.append({"iteration": iteration, "max_delta": round(max_delta, 10)})
        if max_delta <= float(contract["convergence_tolerance"]):
            break
    return values, iterations


def derive_policy(mdp, values, contract):
    gamma = float(contract["gamma"])
    rows = []
    policy = {}
    terminal = set(mdp["terminal_states"])
    for state in mdp["states"]:
        if state in terminal:
            continue
        scored = []
        for action in mdp["actions"][state]:
            score = q_value(state, action, mdp, values, gamma)
            scored.append((score, action))
            rows.append({
                "state": state,
                "action": action,
                "q_value": round(score, 6),
            })
        scored.sort(reverse=True)
        best_score, best_action = scored[0]
        margin = best_score - scored[1][0] if len(scored) > 1 else best_score
        policy[state] = {
            "action": best_action,
            "q_value": round(best_score, 6),
            "margin": round(margin, 6),
            "decision_confident": margin >= float(contract["gate"]["min_value_margin_for_decision"]),
        }
    return policy, rows


def render_decision(mdp, report):
    lines = [
        "# Decisión Bellman",
        "",
        f"Escenario: `{mdp['scenario_id']}`.",
        f"Estado del gate: `{'pass' if report['gate_ok'] else 'review'}`.",
        f"Gamma: `{report['gamma']}`.",
        f"Iteraciones: `{report['iterations']}`.",
        "",
        "## Política resultante",
        "",
        "| Estado | Acción elegida | Valor Q | Margen | Lectura |",
        "|---|---|---:|---:|---|",
    ]
    readings = {
        "nuevo": "pedir evidencia compensa porque aumenta la probabilidad de resolver con cita.",
        "evidencia": "responder con cita domina escalar si la evidencia ya está disponible.",
        "critico": "escalar evita respuestas directas con alto coste de reapertura.",
    }
    for state, row in report["policy"].items():
        lines.append(
            f"| `{state}` | `{row['action']}` | {row['q_value']} | {row['margin']} | {readings.get(state, 'decisión por valor esperado.')} |"
        )
    lines.extend([
        "",
        "## Decisión técnica",
        "",
        "Esta política puede usarse como ejercicio y como especificación inicial, no como despliegue directo. Para pasar a un sistema real harían falta eventos de interacción, trazas de propensión, evaluación offline y serving con política de reserva.",
        "",
        "## Qué cambiaría para experimentar",
        "",
        "- Subir el coste de `pedir_dato` para ver cuándo deja de compensar.",
        "- Reducir la probabilidad de éxito de `responder_con_cita` para detectar sensibilidad.",
        "- Cambiar `gamma` y observar si el sistema se vuelve más miope.",
        "- Añadir un estado `pendiente_legal` si la decisión depende de una revisión externa.",
        "",
    ])
    return "\n".join(lines)


def write_outputs(output_dir, mdp, report, q_rows):
    output_dir.mkdir(parents=True, exist_ok=True)
    write_json(output_dir / "policy_iteration_report.json", report)
    with (output_dir / "value_table.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["state", "value", "best_action", "margin"])
        writer.writeheader()
        for state in mdp["states"]:
            policy_row = report["policy"].get(state, {})
            writer.writerow({
                "state": state,
                "value": report["values"][state],
                "best_action": policy_row.get("action", "terminal"),
                "margin": policy_row.get("margin", ""),
            })
    with (output_dir / "q_values.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["state", "action", "q_value"])
        writer.writeheader()
        writer.writerows(q_rows)
    (output_dir / "bellman_decision.md").write_text(render_decision(mdp, report), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--fail-on-gate", action="store_true")
    args = parser.parse_args()

    mdp = read_json(args.data)
    contract = read_json(args.contract)
    validation_errors = validate_mdp(mdp, contract)
    values, iterations = value_iteration(mdp, contract) if not validation_errors else ({state: 0.0 for state in mdp["states"]}, [])
    policy, q_rows = derive_policy(mdp, values, contract) if not validation_errors else ({}, [])
    gate_ok = not validation_errors and all(row["decision_confident"] for row in policy.values())
    report = {
        "scenario_id": mdp["scenario_id"],
        "contract_version": contract["contract_version"],
        "gamma": contract["gamma"],
        "iterations": len(iterations),
        "last_delta": iterations[-1]["max_delta"] if iterations else None,
        "gate_ok": gate_ok,
        "validation_errors": validation_errors,
        "values": {state: round(value, 6) for state, value in values.items()},
        "policy": policy,
        "q_values": q_rows,
        "iteration_trace": iterations[-10:],
    }
    if args.write:
        write_outputs(args.output, mdp, report, q_rows)
    print(json.dumps({"gate_ok": gate_ok, "policy": {k: v["action"] for k, v in policy.items()}}, ensure_ascii=False, indent=2))
    if args.fail_on_gate and not gate_ok:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
