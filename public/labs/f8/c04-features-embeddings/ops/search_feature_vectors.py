#!/usr/bin/env python3
import argparse
import csv
import json
import math
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASES = ROOT / "data" / "feature_cases.csv"
DEFAULT_QUERIES = ROOT / "data" / "search_queries.csv"
DEFAULT_CONTRACT = ROOT / "contracts" / "feature_contract.json"
DEFAULT_MANIFEST = ROOT / "output" / "feature_manifest.json"
DEFAULT_EMBEDDINGS = ROOT / "output" / "dense_embedding_matrix.csv"
DEFAULT_OUTPUT = ROOT / "output"

STOPWORDS = {
    "con",
    "del",
    "desde",
    "para",
    "por",
    "sin",
    "sobre",
    "una",
    "uno",
    "y",
}


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def read_json(path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_csv(path, fieldnames, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def normalize_text(value):
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9áéíóúñü]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def tokens(value, min_length=3):
    return [
        token
        for token in normalize_text(value).split()
        if len(token) >= min_length and token not in STOPWORDS
    ]


def term_hash(term, dimensions):
    import hashlib

    digest = hashlib.sha256(term.encode("utf-8")).digest()
    index = int.from_bytes(digest[:4], "big") % dimensions
    sign = 1 if digest[4] % 2 == 0 else -1
    return index, sign


def l2_normalize(values):
    norm = math.sqrt(sum(value * value for value in values))
    if norm == 0:
        return values
    return [value / norm for value in values]


def dense_query_embedding(text, manifest, contract):
    dimensions = contract["dense_embedding"]["dimensions"]
    idf = manifest["metadata"]["idf"]
    query_tokens = tokens(text, contract["text_feature"]["min_token_length"])
    vector = [0.0] * dimensions
    counts = Counter(query_tokens)
    for term, count in counts.items():
        index, sign = term_hash(term, dimensions)
        vector[index] += sign * count * idf.get(term, 1.0)
    return l2_normalize(vector), sorted(set(query_tokens) - set(manifest["metadata"]["text_vocabulary"]))


def cosine(left, right):
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return sum(a * b for a, b in zip(left, right)) / (left_norm * right_norm)


def case_lookup(rows):
    return {row["case_id"]: row for row in rows}


def embedding_rows(rows):
    result = []
    for row in rows:
        vector = [
            float(value)
            for key, value in sorted(row.items())
            if key.startswith("embedding_")
        ]
        result.append({**row, "vector": vector})
    return result


def build_search(cases, queries, embeddings, manifest, contract):
    cases_by_id = case_lookup(cases)
    index_splits = set(contract["similarity"]["index_splits"])
    top_k = contract["similarity"]["top_k"]
    index_rows = [
        row
        for row in embedding_rows(embeddings)
        if row["split"] in index_splits
    ]

    result_rows = []
    report_queries = []
    for query in queries:
        query_vector, out_of_vocab = dense_query_embedding(query["text"], manifest, contract)
        scored = []
        for item in index_rows:
            case = cases_by_id[item["case_id"]]
            scored.append(
                {
                    "case_id": item["case_id"],
                    "split": item["split"],
                    "product": case["product"],
                    "label": case["label"],
                    "text": case["text"],
                    "score": cosine(query_vector, item["vector"]),
                }
            )
        scored = sorted(scored, key=lambda item: (-item["score"], item["case_id"]))[:top_k]
        expected_product_found = any(item["product"] == query["expected_product"] for item in scored)
        for rank, item in enumerate(scored, start=1):
            result_rows.append(
                {
                    "query_id": query["query_id"],
                    "rank": rank,
                    "score": round(item["score"], 6),
                    "case_id": item["case_id"],
                    "split": item["split"],
                    "product": item["product"],
                    "label": item["label"],
                    "text": item["text"],
                }
            )
        report_queries.append(
            {
                "query_id": query["query_id"],
                "text": query["text"],
                "expected_product": query["expected_product"],
                "out_of_vocabulary_terms": out_of_vocab,
                "expected_product_in_top_k": expected_product_found,
                "top_case_ids": [item["case_id"] for item in scored],
            }
        )

    return {
        "contract_id": contract["contract_id"],
        "encoder": contract["dense_embedding"]["method"],
        "dimensions": contract["dense_embedding"]["dimensions"],
        "similarity": contract["similarity"]["metric"],
        "index_splits": sorted(index_splits),
        "top_k": top_k,
        "query_count": len(queries),
        "queries": report_queries,
        "gate": "review" if any(query["out_of_vocabulary_terms"] for query in report_queries) else "pass",
    }, result_rows


def write_decision(path, report):
    lines = [
        "# Decisión de búsqueda vectorial",
        "",
        f"Encoder local: `{report['encoder']}`.",
        f"Dimensiones: `{report['dimensions']}`.",
        f"Indice usado: `{', '.join(report['index_splits'])}`.",
        f"Gate: `{report['gate']}`.",
        "",
        "## Lectura",
        "",
        "La búsqueda usa un embedding denso local y similitud coseno. Es suficiente para probar contrato, top-k, metadata y errores de cobertura antes de sustituir el encoder por un modelo neural.",
        "",
        "## Consultas",
        "",
        "| Query | Producto esperado en top-k | Términos fuera de vocabulario | Vecinos |",
        "|---|---|---|---|",
    ]
    for query in report["queries"]:
        terms = ", ".join(f"`{term}`" for term in query["out_of_vocabulary_terms"]) or "ninguno"
        neighbors = ", ".join(f"`{case_id}`" for case_id in query["top_case_ids"])
        lines.append(
            f"| `{query['query_id']}` | {query['expected_product_in_top_k']} | {terms} | {neighbors} |"
        )
    lines.extend(
        [
            "",
            "## Siguiente mejora",
            "",
            "Sustituye el encoder local por embeddings reales, conserva `case_id`, `split`, dimension, versión del modelo, normalizacion y metadata. Despues evalúa recall@k por producto y por canal.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    parser.add_argument("--queries", type=Path, default=DEFAULT_QUERIES)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--embeddings", type=Path, default=DEFAULT_EMBEDDINGS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    cases = read_csv(args.cases)
    queries = read_csv(args.queries)
    contract = read_json(args.contract)
    manifest = read_json(args.manifest)
    embeddings = read_csv(args.embeddings)
    report, rows = build_search(cases, queries, embeddings, manifest, contract)

    if args.write:
        write_json(args.output_dir / "search_report.json", report)
        write_csv(args.output_dir / "search_results.csv", list(rows[0].keys()), rows)
        write_decision(args.output_dir / "search_decision.md", report)

    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
