#!/usr/bin/env python3
import argparse
import json
from math import inf, log, sqrt
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def terminal(data, node):
    return node in data["utility"]


def minimax(data, node, stats):
    if terminal(data, node):
        stats["leaves"] += 1
        return data["utility"][node]
    player = data["nodes"][node]["player"]
    values = [minimax(data, child, stats) for child in data["nodes"][node]["children"]]
    return max(values) if player == "MAX" else min(values)


def alphabeta(data, node, alpha, beta, stats):
    if terminal(data, node):
        stats["leaves"] += 1
        return data["utility"][node]
    player = data["nodes"][node]["player"]
    children = data["nodes"][node]["children"]
    if player == "MAX":
        value = -inf
        for index, child in enumerate(children):
            value = max(value, alphabeta(data, child, alpha, beta, stats))
            alpha = max(alpha, value)
            if alpha >= beta:
                stats["prunes"] += len(children) - index - 1
                break
        return value
    value = inf
    for index, child in enumerate(children):
        value = min(value, alphabeta(data, child, alpha, beta, stats))
        beta = min(beta, value)
        if alpha >= beta:
            stats["prunes"] += len(children) - index - 1
            break
    return value


def choose_minimax(data):
    stats = {"leaves": 0}
    root = data["root"]
    scores = {child: minimax(data, child, stats) for child in data["nodes"][root]["children"]}
    return max(scores, key=scores.get), scores, stats


def choose_alphabeta(data):
    stats = {"leaves": 0, "prunes": 0}
    scores = {}
    alpha = -inf
    best = None
    for child in data["nodes"][data["root"]]["children"]:
        score = alphabeta(data, child, alpha, inf, stats)
        scores[child] = score
        if score > alpha:
            alpha = score
            best = child
    return best, scores, stats


def monte_carlo(data):
    return {
        action: {
            "mean": round(sum(samples) / len(samples), 4),
            "uncertainty": round(1 / sqrt(len(samples)), 4),
            "worst": min(samples),
            "best": max(samples)
        }
        for action, samples in data["rollouts"].items()
    }


def uct(data, c):
    visits = data["uct"]["visits"]
    values = data["uct"]["values"]
    total = sum(visits.values())
    scores = {
        action: values[action] + c * sqrt(log(total) / visits[action])
        for action in visits
    }
    return max(scores, key=scores.get), {key: round(value, 4) for key, value in scores.items()}


def build_report(data, policy):
    best_mm, scores_mm, stats_mm = choose_minimax(data)
    best_ab, scores_ab, stats_ab = choose_alphabeta(data)
    best_uct, uct_scores = uct(data, policy["uct_c"])
    return {
        "minimax": {"best": best_mm, "scores": scores_mm, "stats": stats_mm},
        "alphabeta": {"best": best_ab, "scores": scores_ab, "stats": stats_ab},
        "monte_carlo": monte_carlo(data),
        "uct": {"best": best_uct, "scores": uct_scores, "c": policy["uct_c"]}
    }


def write_markdown(report):
    lines = [
        "# Auditoría de juego",
        "",
        f"Minimax elige `{report['minimax']['best']}` con scores `{report['minimax']['scores']}`.",
        f"Alfa-beta elige `{report['alphabeta']['best']}` visitando `{report['alphabeta']['stats']['leaves']}` hojas y podando `{report['alphabeta']['stats']['prunes']}`.",
        f"UCT elige `{report['uct']['best']}` con c=`{report['uct']['c']}`.",
        "",
        "## Monte Carlo",
        "",
        "| Acción | Media | Peor caso | Mejor caso | Incertidumbre |",
        "|---|---:|---:|---:|---:|",
    ]
    for action, item in report["monte_carlo"].items():
        lines.append(f"| {action} | {item['mean']} | {item['worst']} | {item['best']} | {item['uncertainty']} |")
    lines.extend([
        "",
        "## Decisión",
        "",
        "Si el peor caso es inaceptable, la media no basta. Minimax sirve como prueba de tensión; Monte Carlo sirve para estimar comportamiento medio; UCT reparte presupuesto de simulación.",
    ])
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--fail-on-invalid", action="store_true")
    args = parser.parse_args()

    data = load_json("data/game_tree.json")
    policy = load_json("contracts/game_policy.json")
    report = build_report(data, policy)
    valid = True
    if policy["require_same_minimax_alphabeta"]:
        valid = valid and report["minimax"]["best"] == report["alphabeta"]["best"]
    valid = valid and report["alphabeta"]["stats"]["prunes"] >= policy["min_expected_prunes"]
    report["gate_valid"] = valid

    if args.write:
        (ROOT / "output").mkdir(exist_ok=True)
        (ROOT / "output/game_search_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        (ROOT / "output/game_search_decision.md").write_text(write_markdown(report), encoding="utf-8")

    print(json.dumps(report, indent=2, ensure_ascii=False))
    if args.fail_on_invalid and not valid:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

