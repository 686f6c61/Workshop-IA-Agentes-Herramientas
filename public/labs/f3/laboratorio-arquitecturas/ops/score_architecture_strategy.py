#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASE = ROOT / "data" / "strategy_case.json"
DEFAULT_CONTRACT = ROOT / "contracts" / "arquitecturas_lab_contract.json"
DEFAULT_OUTPUT_DIR = ROOT / "output"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def score_option(option, weights):
    return round(sum(option["scores"][axis] * weight for axis, weight in weights.items()), 4)


def build_report(case, contract):
    rows = []
    for option in case["options"]:
        rows.append({
            "option_id": option["option_id"],
            "label": option["label"],
            "weighted_score": score_option(option, case["weights"]),
            "scores": option["scores"]
        })
    rows = sorted(rows, key=lambda row: row["weighted_score"], reverse=True)
    selected = rows[0]["option_id"]
    return {
        "case_id": case["case_id"],
        "status": "estrategia_defendible" if selected == contract["strategy_gate"]["expected_first_choice"] else "revisar_criterios",
        "selected_option": selected,
        "ranking": rows,
        "evaluation_axes": contract["strategy_gate"]["required_evaluation_axes"]
    }


def render_decision(report):
    lines = [
        "# Decisión de arquitectura",
        "",
        f"Decisión: `{report['selected_option']}`.",
        "",
        "## Scorecard",
        "",
        "| Opción | Puntuación ponderada |",
        "|---|---:|",
    ]
    for row in report["ranking"]:
        lines.append(f"| `{row['option_id']}` | {row['weighted_score']} |")
    lines.extend([
        "",
        "## Por qué",
        "",
        "La normativa cambia y las respuestas deben citar documentos. Por eso conviene separar conocimiento vivo y pesos del modelo: documentos en RAG, modelo para leer, sintetizar y responder con evidencia.",
        "",
        "Fine-tuning puede ayudar a formato o estilo, pero no es la primera herramienta para mantener conocimiento que cambia varias veces al año. El prompt largo sirve para prototipo, pero encarece contexto y mezcla demasiadas responsabilidades.",
        "",
        "## Evaluación mínima",
        "",
    ])
    for axis in report["evaluation_axes"]:
        lines.append(f"- `{axis}`")
    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", type=Path, default=DEFAULT_CASE)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--fail-on-review", action="store_true")
    args = parser.parse_args()

    report = build_report(read_json(args.case), read_json(args.contract))
    if args.write:
        write_json(args.output_dir / "strategy_scorecard.json", report)
        (args.output_dir / "strategy_decision.md").write_text(render_decision(report), encoding="utf-8")
    print(json.dumps({"status": report["status"], "selected_option": report["selected_option"]}, ensure_ascii=False, indent=2))
    if args.fail_on_review and report["status"] != "estrategia_defendible":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
