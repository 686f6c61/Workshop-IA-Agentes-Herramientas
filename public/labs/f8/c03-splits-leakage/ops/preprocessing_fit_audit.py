#!/usr/bin/env python3
import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET = ROOT / "data" / "support_split_cases.csv"
DEFAULT_MANIFEST = ROOT / "output" / "split_manifest.json"
DEFAULT_OUTPUT = ROOT / "output"
STOPWORDS = {
    "a",
    "al",
    "con",
    "de",
    "del",
    "el",
    "en",
    "la",
    "las",
    "los",
    "por",
    "sobre",
    "un",
    "una",
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


def normalize_text(value):
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def tokens(value):
    return [token for token in normalize_text(value).split() if token and token not in STOPWORDS]


def vocabulary(rows):
    counts = Counter()
    for row in rows:
        counts.update(tokens(row["text"]))
    return counts


def split_lookup(manifest):
    return {
        item["case_id"]: item["split"]
        for item in manifest["assignments"]
    }


def rows_by_split(rows, assignments):
    buckets = defaultdict(list)
    for row in rows:
        buckets[assignments[row["case_id"]]].append(row)
    return buckets


def unseen_terms(rows, train_vocab):
    result = {}
    for row in rows:
        missing = sorted(set(tokens(row["text"])) - train_vocab)
        if missing:
            result[row["case_id"]] = missing
    return result


def build_report(rows, manifest):
    assignments = split_lookup(manifest)
    buckets = rows_by_split(rows, assignments)
    train_vocab_counts = vocabulary(buckets["train"])
    all_vocab_counts = vocabulary(rows)
    train_vocab = set(train_vocab_counts)
    all_vocab = set(all_vocab_counts)
    leaked_terms = sorted(all_vocab - train_vocab)

    reserved_rows = buckets["validation"] + buckets["test"]
    reserved_unseen = unseen_terms(reserved_rows, train_vocab)

    return {
        "manifest_policy_id": manifest["policy_id"],
        "selected_strategy": manifest["split_contract"]["selected_strategy"],
        "fit_train_only": {
            "vocabulary_size": len(train_vocab),
            "fit_scope": "train",
        },
        "fit_all_data": {
            "vocabulary_size": len(all_vocab),
            "extra_terms_learned_from_reserved_splits": leaked_terms,
            "extra_term_count": len(leaked_terms),
        },
        "reserved_split_terms_not_seen_in_train": reserved_unseen,
        "decision": (
            "block_fit_all_data"
            if leaked_terms
            else "ok_no_extra_terms_detected"
        ),
    }


def write_decision(path, report):
    lines = [
        "# Decisión de preprocesado",
        "",
        f"Estrategia de split usada: `{report['selected_strategy']}`.",
        f"Decisión: `{report['decision']}`.",
        "",
        "## Lectura",
        "",
        "El vectorizador ajustado con todo el dataset aprende terminos que solo aparecen en validation o test. En un proyecto real, eso significa que el vocabulario ya conoce parte de los datos reservados.",
        "",
        "| Fit | Tamano de vocabulario | Lectura |",
        "|---|---:|---|",
        f"| Solo train | {report['fit_train_only']['vocabulary_size']} | Correcto para desarrollo. |",
        f"| Todo el dataset | {report['fit_all_data']['vocabulary_size']} | No usar para medir. |",
        "",
        "## Términos que entrarian indebidamente",
        "",
    ]

    extra_terms = report["fit_all_data"]["extra_terms_learned_from_reserved_splits"]
    if extra_terms:
        lines.append(", ".join(f"`{term}`" for term in extra_terms))
    else:
        lines.append("No se detectaron terminos adicionales.")

    lines.extend(
        [
            "",
            "## Regla operativa",
            "",
            "Crea el split, ajusta el vectorizador con train y aplica ese mismo vectorizador a validation y test. Guarda los parámetros del vectorizador junto al manifiesto de split.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    rows = read_csv(args.dataset)
    manifest = read_json(args.manifest)
    report = build_report(rows, manifest)
    if args.write:
        write_json(args.output_dir / "preprocessing_fit_report.json", report)
        write_decision(args.output_dir / "preprocessing_fit_decision.md", report)
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
