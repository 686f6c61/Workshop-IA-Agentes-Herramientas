#!/usr/bin/env python3
import argparse
import csv
import hashlib
import json
import math
import re
from collections import Counter
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET = ROOT / "data" / "feature_cases.csv"
DEFAULT_SPLITS = ROOT / "data" / "split_assignments.csv"
DEFAULT_CONTRACT = ROOT / "contracts" / "feature_contract.json"
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


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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


def parse_day(value):
    return date.fromisoformat(value)


def split_lookup(rows):
    return {row["case_id"]: row["split"] for row in rows}


def attach_splits(rows, assignments):
    result = []
    for row in rows:
        if row["case_id"] not in assignments:
            raise ValueError(f"missing split for {row['case_id']}")
        result.append({**row, "split": assignments[row["case_id"]]})
    return result


def fit_metadata(rows, contract):
    train_rows = [row for row in rows if row["split"] == "train"]
    min_train_date = min(parse_day(row["created_at"]) for row in train_rows)
    max_train_days = max((parse_day(row["created_at"]) - min_train_date).days for row in train_rows) or 1
    max_train_tokens = max(len(tokens(row["text"], contract["text_feature"]["min_token_length"])) for row in train_rows) or 1

    product_vocab = sorted({row["product"] for row in train_rows})
    channel_vocab = sorted({row["channel"] for row in train_rows})

    document_frequency = Counter()
    term_counts = Counter()
    for row in train_rows:
        row_tokens = tokens(row["text"], contract["text_feature"]["min_token_length"])
        term_counts.update(row_tokens)
        document_frequency.update(set(row_tokens))

    selected_terms = [
        term
        for term, _ in sorted(term_counts.items(), key=lambda item: (-item[1], item[0]))[: contract["text_feature"]["max_terms"]]
    ]
    train_count = len(train_rows)
    idf = {
        term: math.log((1 + train_count) / (1 + document_frequency[term])) + 1
        for term in selected_terms
    }

    return {
        "min_train_date": min_train_date.isoformat(),
        "max_train_days": max_train_days,
        "max_train_tokens": max_train_tokens,
        "product_vocab": product_vocab,
        "channel_vocab": channel_vocab,
        "text_vocabulary": selected_terms,
        "idf": {term: round(value, 8) for term, value in idf.items()},
        "train_row_count": train_count,
    }


def l2_normalize(values):
    norm = math.sqrt(sum(value * value for value in values))
    if norm == 0:
        return values
    return [value / norm for value in values]


def term_hash(term, dimensions):
    digest = hashlib.sha256(term.encode("utf-8")).digest()
    index = int.from_bytes(digest[:4], "big") % dimensions
    sign = 1 if digest[4] % 2 == 0 else -1
    return index, sign


def dense_hash_embedding(row_tokens, idf, dimensions):
    vector = [0.0] * dimensions
    counts = Counter(row_tokens)
    for term, count in counts.items():
        index, sign = term_hash(term, dimensions)
        weight = count * idf.get(term, 1.0)
        vector[index] += sign * weight
    return [round(value, 8) for value in l2_normalize(vector)]


def transform_row(row, metadata, contract):
    min_train_date = parse_day(metadata["min_train_date"])
    day_delta = (parse_day(row["created_at"]) - min_train_date).days
    day_norm = day_delta / metadata["max_train_days"]
    row_tokens = tokens(row["text"], contract["text_feature"]["min_token_length"])
    token_count_norm = len(row_tokens) / metadata["max_train_tokens"]

    features = {
        "case_id": row["case_id"],
        "split": row["split"],
        "target_label": row["label"],
        "days_since_min_train_date": round(day_norm, 8),
        "text_token_count": round(token_count_norm, 8),
    }

    for value in metadata["product_vocab"]:
        features[f"product__{value}"] = 1 if row["product"] == value else 0
    for value in metadata["channel_vocab"]:
        features[f"channel__{value}"] = 1 if row["channel"] == value else 0

    term_counts = Counter(row_tokens)
    for term in metadata["text_vocabulary"]:
        features[f"tfidf__{term}"] = round(term_counts.get(term, 0) * metadata["idf"][term], 8)

    dense_vector = dense_hash_embedding(
        row_tokens,
        metadata["idf"],
        contract["dense_embedding"]["dimensions"],
    )
    dense = {
        "case_id": row["case_id"],
        "split": row["split"],
        **{f"embedding_{index:02d}": value for index, value in enumerate(dense_vector)},
    }
    return features, dense


def unknown_categories(rows, metadata):
    findings = []
    products = set(metadata["product_vocab"])
    channels = set(metadata["channel_vocab"])
    for row in rows:
        if row["product"] not in products:
            findings.append({"case_id": row["case_id"], "field": "product", "value": row["product"], "split": row["split"]})
        if row["channel"] not in channels:
            findings.append({"case_id": row["case_id"], "field": "channel", "value": row["channel"], "split": row["split"]})
    return findings


def dense_norm_issues(dense_rows):
    issues = []
    for row in dense_rows:
        values = [float(value) for key, value in row.items() if key.startswith("embedding_")]
        norm = math.sqrt(sum(value * value for value in values))
        if values and abs(norm - 1.0) > 0.0001 and norm != 0:
            issues.append({"case_id": row["case_id"], "norm": round(norm, 8)})
    return issues


def build(rows, split_rows, contract):
    assignments = split_lookup(split_rows)
    rows = attach_splits(rows, assignments)
    metadata = fit_metadata(rows, contract)

    feature_rows = []
    dense_rows = []
    for row in rows:
        features, dense = transform_row(row, metadata, contract)
        feature_rows.append(features)
        dense_rows.append(dense)

    feature_columns = list(feature_rows[0].keys())
    dense_columns = list(dense_rows[0].keys())
    unknowns = unknown_categories(rows, metadata)
    norm_issues = dense_norm_issues(dense_rows)
    forbidden_used = [
        column
        for column in contract["forbidden_input_columns"]
        if column in feature_columns and column != contract["entity_key"]
    ]

    quality_report = {
        "contract_id": contract["contract_id"],
        "fit_scope": contract["fit_scope"],
        "fit_row_count": metadata["train_row_count"],
        "row_count": len(rows),
        "feature_dimension": len(feature_columns) - 3,
        "dense_embedding_dimension": contract["dense_embedding"]["dimensions"],
        "unknown_categories": unknowns,
        "forbidden_features_used": forbidden_used,
        "dense_norm_issues": norm_issues,
        "gate": "pass" if not unknowns and not forbidden_used and not norm_issues else "review",
    }

    manifest = {
        "manifest_version": "1.0",
        "contract_id": contract["contract_id"],
        "dataset": {
            "path": "data/feature_cases.csv",
            "sha256": sha256_file(DEFAULT_DATASET),
        },
        "split_assignments": {
            "path": "data/split_assignments.csv",
            "sha256": sha256_file(DEFAULT_SPLITS),
        },
        "fit_scope": contract["fit_scope"],
        "feature_columns": feature_columns,
        "dense_embedding_columns": dense_columns,
        "metadata": metadata,
        "quality_gate": quality_report["gate"],
    }

    return manifest, quality_report, feature_rows, dense_rows


def write_decision(path, report, manifest):
    lines = [
        "# Decisión de features",
        "",
        f"Contrato: `{report['contract_id']}`.",
        f"Gate: `{report['gate']}`.",
        "",
        "## Lectura",
        "",
        f"El pipeline ajusta vocabulario, categorias e IDF solo con train. Genera {report['feature_dimension']} features tabulares/textuales y embeddings densos locales de {report['dense_embedding_dimension']} dimensiones.",
        "",
        "## Checks",
        "",
        f"- Categorias desconocidas: {len(report['unknown_categories'])}",
        f"- Columnas prohibidas usadas como feature: {len(report['forbidden_features_used'])}",
        f"- Vectores densos con norma inesperada: {len(report['dense_norm_issues'])}",
        "",
        "## Cómo adaptarlo",
        "",
        "Cambia `contracts/feature_contract.json` para tu dataset: columnas permitidas, columnas prohibidas, dimension del embedding local, top-k y splits indexables. Si sustituyes el encoder local por un modelo neural, conserva el manifest de dimension, versión y metadata.",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--splits", type=Path, default=DEFAULT_SPLITS)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    rows = read_csv(args.dataset)
    splits = read_csv(args.splits)
    contract = read_json(args.contract)
    manifest, report, feature_rows, dense_rows = build(rows, splits, contract)

    if args.write:
        write_json(args.output_dir / "feature_manifest.json", manifest)
        write_json(args.output_dir / "feature_quality_report.json", report)
        write_csv(args.output_dir / "feature_matrix.csv", list(feature_rows[0].keys()), feature_rows)
        write_csv(args.output_dir / "dense_embedding_matrix.csv", list(dense_rows[0].keys()), dense_rows)
        write_decision(args.output_dir / "feature_decision.md", report, manifest)

    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
