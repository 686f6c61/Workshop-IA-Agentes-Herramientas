#!/usr/bin/env python3
import argparse
import csv
import copy
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SPEC = ROOT / "data" / "reward_spec.json"
DEFAULT_CONTRACT = ROOT / "contracts" / "reward_card_contract.json"
DEFAULT_OUTPUT = ROOT / "output"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def score_candidate(candidate, terms):
    score = 0.0
    contributions = {}
    scores = candidate.get("scores", {})
    for term in terms:
        value = float(scores.get(term["name"], 0.0))
        contribution = float(term["weight"]) * value
        score += contribution
        contributions[term["name"]] = round(contribution, 6)
    return round(score, 6), contributions


def weight_share(terms, category):
    total = sum(abs(float(term["weight"])) for term in terms)
    if total == 0:
        return 0.0
    return sum(abs(float(term["weight"])) for term in terms if term["category"] == category) / total


def grader_confusion(spec):
    rows = spec.get("grader_evaluation", [])
    grouped = {}
    for row in rows:
        grader = row["grader"]
        grouped.setdefault(grader, {"tp": 0, "tn": 0, "fp": 0, "fn": 0})
        gold = bool(row["gold"])
        prediction = bool(row["prediction"])
        if gold and prediction:
            grouped[grader]["tp"] += 1
        elif not gold and not prediction:
            grouped[grader]["tn"] += 1
        elif not gold and prediction:
            grouped[grader]["fp"] += 1
        elif gold and not prediction:
            grouped[grader]["fn"] += 1

    matrix = []
    for grader, counts in sorted(grouped.items()):
        tp = counts["tp"]
        tn = counts["tn"]
        fp = counts["fp"]
        fn = counts["fn"]
        total = tp + tn + fp + fn
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        accuracy = (tp + tn) / total if total else 0.0
        matrix.append({
            "grader": grader,
            "tp": tp,
            "tn": tn,
            "fp": fp,
            "fn": fn,
            "precision": round(precision, 6),
            "recall": round(recall, 6),
            "accuracy": round(accuracy, 6),
        })
    return matrix


def aggregate_grader_metrics(matrix):
    if not matrix:
        return {"grader_accuracy": None, "grader_precision": None, "grader_recall": None}
    return {
        "grader_accuracy": round(sum(row["accuracy"] for row in matrix) / len(matrix), 6),
        "grader_precision": round(sum(row["precision"] for row in matrix) / len(matrix), 6),
        "grader_recall": round(sum(row["recall"] for row in matrix) / len(matrix), 6),
    }


def normalized_cost_terms(spec):
    cost_names = {
        term["name"]
        for term in spec.get("reward_terms", [])
        if term.get("category") == "cost"
    }
    return {
        row["term"]
        for row in spec.get("normalization", [])
        if row.get("term") in cost_names
    }


def hard_gate_summary(spec):
    required = [gate for gate in spec.get("hard_gates", []) if gate.get("required")]
    with_verifier = [
        gate for gate in required
        if gate.get("verifier") and gate.get("verifier") != "none"
    ]
    return {
        "required_hard_gates": required,
        "hard_gate_count": len(required),
        "hard_gates_with_verifier": len(with_verifier),
        "all_hard_gates_have_verifier": len(required) == len(with_verifier),
    }


def audit(spec, contract):
    terms = spec["reward_terms"]
    names = {term["name"] for term in terms}
    required_missing = [name for name in contract["required_terms"] if name not in names]
    proxy_share = weight_share(terms, "proxy")
    cost_share = weight_share(terms, "cost")
    positive_length_bonus = any("length" in term["name"] and float(term["weight"]) > 0 for term in terms)
    hidden_case_rate = sum(1 for case in spec["test_cases"] if case.get("hidden")) / len(spec["test_cases"])
    slice_count = len({case["slice"] for case in spec["test_cases"]})
    verifier_coverage = sum(1 for term in terms if term.get("verifier") and term["verifier"] != "none") / len(terms)

    case_rows = []
    for case in spec["test_cases"]:
        scored = []
        for candidate in case["candidates"]:
            score, contributions = score_candidate(candidate, terms)
            scored.append({
                "candidate_id": candidate["candidate_id"],
                "score": score,
                "contributions": contributions,
            })
        ranked = sorted(scored, key=lambda row: row["score"], reverse=True)
        winner = ranked[0]
        case_rows.append({
            "case_id": case["case_id"],
            "slice": case["slice"],
            "hidden": bool(case.get("hidden")),
            "expected_winner": case["expected_winner"],
            "winner": winner["candidate_id"],
            "winner_score": winner["score"],
            "case_ok": winner["candidate_id"] == case["expected_winner"],
            "ranked_candidates": ranked,
        })

    pass_rate = sum(1 for row in case_rows if row["case_ok"]) / len(case_rows)
    confusion = grader_confusion(spec)
    grader_metrics = aggregate_grader_metrics(confusion)
    normalized_cost = normalized_cost_terms(spec)
    gates = hard_gate_summary(spec)
    checks = {
        "min_cases": len(case_rows) >= contract["min_cases"],
        "min_slice_count": slice_count >= contract["min_slice_count"],
        "min_case_pass_rate": pass_rate >= contract["min_case_pass_rate"],
        "min_hidden_case_rate": hidden_case_rate >= contract["min_hidden_case_rate"],
        "min_hard_gates": gates["hard_gate_count"] >= contract.get("min_hard_gates", 0),
        "hard_gates_have_verifier": gates["all_hard_gates_have_verifier"],
        "min_normalized_cost_terms": len(normalized_cost) >= contract.get("min_normalized_cost_terms", 0),
        "max_proxy_weight_share": proxy_share <= contract["max_proxy_weight_share"],
        "max_cost_weight_share": cost_share <= contract["max_cost_weight_share"],
        "forbid_positive_length_bonus": not (contract["forbid_positive_length_bonus"] and positive_length_bonus),
        "required_terms_present": not required_missing,
    }
    status = "pass" if all(checks.values()) else "block"
    return {
        "scenario_id": spec["scenario_id"],
        "reward_card_version": spec["reward_card_version"],
        "objective": spec["objective"],
        "contract_version": contract["contract_version"],
        "status": status,
        "diagnostics": {
            "cases": len(case_rows),
            "slice_count": slice_count,
            "case_pass_rate": round(pass_rate, 6),
            "hidden_case_rate": round(hidden_case_rate, 6),
            "proxy_weight_share": round(proxy_share, 6),
            "cost_weight_share": round(cost_share, 6),
            "verifier_coverage": round(verifier_coverage, 6),
            "positive_length_bonus": positive_length_bonus,
            "required_missing": required_missing,
            "hard_gate_count": gates["hard_gate_count"],
            "hard_gates_with_verifier": gates["hard_gates_with_verifier"],
            "normalized_cost_terms": len(normalized_cost),
            **grader_metrics,
        },
        "checks": checks,
        "reward_terms": terms,
        "normalization": spec.get("normalization", []),
        "hard_gates": gates["required_hard_gates"],
        "cases": case_rows,
        "grader_confusion_matrix": confusion,
    }


def build_sensitivity_rows(spec, contract):
    base_report = audit(spec, contract)
    base_winners = {row["case_id"]: row["winner"] for row in base_report["cases"]}
    rows = []
    multipliers = [0.5, 0.75, 1.0, 1.25, 1.5]
    for term in spec["reward_terms"]:
        term_name = term["name"]
        for multiplier in multipliers:
            candidate_spec = copy.deepcopy(spec)
            for candidate_term in candidate_spec["reward_terms"]:
                if candidate_term["name"] == term_name:
                    candidate_term["weight"] = round(float(candidate_term["weight"]) * multiplier, 6)
            report = audit(candidate_spec, contract)
            changed_cases = [
                case["case_id"] for case in report["cases"]
                if case["winner"] != base_winners[case["case_id"]]
            ]
            rows.append({
                "term": term_name,
                "multiplier": multiplier,
                "case_pass_rate": report["diagnostics"]["case_pass_rate"],
                "winner_changes": len(changed_cases),
                "changed_cases": ";".join(changed_cases),
                "proxy_weight_share": report["diagnostics"]["proxy_weight_share"],
                "cost_weight_share": report["diagnostics"]["cost_weight_share"],
                "status": report["status"],
            })
    return rows


def render_decision(report):
    lines = [
        "# Decisión de reward card",
        "",
        f"Estado: `{report['status']}`",
        f"Escenario: `{report['scenario_id']}`",
        "",
        "| Diagnóstico | Valor |",
        "|---|---:|",
    ]
    for key, value in report["diagnostics"].items():
        lines.append(f"| `{key}` | {value} |")
    lines.extend(["", "| Check | Pasa |", "|---|---|"])
    for key, value in report["checks"].items():
        lines.append(f"| `{key}` | {'sí' if value else 'no'} |")
    lines.extend(["", "## Lectura", ""])
    if report["status"] == "pass":
        lines.append("La reward card puede pasar a experimento controlado. Aun así, debe versionarse junto al dataset, los verificadores y la evaluación retenida.")
    else:
        lines.append("La reward card debe bloquearse. Revisa términos ausentes, exceso de proxy, bonus por longitud, pocos casos ocultos o casos donde gana el candidato incorrecto.")
    return "\n".join(lines) + "\n"


def render_reward_card(report):
    lines = [
        "# Reward card",
        "",
        f"Escenario: `{report['scenario_id']}`",
        f"Version: `{report['reward_card_version']}`",
        f"Estado: `{report['status']}`",
        "",
        "## Objetivo",
        "",
        report["objective"],
        "",
        "## Terminos",
        "",
        "| Termino | Peso | Categoria | Verificador |",
        "|---|---:|---|---|",
    ]
    for term in report["reward_terms"]:
        lines.append(f"| `{term['name']}` | {term['weight']} | `{term['category']}` | `{term.get('verifier', 'none')}` |")
    lines.extend(["", "## Normalizacion", "", "| Termino | Metodo | Fuente |", "|---|---|---|"])
    for row in report["normalization"]:
        lines.append(f"| `{row['term']}` | `{row['method']}` | `{row['source']}` |")
    lines.extend(["", "## Restricciones duras", "", "| Restriccion | Verificador | Motivo |", "|---|---|---|"])
    for gate in report["hard_gates"]:
        lines.append(f"| `{gate['name']}` | `{gate.get('verifier', 'none')}` | {gate.get('reason', '')} |")
    lines.extend(["", "## Casos", "", "| Caso | Slice | Ganador | Esperado | Estado |", "|---|---|---|---|---|"])
    for case in report["cases"]:
        lines.append(f"| `{case['case_id']}` | `{case['slice']}` | `{case['winner']}` | `{case['expected_winner']}` | `{'pass' if case['case_ok'] else 'review'}` |")
    lines.extend([
        "",
        "## Limites",
        "",
        "- La recompensa es una aproximacion, no una prueba de verdad.",
        "- Los pesos deben revisarse si cambia el producto, el RAG, el modelo base o el contrato de salida.",
        "- Los casos ocultos deben rotar para evitar que la reward card solo mida fixtures conocidos.",
    ])
    return "\n".join(lines) + "\n"


def write_outputs(output_dir, report):
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "reward_card_audit_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output_dir / "reward_card_decision.md").write_text(render_decision(report), encoding="utf-8")
    (output_dir / "reward_card.md").write_text(render_reward_card(report), encoding="utf-8")
    with (output_dir / "component_scorecard.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["name", "weight", "category", "verifier"])
        writer.writeheader()
        writer.writerows(report["reward_terms"])
    with (output_dir / "case_scorecard.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["case_id", "slice", "hidden", "expected_winner", "winner", "winner_score", "case_ok"])
        writer.writeheader()
        for case in report["cases"]:
            writer.writerow({key: case[key] for key in ["case_id", "slice", "hidden", "expected_winner", "winner", "winner_score", "case_ok"]})
    with (output_dir / "grader_confusion_matrix.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["grader", "tp", "tn", "fp", "fn", "precision", "recall", "accuracy"])
        writer.writeheader()
        writer.writerows(report["grader_confusion_matrix"])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", default=str(DEFAULT_SPEC))
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    spec = read_json(Path(args.spec))
    contract = read_json(Path(args.contract))
    report = audit(spec, contract)
    if args.write:
        write_outputs(Path(args.output), report)
        sensitivity_rows = build_sensitivity_rows(spec, contract)
        with (Path(args.output) / "sensitivity_report.csv").open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(sensitivity_rows[0].keys()))
            writer.writeheader()
            writer.writerows(sensitivity_rows)
    print(f"status={report['status']}")
    print(f"cases={report['diagnostics']['cases']}")
    print(f"case_pass_rate={report['diagnostics']['case_pass_rate']}")
    print(f"proxy_weight_share={report['diagnostics']['proxy_weight_share']}")


if __name__ == "__main__":
    main()
