#!/usr/bin/env python3
import argparse
import csv
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET = ROOT / "data" / "quality_cases_dirty.csv"
DEFAULT_CONTRACT = ROOT / "contracts" / "quality_contract.json"
DEFAULT_OUTPUT = ROOT / "output"


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
    return set(normalize_text(value).split())


def jaccard(left, right):
    left_tokens = tokens(left)
    right_tokens = tokens(right)
    if not left_tokens and not right_tokens:
        return 1.0
    if not left_tokens or not right_tokens:
        return 0.0
    return len(left_tokens & right_tokens) / len(left_tokens | right_tokens)


def check_result(name, passes, detail, severity="block"):
    return {
        "name": name,
        "passes": bool(passes),
        "severity": severity,
        "detail": detail,
    }


def missing_by_column(rows, columns):
    counts = Counter()
    for row in rows:
        for column in columns:
            if not row.get(column):
                counts[column] += 1
    total_cells = max(len(rows) * len(columns), 1)
    total_missing = sum(counts.values())
    return round(total_missing / total_cells, 6), dict(counts)


def invalid_values(rows, column, allowed):
    allowed_set = set(allowed)
    return sorted({row.get(column) for row in rows if row.get(column) not in allowed_set})


def duplicate_ids(rows):
    counts = Counter(row.get("case_id") for row in rows)
    return sorted(case_id for case_id, count in counts.items() if case_id and count > 1)


def exact_cross_split_duplicates(rows):
    seen = defaultdict(list)
    for row in rows:
        fingerprint = normalize_text(row.get("text", ""))
        if fingerprint:
            seen[fingerprint].append({"case_id": row.get("case_id"), "split": row.get("split")})

    duplicates = []
    for fingerprint, items in seen.items():
        splits = {item["split"] for item in items}
        if len(items) > 1 and len(splits) > 1:
            duplicates.append({"kind": "exact", "fingerprint": fingerprint, "items": items})
    return duplicates


def near_cross_split_duplicates(rows, threshold):
    pairs = []
    for index, left in enumerate(rows):
        for right in rows[index + 1 :]:
            if left.get("split") == right.get("split"):
                continue
            score = jaccard(left.get("text", ""), right.get("text", ""))
            if score >= threshold and normalize_text(left.get("text", "")) != normalize_text(right.get("text", "")):
                pairs.append(
                    {
                        "kind": "near",
                        "left_case_id": left.get("case_id"),
                        "left_split": left.get("split"),
                        "right_case_id": right.get("case_id"),
                        "right_split": right.get("split"),
                        "jaccard": round(score, 6),
                    }
                )
    return pairs


def license_mismatches(rows, contract):
    mismatches = []
    for row in rows:
        split = row.get("split")
        allowed = contract["allowed_licenses"].get(split, [])
        if row.get("license") not in allowed:
            mismatches.append(
                {
                    "case_id": row.get("case_id"),
                    "split": split,
                    "license": row.get("license"),
                    "allowed": allowed,
                }
            )
    return mismatches


def split_minimum_failures(rows, contract):
    counts = Counter(row.get("split") for row in rows)
    return {
        split: {"actual": counts.get(split, 0), "minimum": minimum}
        for split, minimum in contract["min_rows_per_split"].items()
        if counts.get(split, 0) < minimum
    }


def label_review_candidates(rows, contract):
    candidates = []
    threshold = contract["min_model_probability_for_label"]
    for row in rows:
        reasons = []
        if row.get("annotator_a") != row.get("annotator_b"):
            reasons.append("annotator_disagreement")
        if row.get("expected_label") and row.get("label") != row.get("expected_label"):
            reasons.append("label_differs_from_reference")
        try:
            probability = float(row.get("model_probability", "nan"))
        except ValueError:
            probability = math.nan
        if math.isnan(probability) or probability < threshold:
            reasons.append("low_label_confidence")
        if reasons:
            candidates.append(
                {
                    "case_id": row.get("case_id"),
                    "split": row.get("split"),
                    "label": row.get("label"),
                    "expected_label": row.get("expected_label"),
                    "annotator_a": row.get("annotator_a"),
                    "annotator_b": row.get("annotator_b"),
                    "model_probability": row.get("model_probability"),
                    "reasons": reasons,
                }
            )
    return candidates


def cohen_kappa(rows):
    labels = sorted({row.get("annotator_a") for row in rows} | {row.get("annotator_b") for row in rows})
    labels = [label for label in labels if label]
    total = len(rows) or 1
    observed = sum(1 for row in rows if row.get("annotator_a") == row.get("annotator_b")) / total
    left_counts = Counter(row.get("annotator_a") for row in rows)
    right_counts = Counter(row.get("annotator_b") for row in rows)
    expected = sum((left_counts[label] / total) * (right_counts[label] / total) for label in labels)
    if expected == 1:
        value = 1.0
    else:
        value = (observed - expected) / (1 - expected)
    return {
        "observed_agreement": round(observed, 6),
        "expected_agreement": round(expected, 6),
        "kappa": round(value, 6),
    }


def distribution(rows, column):
    counts = Counter(row.get(column) for row in rows if row.get(column))
    total = sum(counts.values()) or 1
    return {key: counts[key] / total for key in sorted(counts)}


def total_variation(left, right):
    keys = sorted(set(left) | set(right))
    return 0.5 * sum(abs(left.get(key, 0.0) - right.get(key, 0.0)) for key in keys)


def split_label_drift(rows):
    global_dist = distribution(rows, "label")
    by_split = {}
    for split in sorted({row.get("split") for row in rows if row.get("split")}):
        split_rows = [row for row in rows if row.get("split") == split]
        dist = distribution(split_rows, "label")
        by_split[split] = {
            "distribution": {key: round(value, 6) for key, value in dist.items()},
            "total_variation_vs_global": round(total_variation(global_dist, dist), 6),
        }
    return {
        "global_distribution": {key: round(value, 6) for key, value in global_dist.items()},
        "by_split": by_split,
    }


def build_report(rows, contract):
    required = contract["required_columns"]
    present = list(rows[0].keys()) if rows else []
    missing_columns = [column for column in required if column not in present]
    extra_columns = [column for column in present if column not in required]
    missing_rate, missing_columns_counts = missing_by_column(rows, required)
    exact_duplicates = exact_cross_split_duplicates(rows)
    near_duplicates = near_cross_split_duplicates(rows, contract["near_duplicate_jaccard_threshold"])
    label_candidates = label_review_candidates(rows, contract)
    kappa = cohen_kappa(rows)
    label_drift = split_label_drift(rows)
    high_label_drift = {
        split: detail
        for split, detail in label_drift["by_split"].items()
        if detail["total_variation_vs_global"] > contract["max_split_label_total_variation"]
    }

    checks = [
        check_result("schema_columns", not missing_columns, {"missing_columns": missing_columns, "extra_columns": extra_columns}),
        check_result("case_id_unique", not duplicate_ids(rows), {"duplicate_case_ids": duplicate_ids(rows)}),
        check_result("split_values", not invalid_values(rows, "split", contract["allowed_splits"]), {"invalid_splits": invalid_values(rows, "split", contract["allowed_splits"])}),
        check_result("product_values", not invalid_values(rows, "product", contract["allowed_products"]), {"invalid_products": invalid_values(rows, "product", contract["allowed_products"])}),
        check_result("language_values", not invalid_values(rows, "language", contract["allowed_languages"]), {"invalid_languages": invalid_values(rows, "language", contract["allowed_languages"])}),
        check_result("channel_values", not invalid_values(rows, "channel", contract["allowed_channels"]), {"invalid_channels": invalid_values(rows, "channel", contract["allowed_channels"])}),
        check_result("label_values", not invalid_values(rows, "label", contract["allowed_labels"]), {"invalid_labels": invalid_values(rows, "label", contract["allowed_labels"])}),
        check_result("pii_risk_values", not invalid_values(rows, "pii_risk", contract["allowed_pii_risk"]), {"invalid_pii_risk": invalid_values(rows, "pii_risk", contract["allowed_pii_risk"])}),
        check_result("missing_rate", missing_rate <= contract["max_missing_rate"], {"missing_rate": missing_rate, "missing_by_column": missing_columns_counts}),
        check_result("license_compatibility", not license_mismatches(rows, contract), {"license_mismatches": license_mismatches(rows, contract)}),
        check_result("split_minimums", not split_minimum_failures(rows, contract), split_minimum_failures(rows, contract)),
        check_result("exact_cross_split_duplicates", len(exact_duplicates) <= contract["max_exact_cross_split_duplicates"], {"duplicates": exact_duplicates}),
        check_result("near_cross_split_duplicates", len(near_duplicates) <= contract["max_near_cross_split_duplicates"], {"duplicates": near_duplicates}),
        check_result("label_review_queue", not label_candidates, {"candidates": label_candidates}, severity="review"),
        check_result("annotator_agreement", kappa["kappa"] >= contract["min_kappa"], kappa, severity="review"),
        check_result("split_label_distribution", not high_label_drift, {"split_label_drift": label_drift, "high_drift": high_label_drift}, severity="review"),
    ]

    blocking = [check for check in checks if not check["passes"] and check["severity"] == "block"]
    review = [check for check in checks if not check["passes"] and check["severity"] == "review"]
    gate = "block" if blocking else ("review" if review else "pass")

    return {
        "contract_id": contract["contract_id"],
        "owner": contract["owner"],
        "purpose": contract["purpose"],
        "row_count": len(rows),
        "split_counts": dict(Counter(row.get("split") for row in rows)),
        "label_distribution": dict(Counter(row.get("label") for row in rows)),
        "checks": checks,
        "label_review_candidates": label_candidates,
        "exact_cross_split_duplicates": exact_duplicates,
        "near_cross_split_duplicates": near_duplicates,
        "annotator_agreement": kappa,
        "stratification_drift": label_drift,
        "gate": gate,
        "recommendation": recommendation(gate),
    }


def recommendation(gate):
    if gate == "pass":
        return "dataset listo para el uso declarado"
    if gate == "review":
        return "revisar etiquetas o distribuciones antes de automatizar la decisión"
    return "bloquear uso hasta corregir fallos de contrato, leakage o schema"


def write_duplicate_candidates(path, report):
    rows = []
    for item in report["exact_cross_split_duplicates"]:
        rows.append(
            {
                "kind": "exact",
                "left_case_id": item["items"][0]["case_id"],
                "left_split": item["items"][0]["split"],
                "right_case_id": item["items"][1]["case_id"],
                "right_split": item["items"][1]["split"],
                "score": "1.0",
            }
        )
    for item in report["near_cross_split_duplicates"]:
        rows.append(
            {
                "kind": item["kind"],
                "left_case_id": item["left_case_id"],
                "left_split": item["left_split"],
                "right_case_id": item["right_case_id"],
                "right_split": item["right_split"],
                "score": str(item["jaccard"]),
            }
        )
    write_csv(path, ["kind", "left_case_id", "left_split", "right_case_id", "right_split", "score"], rows)


def write_label_queue(path, report):
    rows = []
    for item in report["label_review_candidates"]:
        rows.append(
            {
                "case_id": item["case_id"],
                "split": item["split"],
                "label": item["label"],
                "expected_label": item["expected_label"],
                "annotator_a": item["annotator_a"],
                "annotator_b": item["annotator_b"],
                "model_probability": item["model_probability"],
                "reasons": ";".join(item["reasons"]),
            }
        )
    write_csv(path, ["case_id", "split", "label", "expected_label", "annotator_a", "annotator_b", "model_probability", "reasons"], rows)


def write_csv(path, fieldnames, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_release_gate(path, report):
    blocking = [check["name"] for check in report["checks"] if not check["passes"] and check["severity"] == "block"]
    review = [check["name"] for check in report["checks"] if not check["passes"] and check["severity"] == "review"]
    write_json(
        path,
        {
            "gate": report["gate"],
            "blocking_failures": blocking,
            "review_failures": review,
            "recommendation": report["recommendation"],
        },
    )


def write_clean_actions(path, report):
    blocking = [check["name"] for check in report["checks"] if not check["passes"] and check["severity"] == "block"]
    review = [check["name"] for check in report["checks"] if not check["passes"] and check["severity"] == "review"]
    lines = [
        "# Plan de limpieza",
        "",
        f"Estado del gate: **{report['gate']}**.",
        "",
        "## Primero: bloquear uso automatizado",
        "",
        "No entrenes, no publiques una eval y no indexes este snapshot mientras existan fallos de bloqueo.",
        "",
        "## Fallos de bloqueo",
        "",
    ]
    if blocking:
        for item in blocking:
            lines.append(f"- `{item}`")
    else:
        lines.append("- Ninguno.")
    lines.extend(["", "## Revisiones necesarias", ""])
    if review:
        for item in review:
            lines.append(f"- `{item}`")
    else:
        lines.append("- Ninguna.")
    lines.extend(
        [
            "",
            "## Orden recomendado",
            "",
            "1. Corregir schema, valores fuera de catalogo y licencias incompatibles.",
            "2. Separar o eliminar duplicados que cruzan splits.",
            "3. Abrir `label_review_queue.csv` y revisar cada etiqueta con la política de anotación.",
            "4. Recalcular kappa tras la revisión.",
            "5. Reejecutar el gate y guardar el nuevo reporte.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    rows = read_csv(args.dataset)
    contract = read_json(args.contract)
    report = build_report(rows, contract)

    if args.write:
        write_json(args.output_dir / "quality_report.json", report)
        write_release_gate(args.output_dir / "release_gate.json", report)
        write_duplicate_candidates(args.output_dir / "duplicate_candidates.csv", report)
        write_label_queue(args.output_dir / "label_review_queue.csv", report)
        write_clean_actions(args.output_dir / "clean_actions.md", report)

    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
