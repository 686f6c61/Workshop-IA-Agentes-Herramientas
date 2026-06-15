#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def layer_pairs(candidate):
    dims = [candidate["input_dim"]] + candidate["hidden_layers"] + [candidate["output_dim"]]
    return list(zip(dims[:-1], dims[1:]))


def count_parameters(candidate):
    total = 0
    shapes = []
    for index, (din, dout) in enumerate(layer_pairs(candidate), start=1):
        weights = din * dout
        biases = dout
        params = weights + biases
        total += params
        shapes.append(
            {
                "layer": index,
                "input_dim": din,
                "output_dim": dout,
                "weight_shape": [dout, din],
                "bias_shape": [dout],
                "parameters": params,
            }
        )
    return total, shapes


def memory_estimate(parameters, policy):
    return {
        precision: round(parameters * bytes_per_param / (1024 * 1024), 4)
        for precision, bytes_per_param in policy["bytes_per_parameter"].items()
    }


def validate_output_contract(candidate, policy):
    errors = []
    task = candidate["task"]
    if task not in policy["allowed_tasks"]:
        return [f"tarea no permitida: {task}"]

    rule = policy["output_rules"][task]
    if "output_dim" in rule and candidate["output_dim"] != rule["output_dim"]:
        errors.append(f"{task} espera output_dim={rule['output_dim']}")
    if "min_output_dim" in rule and candidate["output_dim"] < rule["min_output_dim"]:
        errors.append(f"{task} espera al menos {rule['min_output_dim']} salidas")
    if candidate["output_activation"] != rule["activation"]:
        errors.append(f"{task} espera activación {rule['activation']}")
    return errors


def validate_basic_fields(candidate):
    errors = []
    for field in ["id", "task", "input_dim", "hidden_layers", "output_dim", "output_activation", "training_examples"]:
        if field not in candidate:
            errors.append(f"falta campo {field}")
    if errors:
        return errors

    if candidate["input_dim"] <= 0:
        errors.append("input_dim debe ser positivo")
    if candidate["output_dim"] <= 0:
        errors.append("output_dim debe ser positivo")
    if any(layer <= 0 for layer in candidate["hidden_layers"]):
        errors.append("todas las capas ocultas deben ser positivas")
    if candidate["training_examples"] <= 0:
        errors.append("training_examples debe ser positivo")
    return errors


def evaluate_candidate(candidate, policy):
    errors = validate_basic_fields(candidate)
    expected_valid = candidate.get("expected_valid", True)
    total_parameters, shapes = (0, [])
    if not errors:
        total_parameters, shapes = count_parameters(candidate)
        errors.extend(validate_output_contract(candidate, policy))

    examples_per_parameter = (
        round(candidate["training_examples"] / total_parameters, 6)
        if total_parameters
        else 0
    )
    warnings = []

    if not errors:
        if total_parameters > policy["max_parameters_for_intro_lab"]:
            warnings.append("demasiados parámetros para el laboratorio introductorio")
        if examples_per_parameter < policy["min_examples_per_parameter"]:
            warnings.append("muy pocos ejemplos por parámetro")
        elif examples_per_parameter < policy["warning_examples_per_parameter"]:
            warnings.append("relación ejemplos/parámetro baja; exige validación fuerte")
        class_balance = candidate.get("class_balance")
        if class_balance is not None and class_balance < policy["min_class_balance"]:
            warnings.append("clase minoritaria muy pequeña; accuracy puede engañar")

    valid = not errors
    status = "invalid" if errors else ("warning" if warnings else "ok")
    return {
        "id": candidate.get("id", "sin_id"),
        "description": candidate.get("description", ""),
        "task": candidate.get("task"),
        "architecture": [candidate.get("input_dim")] + candidate.get("hidden_layers", []) + [candidate.get("output_dim")],
        "output_contract": {
            "output_dim": candidate.get("output_dim"),
            "activation": candidate.get("output_activation"),
        },
        "training_examples": candidate.get("training_examples"),
        "class_balance": candidate.get("class_balance"),
        "valid": valid,
        "expected_valid": expected_valid,
        "matches_expectation": valid == expected_valid,
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "layer_shapes": shapes,
        "total_parameters": total_parameters,
        "examples_per_parameter": examples_per_parameter,
        "memory_estimate_mb": memory_estimate(total_parameters, policy) if total_parameters else {},
    }


def recommendation(row):
    if not row["valid"]:
        return "corregir contrato antes de entrenar"
    if row["warnings"]:
        return "entrenar solo como experimento controlado y comparar con una base más simple"
    return "candidato razonable para primer entrenamiento"


def render_markdown(rows):
    lines = [
        "# Decisión: presupuesto de arquitectura neuronal",
        "",
        "Una arquitectura se puede revisar antes de entrenar: contrato de salida, formas, parámetros, memoria mínima y relación entre datos y capacidad.",
        "",
        "| Candidato | Arquitectura | Parámetros | Ejemplos/parámetro | Memoria BF16 MB | Estado | Decisión |",
        "|---|---|---:|---:|---:|---|---|",
    ]
    for row in rows:
        architecture = " -> ".join(str(value) for value in row["architecture"])
        bf16 = row["memory_estimate_mb"].get("bf16", "-")
        state_parts = []
        if row["errors"]:
            state_parts.extend(row["errors"])
        if row["warnings"]:
            state_parts.extend(row["warnings"])
        state = "; ".join(state_parts) if state_parts else "ok"
        lines.append(
            f"| `{row['id']}` | {architecture} | {row['total_parameters']} | "
            f"{row['examples_per_parameter']} | {bf16} | {state} | {recommendation(row)} |"
        )

    lines.extend(["", "## Formas por capa", ""])
    for row in rows:
        if not row["layer_shapes"]:
            continue
        lines.append(f"### {row['id']}")
        lines.append("")
        lines.append("| Capa | W | b | Parámetros |")
        lines.append("|---:|---|---|---:|")
        for shape in row["layer_shapes"]:
            w = f"{shape['weight_shape'][0]} x {shape['weight_shape'][1]}"
            b = str(shape["bias_shape"][0])
            lines.append(f"| {shape['layer']} | {w} | {b} | {shape['parameters']} |")
        lines.append("")

    lines.extend(
        [
            "## Lectura técnica",
            "",
            "- Un candidato `invalid` no debe entrenarse: primero se arregla el contrato de salida.",
            "- Un candidato con `warning` puede ser útil, pero exige comparación con una base sencilla y validación fuera de entrenamiento.",
            "- La memoria de pesos no es la memoria total de entrenamiento: faltan activaciones, gradientes y estados del optimizador.",
            "- El conteo de parámetros no mide calidad. Sirve para discutir capacidad, coste y riesgo.",
        ]
    )
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--fail-on-invalid", action="store_true")
    args = parser.parse_args()

    policy = load_json(ROOT / "contracts" / "architecture_policy.json")
    candidates = load_json(ROOT / "data" / "architecture_candidates.json")
    rows = [evaluate_candidate(candidate, policy) for candidate in candidates]

    output_dir = ROOT / "output"
    if args.write:
        output_dir.mkdir(exist_ok=True)
        (output_dir / "architecture_report.json").write_text(
            json.dumps(rows, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (output_dir / "architecture_decision.md").write_text(
            render_markdown(rows) + "\n",
            encoding="utf-8",
        )

    unexpected = [row for row in rows if not row["matches_expectation"]]
    invalid = [row for row in rows if not row["valid"]]
    warnings = [row for row in rows if row["warnings"]]
    print(f"candidatos: {len(rows)}")
    print(f"invalidos: {len(invalid)}")
    print(f"warnings: {len(warnings)}")
    print(f"salida: {output_dir if args.write else 'no escrita'}")

    if args.fail_on_invalid and unexpected:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
