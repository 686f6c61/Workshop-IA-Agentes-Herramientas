#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def query(triples, subject=None, predicate=None, obj=None):
    return sorted(
        [triple for triple in triples
         if (subject is None or triple[0] == subject)
         and (predicate is None or triple[1] == predicate)
         and (obj is None or triple[2] == obj)]
    )


def infer_subclasses(base_triples):
    triples = {tuple(triple) for triple in base_triples}
    changed = True
    inferred = set()

    while changed:
        changed = False
        types = [(s, o) for s, p, o in triples if p == "rdf:type"]
        parents = [(s, o) for s, p, o in triples if p == "rdfs:subClassOf"]
        for entity, cls in types:
            for child, parent in parents:
                candidate = (entity, "rdf:type", parent)
                if cls == child and candidate not in triples:
                    triples.add(candidate)
                    inferred.add(candidate)
                    changed = True

    return sorted([list(item) for item in inferred])


def build_report(base_triples, policy):
    inferred = infer_subclasses(base_triples)
    all_triples = base_triples + inferred
    queries = {
        "tipos_factura": [triple[2] for triple in query(all_triples, "factura:f9", "rdf:type")],
        "facturas_cliente": [triple[0] for triple in query(all_triples, predicate="perteneceA", obj="cliente:c42")],
        "dependencias_db": [triple[0] for triple in query(all_triples, predicate="dependeDe", obj="servicio:db")],
        "plan_cliente": [triple[2] for triple in query(all_triples, "cliente:c42", "tienePlan")]
    }
    required_inferred = [list(item) for item in policy["required_inferred_triples"]]
    valid = all(item in inferred for item in required_inferred)
    valid = valid and all(name in queries and queries[name] for name in policy["required_queries"])
    return {
        "base_triples": base_triples,
        "inferred_triples": inferred,
        "all_triples_count": len(all_triples),
        "queries": queries,
        "gate_valid": valid
    }


def write_markdown(report):
    lines = [
        "# Micrografo simbólico",
        "",
        f"Tripletas base: `{len(report['base_triples'])}`.",
        f"Tripletas inferidas: `{len(report['inferred_triples'])}`.",
        "",
        "## Consultas",
        "",
        "| Consulta | Resultado |",
        "|---|---|",
    ]
    for name, values in report["queries"].items():
        lines.append(f"| `{name}` | `{values}` |")
    lines.extend([
        "",
        "## Inferencias",
        "",
    ])
    for triple in report["inferred_triples"]:
        lines.append(f"- `{triple}`")
    lines.extend([
        "",
        "## Decisión",
        "",
        "El grafo sirve cuando necesitas relaciones verificables. Un vector store puede recuperar texto parecido; el grafo puede decir qué relación sostiene una decisión.",
    ])
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--fail-on-invalid", action="store_true")
    args = parser.parse_args()

    triples = load_json("data/triples.json")
    policy = load_json("contracts/graph_policy.json")
    report = build_report(triples, policy)

    if args.write:
        (ROOT / "output").mkdir(exist_ok=True)
        (ROOT / "output/symbolic_graph_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        (ROOT / "output/symbolic_graph_decision.md").write_text(write_markdown(report), encoding="utf-8")

    print(json.dumps(report, indent=2, ensure_ascii=False))
    if args.fail_on_invalid and not report["gate_valid"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

