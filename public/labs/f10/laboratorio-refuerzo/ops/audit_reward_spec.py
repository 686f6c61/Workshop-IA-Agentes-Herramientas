#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = ROOT / "data" / "reward_cases.json"
DEFAULT_CONTRACT = ROOT / "contracts" / "refuerzo_lab_contract.json"
DEFAULT_OUTPUT = ROOT / "output"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def score_candidate(candidate, terms):
    return (
        terms["correctness"] * candidate["correctness"]
        + terms["citation"] * candidate["citation"]
        + terms["abstention"] * candidate["abstention"]
        + terms["format"] * candidate["format"]
        + terms["cost_per_tool"] * candidate["tool_calls"]
        + terms["cost_per_100_tokens"] * (candidate["tokens"] / 100)
    )


def expected_ok(case, winner):
    if case["expected_behavior"] == "responder_con_cita":
        return winner["correctness"] == 1 and winner["citation"] == 1 and winner["abstention"] == 0
    if case["expected_behavior"] == "abstenerse":
        return winner["abstention"] == 1 and winner["correctness"] == 1
    if case["expected_behavior"] == "responder_estructurado":
        return winner["correctness"] == 1 and winner["citation"] == 1 and winner["format"] == 1
    return False


def audit(data, contract):
    rows = []
    for case in data["cases"]:
        scored = []
        for candidate in case["candidates"]:
            scored.append({
                **candidate,
                "score": round(score_candidate(candidate, data["reward_terms"]), 4)
            })
        ranked = sorted(scored, key=lambda row: row["score"], reverse=True)
        winner = ranked[0]
        rows.append({
            "case_id": case["case_id"],
            "expected_behavior": case["expected_behavior"],
            "winner": winner["candidate_id"],
            "winner_score": winner["score"],
            "winner_notes": winner["notes"],
            "case_ok": expected_ok(case, winner),
            "ranked_candidates": ranked
        })
    pass_rate = sum(row["case_ok"] for row in rows) / len(rows)
    required_terms = contract["reward_gate"]["required_terms"]
    missing_terms = [term for term in required_terms if term not in data["reward_terms"] and term != "cost"]
    if "cost" in required_terms and not any(key.startswith("cost_") for key in data["reward_terms"]):
        missing_terms.append("cost")
    length_bonus_present = any("length" in key or "tokens_bonus" in key for key in data["reward_terms"])
    gate_ok = (
        pass_rate >= contract["reward_gate"]["min_case_pass_rate"]
        and not missing_terms
        and not (contract["reward_gate"]["forbid_length_bonus"] and length_bonus_present)
    )
    return {
        "scenario_id": data["scenario_id"],
        "gate_ok": gate_ok,
        "pass_rate": round(pass_rate, 4),
        "missing_terms": missing_terms,
        "length_bonus_present": length_bonus_present,
        "reward_terms": data["reward_terms"],
        "cases": rows
    }


def render_reward_card(report):
    lines = [
        "# Reward card",
        "",
        f"Decision: `{'publicar_reward_spec' if report['gate_ok'] else 'revisar_reward_spec'}`.",
        "",
        "## Objetivo",
        "",
        "Premiar respuestas correctas, con evidencia, abstención cuando falta fuente, formato validable y coste controlado.",
        "",
        "## Términos de recompensa",
        "",
        "| Término | Peso | Lectura |",
        "|---|---:|---|",
    ]
    for term, value in report["reward_terms"].items():
        lines.append(f"| `{term}` | {value} | componente explícito de la recompensa |")
    lines.extend([
        "",
        "## Casos de auditoría",
        "",
        "| Caso | Ganador | Score | Estado |",
        "|---|---|---:|---|",
    ])
    for row in report["cases"]:
        lines.append(
            f"| `{row['case_id']}` | `{row['winner']}` | {row['winner_score']} | `{'pass' if row['case_ok'] else 'review'}` |"
        )
    lines.extend([
        "",
        "## Límites",
        "",
        "- No hay bonus por longitud.",
        "- Una respuesta correcta sin cita no gana cuando el caso requiere evidencia.",
        "- Una pregunta sin fuente debe abstenerse.",
        "- El coste se resta, pero nunca debe dominar exactitud y evidencia.",
        "",
        "## Repetición del gate",
        "",
        "Repetir el gate si cambian documentos, formato de salida, herramienta de recuperación, modelo base o pesos de recompensa.",
        "",
    ])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--fail-on-gate", action="store_true")
    args = parser.parse_args()

    report = audit(read_json(args.data), read_json(args.contract))
    ci_gate = {
        "decision": "publicar_reward_spec" if report["gate_ok"] else "revisar_reward_spec",
        "gate_ok": report["gate_ok"],
        "pass_rate": report["pass_rate"],
        "missing_terms": report["missing_terms"],
        "length_bonus_present": report["length_bonus_present"]
    }
    if args.write:
        write_json(args.output_dir / "reward_audit_report.json", report)
        write_json(args.output_dir / "ci_reward_gate.json", ci_gate)
        (args.output_dir / "reward_card.md").write_text(render_reward_card(report), encoding="utf-8")
    print(json.dumps(ci_gate, ensure_ascii=False, indent=2))
    if args.fail_on_gate and not report["gate_ok"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
