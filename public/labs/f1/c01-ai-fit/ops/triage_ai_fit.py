#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def choose_recommendation(case, review_threshold):
    reasons = []
    components = []

    if case["needs_exact_number"] or case["known_database"]:
        components.append("sql_or_deterministic_code")
        reasons.append("hay que calcular o consultar un dato exacto")

    if case["docs_available"] or (case["requires_sources"] and not case["known_database"]):
        components.append("search_or_rag")
        reasons.append("la respuesta debe apoyarse en fuentes recuperables")

    if case["generation_needed"]:
        components.append("llm_generation")
        reasons.append("hay que redactar, resumir o transformar lenguaje")

    if case["external_action"] or case["needs_live_state"]:
        components.append("tool_or_api")
        reasons.append("hace falta leer estado real o actuar sobre un sistema")

    if case["impact"] >= review_threshold or case["external_action"]:
        components.append("human_review")
        reasons.append("el impacto o la acción externa exige una persona responsable")

    components = list(dict.fromkeys(components))

    if len(components) == 1:
        primary = components[0]
    elif len(components) == 0:
        primary = "human_review"
        components = ["human_review"]
        reasons.append("el caso no tiene señales suficientes para automatizar")
    else:
        primary = "hybrid_system"

    return primary, components, reasons


def controls_for(components, policy):
    controls = []
    for component in components:
        controls.extend(policy["controls"][component])
    return list(dict.fromkeys(controls))


def build_report(cases, policy):
    rows = []
    for case in cases:
        primary, components, reasons = choose_recommendation(
            case, policy["impact_review_threshold"]
        )
        controls = controls_for(components, policy)
        rows.append(
            {
                "id": case["id"],
                "title": case["title"],
                "recommendation": primary,
                "components": components,
                "needs_review": "human_review" in components,
                "controls": controls,
                "reasons": reasons,
            }
        )
    return rows


def render_markdown(rows):
    lines = [
        "# Decisión: ¿encaja aquí IA generativa?",
        "",
        "La regla del capítulo 01 es sencilla: un LLM genera lenguaje; no sustituye cálculo exacto, fuentes, permisos ni responsabilidad.",
        "",
        "| Caso | Recomendación | Componentes | Controles mínimos |",
        "|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            "| {title} | `{recommendation}` | {components} | {controls} |".format(
                title=row["title"],
                recommendation=row["recommendation"],
                components=", ".join(f"`{item}`" for item in row["components"]),
                controls=", ".join(f"`{item}`" for item in row["controls"]),
            )
        )

    lines.extend(["", "## Lectura técnica", ""])
    for row in rows:
        lines.append(f"### {row['title']}")
        lines.append("")
        lines.append("Por qué: " + "; ".join(row["reasons"]) + ".")
        if row["needs_review"]:
            lines.append("Decisión: no publiques automatización directa; exige revisión humana trazable.")
        else:
            lines.append("Decisión: se puede automatizar con los controles indicados y pruebas pequeñas.")
        lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--fail-on-review", action="store_true")
    args = parser.parse_args()

    cases = load_json(ROOT / "data" / "use_cases.json")
    policy = load_json(ROOT / "contracts" / "decision_policy.json")
    rows = build_report(cases, policy)

    output_dir = ROOT / "output"
    if args.write:
        output_dir.mkdir(exist_ok=True)
        (output_dir / "ai_fit_report.json").write_text(
            json.dumps(rows, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (output_dir / "ai_fit_decision.md").write_text(
            render_markdown(rows) + "\n",
            encoding="utf-8",
        )

    review_count = sum(1 for row in rows if row["needs_review"])
    print(f"casos: {len(rows)}")
    print(f"requieren_revision: {review_count}")
    print(f"salida: {output_dir if args.write else 'no escrita'}")

    if args.fail_on_review and review_count:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
