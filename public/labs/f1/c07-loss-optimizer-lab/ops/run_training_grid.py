#!/usr/bin/env python3
import argparse
import json
import math
import random
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sigmoid(z):
    if z >= 0:
        return 1.0 / (1.0 + math.exp(-z))
    ez = math.exp(z)
    return ez / (1.0 + ez)


def make_dataset(seed, examples):
    rng = random.Random(seed)
    rows = []
    for _ in range(examples):
        urgency = rng.gauss(0.0, 1.0)
        value = rng.gauss(0.0, 1.0)
        noise = rng.gauss(0.0, 0.55)
        score = 1.35 * urgency - 0.85 * value + 0.35 + noise
        label = 1 if score > 0 else 0
        rows.append(([urgency, value], label))
    rng.shuffle(rows)
    return rows


def split_dataset(rows, train_ratio):
    cut = int(len(rows) * train_ratio)
    return rows[:cut], rows[cut:]


def predict(params, x):
    return sigmoid(params["w1"] * x[0] + params["w2"] * x[1] + params["b"])


def loss_value(probability, label, loss_name):
    eps = 1e-12
    if loss_name == "bce":
        p = min(max(probability, eps), 1.0 - eps)
        return -(label * math.log(p) + (1 - label) * math.log(1 - p))
    if loss_name == "mse":
        return 0.5 * (probability - label) ** 2
    raise ValueError(f"pérdida no soportada: {loss_name}")


def gradients(params, rows, loss_name):
    grad = {"w1": 0.0, "w2": 0.0, "b": 0.0}
    total_loss = 0.0
    for x, label in rows:
        p = predict(params, x)
        total_loss += loss_value(p, label, loss_name)
        if loss_name == "bce":
            dloss_dz = p - label
        elif loss_name == "mse":
            dloss_dz = (p - label) * p * (1.0 - p)
        else:
            raise ValueError(f"pérdida no soportada: {loss_name}")
        grad["w1"] += dloss_dz * x[0]
        grad["w2"] += dloss_dz * x[1]
        grad["b"] += dloss_dz
    n = len(rows)
    return {k: v / n for k, v in grad.items()}, total_loss / n


def metrics(params, rows, loss_name):
    losses = []
    tp = fp = tn = fn = 0
    for x, label in rows:
        p = predict(params, x)
        losses.append(loss_value(p, label, loss_name))
        pred = 1 if p >= 0.5 else 0
        if pred == 1 and label == 1:
            tp += 1
        elif pred == 1 and label == 0:
            fp += 1
        elif pred == 0 and label == 0:
            tn += 1
        else:
            fn += 1
    accuracy = (tp + tn) / len(rows)
    precision = tp / max(tp + fp, 1)
    recall = tp / max(tp + fn, 1)
    f1 = 0.0 if precision + recall == 0 else 2 * precision * recall / (precision + recall)
    return {
        "loss": sum(losses) / len(losses),
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "confusion": {"tp": tp, "fp": fp, "tn": tn, "fn": fn},
    }


def train_sgd(params, grad, config):
    lr = config["learning_rate"]
    wd = config["weight_decay"]
    for key in ["w1", "w2"]:
        params[key] -= lr * (grad[key] + wd * params[key])
    params["b"] -= lr * grad["b"]


def train_adamw(params, grad, state, config, step):
    lr = config["learning_rate"]
    beta1 = 0.9
    beta2 = 0.999
    eps = 1e-8
    wd = config["weight_decay"]
    for key in ["w1", "w2", "b"]:
        state["m"][key] = beta1 * state["m"][key] + (1 - beta1) * grad[key]
        state["v"][key] = beta2 * state["v"][key] + (1 - beta2) * (grad[key] ** 2)
        m_hat = state["m"][key] / (1 - beta1 ** step)
        v_hat = state["v"][key] / (1 - beta2 ** step)
        params[key] -= lr * m_hat / (math.sqrt(v_hat) + eps)
        if key != "b" and wd:
            params[key] -= lr * wd * params[key]


def run_training(train_rows, valid_rows, run_config, epochs):
    params = {"w1": 0.0, "w2": 0.0, "b": 0.0}
    state = {"m": {"w1": 0.0, "w2": 0.0, "b": 0.0}, "v": {"w1": 0.0, "w2": 0.0, "b": 0.0}}
    history = []
    for epoch in range(1, epochs + 1):
        grad, train_loss = gradients(params, train_rows, run_config["loss"])
        if run_config["optimizer"] == "sgd":
            train_sgd(params, grad, run_config)
        elif run_config["optimizer"] == "adamw":
            train_adamw(params, grad, state, run_config, epoch)
        else:
            raise ValueError(f"optimizador no soportado: {run_config['optimizer']}")
        if epoch in {1, 5, 20, 60, epochs}:
            valid = metrics(params, valid_rows, run_config["loss"])
            history.append({"epoch": epoch, "train_loss": train_loss, "valid_loss": valid["loss"], "valid_f1": valid["f1"]})
    train = metrics(params, train_rows, run_config["loss"])
    valid = metrics(params, valid_rows, run_config["loss"])
    return params, train, valid, history


def evaluate_run(train_rows, valid_rows, run_config, policy):
    params, train, valid, history = run_training(train_rows, valid_rows, run_config, policy["epochs"])
    gap = train["f1"] - valid["f1"]
    warnings = []
    if gap > policy["validation_gap_warning"]:
        warnings.append("brecha train/validación alta")
    if run_config["loss"] == "mse":
        warnings.append("MSE no es la pérdida natural para clasificación binaria")
    return {
        "id": run_config["id"],
        "loss": run_config["loss"],
        "optimizer": run_config["optimizer"],
        "learning_rate": run_config["learning_rate"],
        "weight_decay": run_config["weight_decay"],
        "params": {k: round(v, 6) for k, v in params.items()},
        "train": {k: round(v, 6) if isinstance(v, float) else v for k, v in train.items()},
        "valid": {k: round(v, 6) if isinstance(v, float) else v for k, v in valid.items()},
        "f1_gap": round(gap, 6),
        "history": [{k: round(v, 6) if isinstance(v, float) else v for k, v in item.items()} for item in history],
        "warnings": warnings,
    }


def recommendation(row):
    if row["warnings"] and row["valid"]["f1"] < 0.8:
        return "descartar"
    if row["valid"]["f1"] >= 0.88 and not row["warnings"]:
        return "candidato principal"
    if row["valid"]["f1"] >= 0.85:
        return "candidato a revisar"
    return "baseline útil, pero mejorable"


def render_markdown(rows):
    ordered = sorted(rows, key=lambda item: item["valid"]["f1"], reverse=True)
    lines = [
        "# Decisión: pérdida y optimizador",
        "",
        "Todas las runs usan el mismo dataset sintético y la misma partición train/validación. La comparación mira pérdida, F1, accuracy y brecha de generalización.",
        "",
        "| Run | Pérdida | Optimizador | lr | weight decay | F1 valid | Accuracy valid | Gap F1 | Avisos | Decisión |",
        "|---|---|---|---:|---:|---:|---:|---:|---|---|",
    ]
    for row in ordered:
        warnings = "; ".join(row["warnings"]) if row["warnings"] else "ok"
        lines.append(
            f"| `{row['id']}` | {row['loss']} | {row['optimizer']} | {row['learning_rate']} | "
            f"{row['weight_decay']} | {row['valid']['f1']} | {row['valid']['accuracy']} | "
            f"{row['f1_gap']} | {warnings} | {recommendation(row)} |"
        )

    lines.extend(["", "## Curvas resumidas", ""])
    for row in ordered:
        lines.append(f"### {row['id']}")
        lines.append("")
        lines.append("| Época | Train loss | Valid loss | Valid F1 |")
        lines.append("|---:|---:|---:|---:|")
        for item in row["history"]:
            lines.append(f"| {item['epoch']} | {item['train_loss']} | {item['valid_loss']} | {item['valid_f1']} |")
        lines.append("")

    lines.extend(
        [
            "## Lectura técnica",
            "",
            "- BCE es la pérdida natural para clasificación binaria porque optimiza probabilidad logarítmica de la clase correcta.",
            "- MSE puede aprender algo, pero su gradiente no está tan alineado con clasificación probabilística.",
            "- No compares el valor absoluto de BCE y MSE como si fueran la misma escala; compara validación y comportamiento.",
            "- AdamW añade estado interno y weight decay desacoplado; por eso puede ser más estable que SGD con menos ajuste manual.",
            "- Una run no se elige solo por train loss: validación y F1 mandan.",
        ]
    )
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--fail-on-invalid", action="store_true")
    args = parser.parse_args()

    policy = load_json(ROOT / "contracts" / "training_grid.json")
    rows = make_dataset(policy["seed"], policy["examples"])
    train_rows, valid_rows = split_dataset(rows, policy["train_ratio"])
    results = [evaluate_run(train_rows, valid_rows, run_config, policy) for run_config in policy["runs"]]

    output_dir = ROOT / "output"
    if args.write:
        output_dir.mkdir(exist_ok=True)
        (output_dir / "training_report.json").write_text(
            json.dumps(results, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (output_dir / "training_decision.md").write_text(
            render_markdown(results) + "\n",
            encoding="utf-8",
        )

    invalid = [row for row in results if row["valid"]["f1"] < 0.65]
    print(f"runs: {len(results)}")
    print(f"valid_f1_bajo: {len(invalid)}")
    print(f"salida: {output_dir if args.write else 'no escrita'}")
    if args.fail_on_invalid and invalid:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
