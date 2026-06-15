#!/usr/bin/env python3
import argparse
import json
import math
import random
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def softmax(logits, temperature):
    if temperature == 0:
        winner = max(range(len(logits)), key=lambda i: logits[i])
        return [1.0 if i == winner else 0.0 for i in range(len(logits))]
    scaled = [value / temperature for value in logits]
    offset = max(scaled)
    exps = [math.exp(value - offset) for value in scaled]
    total = sum(exps)
    return [value / total for value in exps]


def sample_index(probabilities, rng):
    pick = rng.random()
    total = 0.0
    for index, probability in enumerate(probabilities):
        total += probability
        if pick <= total:
            return index
    return len(probabilities) - 1


def passes_properties(text, properties):
    lowered = text.lower()
    if len(text) > properties["max_chars"]:
        return False
    for options in properties["must_contain_any"]:
        if not any(option.lower() in lowered for option in options):
            return False
    return True


def evaluate_case(case, policy, temperature):
    rng = random.Random(f"{policy['seed']}:{case['id']}:{temperature}")
    logits = [candidate["logit"] for candidate in case["candidates"]]
    probabilities = softmax(logits, temperature)
    rows = []
    for _ in range(policy["runs_per_case"]):
        idx = sample_index(probabilities, rng)
        text = case["candidates"][idx]["text"]
        rows.append(
            {
                "text": text,
                "exact": text == case["expected_exact"],
                "properties": passes_properties(text, case["properties"]),
            }
        )

    exact_pass = sum(row["exact"] for row in rows) / len(rows)
    property_pass = sum(row["properties"] for row in rows) / len(rows)
    unique_outputs = len({row["text"] for row in rows})
    gate_pass = property_pass >= policy["property_pass_min"]

    if case["task_type"] == "factual":
        gate_pass = gate_pass and unique_outputs <= policy["max_unique_outputs_for_factual"]

    return {
        "case_id": case["id"],
        "task_type": case["task_type"],
        "temperature": temperature,
        "probabilities": [
            {
                "text": candidate["text"],
                "logit": candidate["logit"],
                "probability": round(probabilities[index], 4),
            }
            for index, candidate in enumerate(case["candidates"])
        ],
        "exact_pass_rate": round(exact_pass, 4),
        "property_pass_rate": round(property_pass, 4),
        "unique_outputs": unique_outputs,
        "gate_pass": gate_pass,
    }


def render_decision(results, policy):
    lines = [
        "# Decisión: cómo testear una salida probabilística",
        "",
        "Un assert exacto mide si la frase coincide letra por letra. Una evaluación de propiedades mide si la salida conserva el contrato que importa.",
        "",
        f"Ejecuciones por caso: `{policy['runs_per_case']}`.",
        "",
        "| Caso | Temperatura | Exact pass | Property pass | Salidas únicas | Gate |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for row in results:
        lines.append(
            "| {case} | {temperature} | {exact:.2f} | {prop:.2f} | {unique} | {gate} |".format(
                case=row["case_id"],
                temperature=row["temperature"],
                exact=row["exact_pass_rate"],
                prop=row["property_pass_rate"],
                unique=row["unique_outputs"],
                gate="pasa" if row["gate_pass"] else "revisar",
            )
        )

    lines.extend(
        [
            "",
            "## Lectura técnica",
            "",
            "Si `exact_pass_rate` cae pero `property_pass_rate` se mantiene alto, el problema no es necesariamente el modelo: es el test.",
            "Si `property_pass_rate` cae al subir la temperatura, la tarea necesita muestreo más conservador, salida estructurada o una evaluación más fuerte.",
            "Si hay demasiadas salidas únicas en una tarea factual, el producto puede parecer inestable aunque muchas respuestas sean aceptables.",
        ]
    )
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--fail-on-gate", action="store_true")
    args = parser.parse_args()

    policy = load_json(ROOT / "contracts" / "eval_policy.json")
    cases = load_json(ROOT / "data" / "sampling_cases.json")

    results = []
    for case in cases:
        for temperature in policy["temperatures"]:
            results.append(evaluate_case(case, policy, temperature))

    output_dir = ROOT / "output"
    if args.write:
        output_dir.mkdir(exist_ok=True)
        (output_dir / "stochastic_eval_report.json").write_text(
            json.dumps(results, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (output_dir / "stochastic_eval_decision.md").write_text(
            render_decision(results, policy) + "\n",
            encoding="utf-8",
        )

    failing = [row for row in results if not row["gate_pass"]]
    print(f"casos_temperatura: {len(results)}")
    print(f"gates_a_revisar: {len(failing)}")
    print(f"salida: {output_dir if args.write else 'no escrita'}")

    if args.fail_on_gate and failing:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
