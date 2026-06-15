#!/usr/bin/env python3
import argparse
import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EVENTS = ROOT / "data" / "experiment_events.csv"
DEFAULT_CONTRACT = ROOT / "contracts" / "feature_flag_contract.json"
DEFAULT_OUTPUT = ROOT / "output"


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def read_json(path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def bucket_for(unit_id, salt):
    digest = hashlib.sha256(f"{salt}|{unit_id}".encode("utf-8")).hexdigest()
    return int(digest[:12], 16) / float(16**12 - 1)


def context_hash(row, fields):
    payload = "|".join(f"{field}={row.get(field, '')}" for field in fields)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def assign_variant(unit_id, contract):
    bucket = bucket_for(unit_id, contract["salt"])
    cumulative = 0.0
    for variant, share in contract["variants"].items():
        cumulative += share
        if bucket <= cumulative:
            return variant, bucket
    return list(contract["variants"])[-1], bucket


def build_exposures(rows, contract):
    exposures = []
    mismatches = []
    for index, row in enumerate(rows, start=1):
        unit_id = row[contract["targeting_key"]]
        assigned_variant, bucket = assign_variant(unit_id, contract)
        original_variant = row.get("variant", "")
        if original_variant and original_variant != assigned_variant:
            mismatches.append({
                "unit_id": unit_id,
                "dataset_variant": original_variant,
                "flag_variant": assigned_variant,
            })
        exposures.append({
            "unit_id": unit_id,
            "flag_key": contract["flag_key"],
            "variant": assigned_variant,
            "assigned_at": "2026-06-07T09:00:00Z",
            "exposed_at": f"2026-06-07T09:{index:02d}:00Z",
            "flag_version": contract["versión"],
            "context_hash": context_hash(row, contract["context_fields"]),
            "bucket": round(bucket, 6),
        })
    return exposures, mismatches


def summarize(exposures, mismatches, contract):
    counts = {}
    for row in exposures:
        counts[row["variant"]] = counts.get(row["variant"], 0) + 1
    total = len(exposures)
    shares = {variant: round(count / total, 6) for variant, count in counts.items()}
    return {
        "flag_key": contract["flag_key"],
        "versión": contract["versión"],
        "targeting_key": contract["targeting_key"],
        "events": total,
        "variant_counts": counts,
        "variant_shares": shares,
        "dataset_flag_mismatches": mismatches,
        "status": "review" if mismatches else "pass",
    }


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def render(summary):
    lines = [
        "# Asignacion por feature flag",
        "",
        f"Estado: **{summary['status']}**.",
        "",
        "| Variante | Unidades | Share |",
        "|---|---:|---:|",
    ]
    for variant, count in sorted(summary["variant_counts"].items()):
        lines.append(f"| `{variant}` | `{count}` | `{summary['variant_shares'][variant]}` |")
    lines.extend([
        "",
        "## Lectura",
        "",
        "Este ejemplo simula evaluación determinista por flag. En un sistema real, este output debería corresponder a una tabla de exposición: unidad, variante, versión de flag, contexto y momento de exposición.",
        "",
    ])
    if summary["dataset_flag_mismatches"]:
        lines.append("Hay diferencias entre la variante del dataset y la variante calculada por la flag. En producción esto bloquearia el analisis hasta explicar la fuente de verdad.")
    else:
        lines.append("No hay diferencias entre dataset y flag simulada.")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--events", type=Path, default=DEFAULT_EVENTS)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    rows = read_csv(args.events)
    contract = read_json(args.contract)
    exposures, mismatches = build_exposures(rows, contract)
    summary = summarize(exposures, mismatches, contract)
    if args.write:
        write_csv(args.output_dir / "exposure_events.csv", exposures)
        write_json(args.output_dir / "flag_assignment_manifest.json", summary)
        (args.output_dir / "flag_assignment_decision.md").write_text(render(summary), encoding="utf-8")
    else:
        print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
