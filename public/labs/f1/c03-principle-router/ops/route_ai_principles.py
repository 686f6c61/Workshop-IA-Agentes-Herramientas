#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def route_case(case, policy):
    scores = {
        "supervised_learning": 0,
        "unsupervised_learning": 0,
        "post_training": 0,
        "attention_context": 0,
        "scaling_cost": 0,
    }
    reasons = []
    flags = []

    if case["labeled_examples"] >= policy["min_labeled_examples_for_supervised"]:
        scores["supervised_learning"] += 3
        reasons.append("hay suficientes ejemplos etiquetados para medir error")
    elif case["labeled_examples"] > 0:
        scores["supervised_learning"] += 1
        flags.append("pocos ejemplos etiquetados: valida antes de prometer fine-tuning")

    if case["unlabeled_pool"] > case["labeled_examples"] * 5:
        scores["unsupervised_learning"] += 2
        reasons.append("hay mucho dato sin etiquetar para explorar estructura")

    if case["needs_preference_alignment"]:
        scores["post_training"] += 4
        reasons.append("el comportamiento deseado depende de preferencias y abstención")
    elif case["needs_generation"]:
        scores["post_training"] += 1

    if case["context_tokens"] >= policy["high_context_tokens"]:
        scores["attention_context"] += 4
        reasons.append("el presupuesto de contexto condiciona coste y recuperación")
    elif case["context_tokens"] > 3000:
        scores["attention_context"] += 1

    if case["latency_ms"] <= policy["latency_sensitive_ms"] and case["needs_generation"]:
        scores["scaling_cost"] += 4
        reasons.append("la generación tiene objetivo estricto de latencia")
    elif case["latency_ms"] <= policy["latency_sensitive_ms"] or case["needs_generation"]:
        scores["scaling_cost"] += 2
        reasons.append("hay que comparar calidad, latencia y coste")

    if case["impact"] >= policy["high_impact_threshold"]:
        flags.append("impacto alto: exige evaluación y revisión antes de publicar")

    primary = max(scores, key=scores.get)
    supporting = [
        principle for principle, score in scores.items()
        if principle != primary and score > 0
    ]
    artifacts = [policy["principles"][primary]["artifact"]]
    artifacts += [policy["principles"][principle]["artifact"] for principle in supporting]

    return {
        "id": case["id"],
        "title": case["title"],
        "primary_principle": primary,
        "supporting_principles": supporting,
        "required_artifacts": list(dict.fromkeys(artifacts)),
        "review_flags": flags,
        "reasons": reasons,
        "next_chapter": policy["principles"][primary]["next_chapter"],
    }


def render_markdown(rows):
    lines = [
        "# Decisión: ¿qué principio de IA domina el caso?",
        "",
        "El objetivo no es encasillar el proyecto en una palabra. El objetivo es detectar qué pieza manda la decisión técnica y qué artefactos hacen falta antes de construir.",
        "",
        "| Caso | Principio dominante | Principios secundarios | Artefactos mínimos | Revisión |",
        "|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            "| {title} | `{primary}` | {supporting} | {artifacts} | {review} |".format(
                title=row["title"],
                primary=row["primary_principle"],
                supporting=", ".join(f"`{item}`" for item in row["supporting_principles"]) or "-",
                artifacts=", ".join(row["required_artifacts"]),
                review="; ".join(row["review_flags"]) or "sin bloqueo inicial",
            )
        )

    lines.extend(["", "## Lectura técnica", ""])
    for row in rows:
        lines.append(f"### {row['title']}")
        lines.append("")
        lines.append(f"Principio dominante: `{row['primary_principle']}`.")
        lines.append("Por qué: " + ("; ".join(row["reasons"]) or "faltan señales fuertes; pide más contexto") + ".")
        lines.append("Siguiente lugar del facsímil: " + row["next_chapter"] + ".")
        if row["review_flags"]:
            lines.append("Cuidado: " + "; ".join(row["review_flags"]) + ".")
        lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--fail-on-review", action="store_true")
    args = parser.parse_args()

    policy = load_json(ROOT / "contracts" / "principle_policy.json")
    cases = load_json(ROOT / "data" / "project_cases.json")
    rows = [route_case(case, policy) for case in cases]

    output_dir = ROOT / "output"
    if args.write:
        output_dir.mkdir(exist_ok=True)
        (output_dir / "principle_report.json").write_text(
            json.dumps(rows, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (output_dir / "principle_decision.md").write_text(
            render_markdown(rows) + "\n",
            encoding="utf-8",
        )

    review_count = sum(1 for row in rows if row["review_flags"])
    print(f"casos: {len(rows)}")
    print(f"requieren_revision: {review_count}")
    print(f"salida: {output_dir if args.write else 'no escrita'}")

    if args.fail_on_review and review_count:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
