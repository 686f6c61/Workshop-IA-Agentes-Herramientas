#!/usr/bin/env python3
import argparse
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATASET = ROOT / "data" / "support_cases.csv"
DEFAULT_CONTRACT = ROOT / "contracts" / "data_contract.json"
DEFAULT_OUTPUT = ROOT / "output"


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_text(value):
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def read_json(path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def check_result(name, passes, detail, severity="block"):
    return {
        "name": name,
        "passes": bool(passes),
        "severity": severity,
        "detail": detail,
    }


def missing_rate(rows, columns):
    total = max(len(rows) * len(columns), 1)
    missing = 0
    by_column = Counter()
    for row in rows:
        for column in columns:
            if row.get(column, "") == "":
                missing += 1
                by_column[column] += 1
    return round(missing / total, 6), dict(by_column)


def find_duplicate_text_across_splits(rows):
    seen = defaultdict(list)
    for row in rows:
        fingerprint = normalize_text(row.get("text", ""))
        if fingerprint:
            seen[fingerprint].append({"case_id": row.get("case_id"), "split": row.get("split")})

    duplicates = []
    for fingerprint, items in seen.items():
        splits = {item["split"] for item in items}
        if len(items) > 1 and len(splits) > 1:
            duplicates.append({"fingerprint": fingerprint, "items": items})
    return duplicates


def find_license_mismatches(rows, contract):
    allowed = contract["allowed_licenses"]
    mismatches = []
    for row in rows:
        split = row.get("split")
        license_value = row.get("license")
        if license_value not in allowed.get(split, []):
            mismatches.append(
                {
                    "case_id": row.get("case_id"),
                    "split": split,
                    "license": license_value,
                    "allowed": allowed.get(split, []),
                }
            )
    return mismatches


def build_report(rows, contract, dataset_path, contract_path):
    required_columns = contract["required_columns"]
    present_columns = list(rows[0].keys()) if rows else []
    missing_columns = [column for column in required_columns if column not in present_columns]
    extra_columns = [column for column in present_columns if column not in required_columns]

    split_counts = Counter(row.get("split") for row in rows)
    label_distribution = Counter(row.get("label") for row in rows)
    label_by_split = defaultdict(Counter)
    product_counts = Counter(row.get("product") for row in rows)
    pii_counts = Counter(row.get("pii_risk") for row in rows)

    for row in rows:
        label_by_split[row.get("split")][row.get("label")] += 1

    duplicate_ids = [case_id for case_id, count in Counter(row.get("case_id") for row in rows).items() if count > 1]
    invalid_splits = sorted({row.get("split") for row in rows} - set(contract["allowed_splits"]))
    invalid_labels = sorted({row.get("label") for row in rows} - set(contract["allowed_labels"]))
    invalid_pii = sorted({row.get("pii_risk") for row in rows} - set(contract["allowed_pii_risk"]))
    miss_rate, missing_by_column = missing_rate(rows, required_columns)
    duplicate_text = find_duplicate_text_across_splits(rows)
    license_mismatches = find_license_mismatches(rows, contract)

    lineage_missing = []
    for row in rows:
        missing = [field for field in contract["required_lineage_fields"] if not row.get(field)]
        if missing:
            lineage_missing.append({"case_id": row.get("case_id"), "missing": missing})

    split_min_failures = {
        split: {
            "actual": split_counts.get(split, 0),
            "minimum": minimum,
        }
        for split, minimum in contract["min_rows_per_split"].items()
        if split_counts.get(split, 0) < minimum
    }

    label_min_failures = {
        label: {
            "actual": label_distribution.get(label, 0),
            "minimum": contract["min_label_count_total"],
        }
        for label in contract["allowed_labels"]
        if label_distribution.get(label, 0) < contract["min_label_count_total"]
    }

    checks = [
        check_result(
            "schema_columns",
            not missing_columns,
            {"missing_columns": missing_columns, "extra_columns": extra_columns},
        ),
        check_result("case_id_unique", not duplicate_ids, {"duplicate_case_ids": duplicate_ids}),
        check_result("split_values", not invalid_splits, {"invalid_splits": invalid_splits}),
        check_result("label_values", not invalid_labels, {"invalid_labels": invalid_labels}),
        check_result("missing_rate", miss_rate <= contract["max_missing_rate"], {"missing_rate": miss_rate, "missing_by_column": missing_by_column}),
        check_result("split_minimums", not split_min_failures, split_min_failures),
        check_result("label_minimums", not label_min_failures, label_min_failures, severity="review"),
        check_result("license_compatibility", not license_mismatches, {"license_mismatches": license_mismatches}),
        check_result("pii_risk_allowed", not invalid_pii, {"invalid_pii_risk_values": invalid_pii}),
        check_result("lineage_complete", not lineage_missing, {"lineage_missing": lineage_missing}),
        check_result(
            "duplicate_text_across_splits",
            len(duplicate_text) <= contract["max_duplicate_text_across_splits"],
            {"duplicates": duplicate_text},
        ),
    ]

    blocking_failures = [check for check in checks if not check["passes"] and check["severity"] == "block"]
    review_failures = [check for check in checks if not check["passes"] and check["severity"] == "review"]
    gate = "block" if blocking_failures else ("review" if review_failures else "pass")

    return {
        "contract_id": contract["contract_id"],
        "owner": contract["owner"],
        "purpose": contract["purpose"],
        "dataset_path": str(dataset_path.relative_to(ROOT)),
        "dataset_hash_sha256": sha256_file(dataset_path),
        "contract_hash_sha256": sha256_file(contract_path),
        "row_count": len(rows),
        "split_counts": dict(split_counts),
        "label_distribution": dict(label_distribution),
        "label_by_split": {split: dict(counts) for split, counts in label_by_split.items()},
        "product_counts": dict(product_counts),
        "pii_risk_counts": dict(pii_counts),
        "checks": checks,
        "gate": gate,
        "recommendation": recommendation_for_gate(gate),
    }


def recommendation_for_gate(gate):
    if gate == "pass":
        return "usar como dataset didactico y adaptar contrato antes de usar datos reales"
    if gate == "review":
        return "revisar puntos marcados antes de automatizar una release"
    return "bloquear uso hasta corregir fallos de contrato"


def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_dataset_card(path, report):
    lines = [
        "# Dataset card: support_cases",
        "",
        f"Contrato: `{report['contract_id']}`.",
        f"Owner: `{report['owner']}`.",
        f"Filas: `{report['row_count']}`.",
        f"Hash dataset: `{report['dataset_hash_sha256']}`.",
        "",
        "## Uso previsto",
        "",
        report["purpose"],
        "",
        "## Distribución",
        "",
        "| Campo | Conteo |",
        "|---|---:|",
        f"| train | {report['split_counts'].get('train', 0)} |",
        f"| validation | {report['split_counts'].get('validation', 0)} |",
        f"| test | {report['split_counts'].get('test', 0)} |",
        "",
        "## Etiquetas",
        "",
        "| Etiqueta | Conteo |",
        "|---|---:|",
    ]
    for label, count in sorted(report["label_distribution"].items()):
        lines.append(f"| `{label}` | {count} |")
    lines.extend(
        [
            "",
            "## Resultado del gate",
            "",
            f"Estado: `{report['gate']}`.",
            f"Recomendación: {report['recommendation']}.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_release_gate(report):
    blocking = [check for check in report["checks"] if not check["passes"] and check["severity"] == "block"]
    review = [check for check in report["checks"] if not check["passes"] and check["severity"] == "review"]
    return {
        "gate": report["gate"],
        "dataset_hash_sha256": report["dataset_hash_sha256"],
        "contract_hash_sha256": report["contract_hash_sha256"],
        "blocking_failures": [check["name"] for check in blocking],
        "review_failures": [check["name"] for check in review],
        "must_fix_before_training": [check["name"] for check in blocking],
        "recommendation": report["recommendation"],
    }


def build_leakage_report(report):
    leakage_check = next(check for check in report["checks"] if check["name"] == "duplicate_text_across_splits")
    return {
        "check": "duplicate_text_across_splits",
        "passes": leakage_check["passes"],
        "duplicates": leakage_check["detail"]["duplicates"],
        "reading": "sin duplicados textuales entre splits" if leakage_check["passes"] else "revisar ejemplos cruzados antes de evaluar",
    }


def write_decision(path, report):
    checks = "\n".join(
        f"- `{check['name']}`: {'pasa' if check['passes'] else 'revisar'} — {check['detail']}"
        for check in report["checks"]
    )
    text = f"""# Decisión de datos

Estado: **{report['gate']}**.

## Lectura

Este dataset puede usarse como material didactico porque tiene contrato, schema esperado, splits definidos, licencias compatibles, linaje por fila y hashes reproducibles.
Antes de usar datos reales, el contrato debería ampliarse con fuentes originales, política de retención, revisión de etiquetas, evaluación por slices y propietario operativo.

## Checks

{checks}
"""
    path.write_text(text, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    rows = read_csv(args.dataset)
    contract = read_json(args.contract)
    report = build_report(rows, contract, args.dataset, args.contract)
    manifest = {
        "contract_id": report["contract_id"],
        "owner": report["owner"],
        "purpose": report["purpose"],
        "dataset_hash_sha256": report["dataset_hash_sha256"],
        "contract_hash_sha256": report["contract_hash_sha256"],
        "row_count": report["row_count"],
        "splits": report["split_counts"],
        "gate": report["gate"],
    }

    if args.write:
        write_json(args.output_dir / "data_quality_report.json", report)
        write_json(args.output_dir / "lineage_manifest.json", manifest)
        write_json(args.output_dir / "data_release_gate.json", build_release_gate(report))
        write_json(args.output_dir / "leakage_report.json", build_leakage_report(report))
        write_dataset_card(args.output_dir / "dataset_card.md", report)
        write_decision(args.output_dir / "data_release_decision.md", report)

    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
