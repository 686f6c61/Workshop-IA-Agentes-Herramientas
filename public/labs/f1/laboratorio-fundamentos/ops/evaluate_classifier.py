#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASES = ROOT / "data" / "classifier_cases.json"
DEFAULT_CONTRACT = ROOT / "contracts" / "fundamentos_lab_contract.json"
DEFAULT_OUTPUT_DIR = ROOT / "output"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def safe_divide(numerator, denominator):
    return numerator / denominator if denominator else 0.0


def metrics_for(model):
    tp = model["tp"]
    fp = model["fp"]
    fn = model["fn"]
    tn = model["tn"]
    precision = safe_divide(tp, tp + fp)
    recall = safe_divide(tp, tp + fn)
    f1 = safe_divide(2 * precision * recall, precision + recall)
    return {
        "model_id": model["model_id"],
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "priority_queue": tp + fp,
        "total_cases": tp + fp + fn + tn
    }


def decide(rows, contract):
    gate = contract["classifier_gate"]
    capacity = contract["priority_review_capacity"]
    feasible = [
        row for row in rows
        if row["f1"] >= gate["min_f1"] and row["priority_queue"] <= capacity
    ]
    if feasible:
        selected = max(feasible, key=lambda row: (row["f1"], row["precision"], row["recall"]))
        status = "publicar_piloto"
    else:
        selected = max(rows, key=lambda row: row["f1"])
        status = "revisar_umbral"
    return {
        "status": status,
        "selected_model": selected["model_id"],
        "capacity": capacity,
        "reason": (
            "Se elige el modelo que supera el F1 mínimo y cabe en la cola diaria."
            if feasible
            else "Ningún modelo cumple todo el gate; hace falta ajustar umbral o capacidad."
        )
    }


def render_decision(report):
    selected = report["decision"]["selected_model"]
    rows = {row["model_id"]: row for row in report["models"]}
    selected_row = rows[selected]
    lines = [
        "# Decisión de clasificador",
        "",
        f"Decisión: `{report['decision']['status']}`.",
        f"Modelo elegido: `{selected}`.",
        "",
        "## Motivo",
        "",
        (
            f"`{selected}` alcanza F1 `{selected_row['f1']}` y manda "
            f"`{selected_row['priority_queue']}` tickets a revisión prioritaria, "
            f"por debajo de la capacidad diaria de `{report['decision']['capacity']}`."
        ),
        "",
        "| Modelo | Precisión | Recall | F1 | Cola prioritaria |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in report["models"]:
        lines.append(
            f"| `{row['model_id']}` | {row['precision']} | {row['recall']} | {row['f1']} | {row['priority_queue']} |"
        )
    lines.extend([
        "",
        "## Lectura para una persona no técnica",
        "",
        "El primer modelo encuentra más casos importantes, pero genera una cola demasiado grande. El segundo manda menos ruido y cabe en la capacidad diaria del equipo.",
        "",
    ])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--fail-on-review", action="store_true")
    args = parser.parse_args()

    cases = read_json(args.cases)
    contract = read_json(args.contract)
    rows = [metrics_for(model) for model in cases["models"]]
    report = {
        "lab_id": contract["lab_id"],
        "positive_class": cases["positive_class"],
        "models": rows,
        "decision": decide(rows, contract)
    }

    if args.write:
        write_json(args.output_dir / "classifier_metrics.json", report)
        (args.output_dir / "classifier_decision.md").write_text(render_decision(report), encoding="utf-8")

    print(json.dumps(report["decision"], ensure_ascii=False, indent=2))
    if args.fail_on_review and report["decision"]["status"] != "publicar_piloto":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
