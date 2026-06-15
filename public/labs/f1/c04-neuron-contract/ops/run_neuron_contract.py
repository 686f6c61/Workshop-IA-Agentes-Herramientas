#!/usr/bin/env python3
import argparse
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def activate(value, activation):
    if activation == "linear":
        return value
    if activation == "relu":
        return max(0.0, value)
    if activation == "sigmoid":
        return 1.0 / (1.0 + math.exp(-value))
    raise ValueError(f"activación no permitida: {activation}")


def validate_case(case, policy):
    errors = []
    for field in policy["required_fields"]:
        if field not in case:
            errors.append(f"falta campo {field}")
    if errors:
        return errors

    if case["activation"] not in policy["allowed_activations"]:
        errors.append("activación no permitida")
    if len(case["inputs"]) != len(case["weights"]):
        errors.append("inputs y weights deben tener la misma dimensión")
    for name in ["inputs", "weights"]:
        if not all(isinstance(value, (int, float)) for value in case[name]):
            errors.append(f"{name} contiene valores no numéricos")
    if not isinstance(case["bias"], (int, float)):
        errors.append("bias debe ser numérico")
    return errors


def compute(case):
    z = sum(x * w for x, w in zip(case["inputs"], case["weights"])) + case["bias"]
    y = activate(z, case["activation"])
    return z, y


def sensitivity(case, policy):
    base_z, base_y = compute(case)
    delta = policy["sensitivity_delta"]
    rows = []

    for index in range(len(case["weights"])):
        changed = json.loads(json.dumps(case))
        changed["weights"][index] += delta
        _, changed_y = compute(changed)
        rows.append(
            {
                "parameter": f"w{index + 1}",
                "delta": delta,
                "output_change": round(changed_y - base_y, 10),
            }
        )

    changed = json.loads(json.dumps(case))
    changed["bias"] += delta
    _, changed_y = compute(changed)
    rows.append(
        {
            "parameter": "bias",
            "delta": delta,
            "output_change": round(changed_y - base_y, 10),
        }
    )
    return rows


def evaluate(cases, policy):
    rows = []
    tolerance = policy["tolerance"]
    for case in cases:
        errors = validate_case(case, policy)
        expected_valid = case.get("expected_valid", True)
        if errors:
            rows.append(
                {
                    "id": case.get("id", "sin_id"),
                    "valid": False,
                    "expected_valid": expected_valid,
                    "matches_expectation": expected_valid is False,
                    "errors": errors,
                }
            )
            continue

        z, y = compute(case)
        expected = case.get("expected_output")
        matches = expected is None or abs(y - expected) <= tolerance
        rows.append(
            {
                "id": case["id"],
                "valid": True,
                "expected_valid": expected_valid,
                "dimension": len(case["inputs"]),
                "activation": case["activation"],
                "z": round(z, 10),
                "output": round(y, 10),
                "expected_output": expected,
                "matches_expected": matches,
                "matches_expectation": expected_valid is True and matches,
                "sensitivity": sensitivity(case, policy),
            }
        )
    return rows


def render_markdown(rows):
    lines = [
        "# Decisión: neurona artificial con contrato",
        "",
        "Una neurona solo calcula si el contrato de entrada se cumple: misma dimensión para entradas y pesos, sesgo numérico y activación permitida.",
        "",
        "| Caso | Válido | Dimensión | Activación | z | salida | Estado |",
        "|---|---|---:|---|---:|---:|---|",
    ]
    for row in rows:
        if not row["valid"]:
            status = "fallo esperado" if row["matches_expectation"] else "revisar"
            lines.append(
                f"| {row['id']} | no | - | - | - | - | {status}: {'; '.join(row['errors'])} |"
            )
            continue
        status = "pasa" if row["matches_expectation"] else "revisar"
        lines.append(
            f"| {row['id']} | sí | {row['dimension']} | `{row['activation']}` | {row['z']} | {row['output']} | {status} |"
        )

    lines.extend(["", "## Sensibilidad", ""])
    for row in rows:
        if not row["valid"]:
            continue
        strongest = max(row["sensitivity"], key=lambda item: abs(item["output_change"]))
        lines.append(
            f"- `{row['id']}`: el mayor cambio de salida viene de `{strongest['parameter']}` "
            f"con variación {strongest['output_change']}."
        )
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--fail-on-invalid", action="store_true")
    args = parser.parse_args()

    cases = load_json(ROOT / "data" / "neuron_cases.json")
    policy = load_json(ROOT / "contracts" / "neuron_policy.json")
    rows = evaluate(cases, policy)

    output_dir = ROOT / "output"
    if args.write:
        output_dir.mkdir(exist_ok=True)
        (output_dir / "neuron_report.json").write_text(
            json.dumps(rows, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (output_dir / "neuron_decision.md").write_text(
            render_markdown(rows) + "\n",
            encoding="utf-8",
        )

    unexpected = [row for row in rows if not row["matches_expectation"]]
    invalid = [row for row in rows if not row["valid"]]
    mismatches = [row for row in rows if row["valid"] and not row["matches_expected"]]
    print(f"casos: {len(rows)}")
    print(f"invalidos: {len(invalid)}")
    print(f"mismatches: {len(mismatches)}")
    print(f"salida: {output_dir if args.write else 'no escrita'}")

    if args.fail_on_invalid and unexpected:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
