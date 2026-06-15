#!/usr/bin/env python3
import argparse
import json
import math
import re
import unicodedata
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = ROOT / "data" / "semantic_documents.json"
DEFAULT_CONTRACT = ROOT / "contracts" / "fundamentos_lab_contract.json"
DEFAULT_OUTPUT_DIR = ROOT / "output"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def normalize(text):
    text = unicodedata.normalize("NFD", text.lower())
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    return re.findall(r"[a-z0-9]+", text)


def average_vector(text, word_vectors, dimensions):
    vectors = [word_vectors[token] for token in normalize(text) if token in word_vectors]
    if not vectors:
        return [0.0 for _ in dimensions]
    return [sum(values) / len(values) for values in zip(*vectors)]


def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0


def reciprocal_rank(expected_doc, ranked_docs):
    if expected_doc not in ranked_docs:
        return 0.0
    return 1.0 / (ranked_docs.index(expected_doc) + 1)


def run_case(case, documents, data):
    dimensions = data["dimensions"]
    word_vectors = data["word_vectors"]
    query_vector = average_vector(case["query"], word_vectors, dimensions)
    scored = []
    for document in documents:
        doc_vector = average_vector(document["title"], word_vectors, dimensions)
        scored.append({
            "doc_id": document["doc_id"],
            "title": document["title"],
            "score": round(cosine(query_vector, doc_vector), 4)
        })
    ranked = sorted(scored, key=lambda row: row["score"], reverse=True)
    trace = {
        "trace_id": str(uuid.uuid4()),
        "case_id": case["case_id"],
        "spans": [
            {"name": "tokenize_query", "tokens": normalize(case["query"])},
            {"name": "embed_query", "vector": [round(x, 4) for x in query_vector]},
            {"name": "score_documents", "candidate_count": len(documents)},
            {"name": "rank", "top_docs": [row["doc_id"] for row in ranked[:3]]}
        ]
    }
    return {
        "case_id": case["case_id"],
        "query": case["query"],
        "expected_doc": case["expected_doc"],
        "ranked_docs": ranked[:3],
        "reciprocal_rank": round(reciprocal_rank(case["expected_doc"], [row["doc_id"] for row in ranked]), 4),
        "trace": trace
    }


def evaluate(results):
    hit_at_1 = sum(result["ranked_docs"][0]["doc_id"] == result["expected_doc"] for result in results) / len(results)
    mrr = sum(result["reciprocal_rank"] for result in results) / len(results)
    trace_complete_rate = sum(len(result["trace"]["spans"]) >= 4 for result in results) / len(results)
    return {
        "hit_at_1": round(hit_at_1, 4),
        "mrr": round(mrr, 4),
        "trace_complete_rate": round(trace_complete_rate, 4)
    }


def render_decision(report):
    lines = [
        "# Decisión de mini buscador semántico",
        "",
        f"Decisión: `{report['status']}`.",
        "",
        "## Métricas",
        "",
        f"- Hit@1: `{report['metrics']['hit_at_1']}`.",
        f"- MRR: `{report['metrics']['mrr']}`.",
        f"- Cobertura de trazas: `{report['metrics']['trace_complete_rate']}`.",
        "",
        "## Resultados por consulta",
        "",
        "| Caso | Consulta | Esperado | Primer resultado |",
        "|---|---|---|---|",
    ]
    for result in report["results"]:
        top = result["ranked_docs"][0]
        lines.append(
            f"| `{result['case_id']}` | {result['query']} | `{result['expected_doc']}` | `{top['doc_id']}` · {top['score']} |"
        )
    lines.extend([
        "",
        "## Lectura",
        "",
        "El buscador funciona en esta maqueta porque los vectores separan acceso y facturas. En un sistema real habría que ampliar casos, medir errores por categoría y versionar el vocabulario o el modelo de embeddings.",
        "",
    ])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--fail-on-review", action="store_true")
    args = parser.parse_args()

    data = read_json(args.data)
    contract = read_json(args.contract)
    results = [run_case(case, data["documents"], data) for case in data["queries"]]
    metrics = evaluate(results)
    gate = contract["semantic_search_gate"]
    status = (
        "publicar_piloto"
        if metrics["hit_at_1"] >= gate["min_hit_at_1"]
        and metrics["mrr"] >= gate["min_mrr"]
        and metrics["trace_complete_rate"] >= gate["min_trace_complete_rate"]
        else "ampliar_dataset"
    )
    report = {"lab_id": contract["lab_id"], "status": status, "metrics": metrics, "results": results}

    if args.write:
        write_json(args.output_dir / "semantic_search_report.json", report)
        trace_lines = [json.dumps(result["trace"], ensure_ascii=False) for result in results]
        (args.output_dir / "semantic_search_traces.jsonl").write_text("\n".join(trace_lines) + "\n", encoding="utf-8")
        (args.output_dir / "semantic_search_decision.md").write_text(render_decision(report), encoding="utf-8")

    print(json.dumps({"status": status, "metrics": metrics}, ensure_ascii=False, indent=2))
    if args.fail_on_review and status != "publicar_piloto":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
