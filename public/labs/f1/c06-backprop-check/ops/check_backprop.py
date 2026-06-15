#!/usr/bin/env python3
import argparse
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sigmoid(z):
    if z >= 0:
        return 1.0 / (1.0 + math.exp(-z))
    ez = math.exp(z)
    return ez / (1.0 + ez)


def forward(case, w=None, b=None):
    w = case["w"] if w is None else w
    b = case["b"] if b is None else b
    z = w * case["x"] + b
    a = sigmoid(z)
    loss = 0.5 * (a - case["y"]) ** 2
    return z, a, loss


def analytic_gradients(case):
    z, a, loss = forward(case)
    dloss_da = a - case["y"]
    da_dz = a * (1.0 - a)
    dloss_dz = dloss_da * da_dz
    dloss_dw = dloss_dz * case["x"]
    dloss_db = dloss_dz
    return {
        "z": z,
        "a": a,
        "loss": loss,
        "dE_da": dloss_da,
        "da_dz": da_dz,
        "dE_dz": dloss_dz,
        "dE_dw": dloss_dw,
        "dE_db": dloss_db,
    }


def numeric_gradient(case, parameter, epsilon):
    if parameter == "w":
        _, _, loss_plus = forward(case, w=case["w"] + epsilon)
        _, _, loss_minus = forward(case, w=case["w"] - epsilon)
    elif parameter == "b":
        _, _, loss_plus = forward(case, b=case["b"] + epsilon)
        _, _, loss_minus = forward(case, b=case["b"] - epsilon)
    else:
        raise ValueError(f"parámetro no soportado: {parameter}")
    return (loss_plus - loss_minus) / (2.0 * epsilon)


def update(case, gradients, learning_rate, sign=-1.0):
    new_w = case["w"] + sign * learning_rate * gradients["dE_dw"]
    new_b = case["b"] + sign * learning_rate * gradients["dE_db"]
    _, _, new_loss = forward(case, w=new_w, b=new_b)
    delta_w = new_w - case["w"]
    update_ratio = abs(delta_w) / max(abs(case["w"]), 1e-12)
    return {
        "learning_rate": learning_rate,
        "w_after": new_w,
        "b_after": new_b,
        "loss_after": new_loss,
        "loss_delta": new_loss - gradients["loss"],
        "improves": new_loss < gradients["loss"],
        "update_ratio_w": update_ratio,
    }


def evaluate_case(case, policy):
    gradients = analytic_gradients(case)
    numeric = {
        "dE_dw": numeric_gradient(case, "w", policy["epsilon"]),
        "dE_db": numeric_gradient(case, "b", policy["epsilon"]),
    }
    errors = {
        "dE_dw": abs(gradients["dE_dw"] - numeric["dE_dw"]),
        "dE_db": abs(gradients["dE_db"] - numeric["dE_db"]),
    }
    gradient_check = all(error <= policy["gradient_tolerance"] for error in errors.values())
    grad_norm = math.sqrt(gradients["dE_dw"] ** 2 + gradients["dE_db"] ** 2)

    sweep = [
        update(case, gradients, learning_rate)
        for learning_rate in policy["learning_rates"]
    ]
    wrong_sign = update(case, gradients, 0.1, sign=1.0)

    warnings = []
    if grad_norm < policy["vanishing_gradient_threshold"]:
        warnings.append("gradiente casi nulo")
    if any(item["update_ratio_w"] > policy["exploding_update_ratio"] for item in sweep):
        warnings.append("algún learning rate mueve el peso más que su escala actual")

    return {
        "id": case["id"],
        "description": case["description"],
        "input": {"x": case["x"], "w": case["w"], "b": case["b"], "y": case["y"]},
        "forward": {
            "z": round(gradients["z"], 12),
            "a": round(gradients["a"], 12),
            "loss": round(gradients["loss"], 12),
        },
        "analytic_gradients": {k: round(v, 12) for k, v in gradients.items() if k.startswith("dE") or k == "da_dz"},
        "numeric_gradients": {k: round(v, 12) for k, v in numeric.items()},
        "gradient_error": {k: round(v, 12) for k, v in errors.items()},
        "gradient_check": gradient_check,
        "gradient_norm": round(grad_norm, 12),
        "learning_rate_sweep": [
            {
                "learning_rate": item["learning_rate"],
                "loss_after": round(item["loss_after"], 12),
                "loss_delta": round(item["loss_delta"], 12),
                "improves": item["improves"],
                "update_ratio_w": round(item["update_ratio_w"], 12),
            }
            for item in sweep
        ],
        "wrong_sign_loss": round(wrong_sign["loss_after"], 12),
        "warnings": warnings,
    }


def recommended_learning_rate(row):
    improving = [
        item
        for item in row["learning_rate_sweep"]
        if item["improves"] and item["update_ratio_w"] <= 0.5
    ]
    if not improving:
        return "ninguno"
    best = min(improving, key=lambda item: item["loss_after"])
    return str(best["learning_rate"])


def render_markdown(rows):
    lines = [
        "# Decisión: comprobación de retropropagación",
        "",
        "El informe compara gradientes analíticos contra diferencias finitas y revisa cómo cambia la pérdida con distintos learning rates.",
        "",
        "| Caso | Loss inicial | Grad norm | Check | Learning rate recomendado | Loss con signo contrario | Avisos |",
        "|---|---:|---:|---|---:|---:|---|",
    ]
    for row in rows:
        check = "pasa" if row["gradient_check"] else "revisar"
        warnings = "; ".join(row["warnings"]) if row["warnings"] else "ok"
        lines.append(
            f"| `{row['id']}` | {row['forward']['loss']} | {row['gradient_norm']} | {check} | "
            f"{recommended_learning_rate(row)} | {row['wrong_sign_loss']} | {warnings} |"
        )

    lines.extend(["", "## Gradientes", ""])
    for row in rows:
        lines.append(f"### {row['id']}")
        lines.append("")
        lines.append("| Parámetro | Analítico | Numérico | Error absoluto |")
        lines.append("|---|---:|---:|---:|")
        for name in ["dE_dw", "dE_db"]:
            lines.append(
                f"| `{name}` | {row['analytic_gradients'][name]} | "
                f"{row['numeric_gradients'][name]} | {row['gradient_error'][name]} |"
            )
        lines.append("")

    lines.extend(["## Barrido de learning rate", ""])
    for row in rows:
        lines.append(f"### {row['id']}")
        lines.append("")
        lines.append("| lr | Loss después | Cambio de loss | Mejora | Ratio actualización w |")
        lines.append("|---:|---:|---:|---|---:|")
        for item in row["learning_rate_sweep"]:
            improves = "sí" if item["improves"] else "no"
            lines.append(
                f"| {item['learning_rate']} | {item['loss_after']} | {item['loss_delta']} | "
                f"{improves} | {item['update_ratio_w']} |"
            )
        lines.append("")

    lines.extend(
        [
            "## Lectura técnica",
            "",
            "- Si el gradient check falla, primero se revisa la derivada, el signo y la función de pérdida.",
            "- Si el gradiente es casi cero, puede haber saturación o una cadena de activaciones que atenúa la señal.",
            "- Si el learning rate mejora con pasos pequeños pero empeora con pasos grandes, el problema no es la derivada: es la escala de actualización.",
            "- La actualización con signo contrario debe empeorar o no mejorar. Si mejora, has definido la pérdida o el signo de forma sospechosa.",
        ]
    )
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--fail-on-mismatch", action="store_true")
    args = parser.parse_args()

    policy = load_json(ROOT / "contracts" / "backprop_policy.json")
    cases = load_json(ROOT / "data" / "backprop_cases.json")
    rows = [evaluate_case(case, policy) for case in cases]

    output_dir = ROOT / "output"
    if args.write:
        output_dir.mkdir(exist_ok=True)
        (output_dir / "backprop_report.json").write_text(
            json.dumps(rows, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (output_dir / "backprop_decision.md").write_text(
            render_markdown(rows) + "\n",
            encoding="utf-8",
        )

    mismatches = [row for row in rows if not row["gradient_check"]]
    print(f"casos: {len(rows)}")
    print(f"gradient_check_fallos: {len(mismatches)}")
    print(f"salida: {output_dir if args.write else 'no escrita'}")

    if args.fail_on_mismatch and mismatches:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
