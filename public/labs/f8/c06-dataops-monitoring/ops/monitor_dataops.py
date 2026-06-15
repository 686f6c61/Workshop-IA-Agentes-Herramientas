#!/usr/bin/env python3
import argparse
import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REFERENCE = ROOT / "data" / "reference_events.csv"
DEFAULT_PRODUCTION = ROOT / "data" / "production_events.csv"
DEFAULT_CONTRACT = ROOT / "contracts" / "monitoring_contract.json"
DEFAULT_OUTPUT = ROOT / "output"


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def read_json(path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def as_float(value):
    return float(str(value).replace(",", "."))


def as_int(value):
    return int(float(value))


def pct(value):
    return round(value, 6)


def distribution(rows, column):
    counts = Counter(row[column] for row in rows if row.get(column))
    total = sum(counts.values()) or 1
    return {key: counts[key] / total for key in sorted(counts)}


def smooth(left, right, epsilon=1e-6):
    keys = sorted(set(left) | set(right))
    p = [left.get(key, 0.0) + epsilon for key in keys]
    q = [right.get(key, 0.0) + epsilon for key in keys]
    return keys, p, q


def total_variation(left, right):
    keys, p, q = smooth(left, right, epsilon=0.0)
    return pct(0.5 * sum(abs(a - b) for a, b in zip(p, q))), keys


def psi(left, right):
    keys, p, q = smooth(left, right)
    return pct(sum((b - a) * math.log(b / a) for a, b in zip(p, q))), keys


def p95(values):
    if not values:
        return None
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, math.ceil(0.95 * len(ordered)) - 1))
    return ordered[index]


def safe_capture(rows):
    positives = [row for row in rows if as_int(row["true_priority"]) == 1]
    if not positives:
        return None
    safe = [row for row in positives if row["decision"] != "normal"]
    return pct(len(safe) / len(positives))


def miss_rate(rows):
    positives = [row for row in rows if as_int(row["true_priority"]) == 1]
    if not positives:
        return None
    misses = [row for row in positives if row["decision"] == "normal"]
    return pct(len(misses) / len(positives))


def review_rate(rows):
    if not rows:
        return None
    reviews = [row for row in rows if row["decision"] == "revisar"]
    return pct(len(reviews) / len(rows))


def missing_trace_rate(rows):
    if not rows:
        return None
    missing = [row for row in rows if not row.get("trace_id")]
    return pct(len(missing) / len(rows))


def group_by(rows, field):
    groups = defaultdict(list)
    for row in rows:
        groups[row[field]].append(row)
    return dict(groups)


def check_schema(rows, contract):
    present = list(rows[0].keys()) if rows else []
    required = contract["required_columns"]
    missing = [column for column in required if column not in present]
    extra = [column for column in present if column not in required]
    invalid = []
    for column, allowed in contract["allowed_values"].items():
        values = sorted({row.get(column) for row in rows if row.get(column) not in set(allowed)})
        if values:
            invalid.append({"column": column, "values": values})
    return {"missing_columns": missing, "extra_columns": extra, "invalid_values": invalid}


def window_metrics(rows, contract):
    latencies = [as_float(row["latency_ms"]) for row in rows]
    metrics = {
        "n": len(rows),
        "missing_trace_rate": missing_trace_rate(rows),
        "latency_p95_ms": p95(latencies),
        "review_rate": review_rate(rows),
        "miss_rate": miss_rate(rows),
        "safety_capture": safe_capture(rows),
    }
    slice_metrics = []
    for field in contract["slice_fields"]:
        for value, grouped in sorted(group_by(rows, field).items()):
            slice_id = f"{field}={value}"
            slice_metrics.append({
                "slice_id": slice_id,
                "field": field,
                "value": value,
                "n": len(grouped),
                "missing_trace_rate": missing_trace_rate(grouped),
                "latency_p95_ms": p95([as_float(row["latency_ms"]) for row in grouped]),
                "review_rate": review_rate(grouped),
                "miss_rate": miss_rate(grouped),
                "safety_capture": safe_capture(grouped),
            })
    return metrics, slice_metrics


def drift_report(reference_rows, current_rows, contract):
    rows = []
    for column in contract["drift_columns"]:
        ref = distribution(reference_rows, column)
        cur = distribution(current_rows, column)
        tv, keys = total_variation(ref, cur)
        psi_value, _ = psi(ref, cur)
        rows.append({
            "column": column,
            "total_variation": tv,
            "psi": psi_value,
            "reference_distribution": {key: pct(ref.get(key, 0.0)) for key in keys},
            "current_distribution": {key: pct(cur.get(key, 0.0)) for key in keys},
        })
    return rows


def flag_window(window, metrics, slice_metrics, drifts, schema, contract):
    flags = []
    slo = contract["slo"]

    if schema["missing_columns"] or schema["invalid_values"]:
        flags.append({"severity": "block", "window": window, "kind": "schema", "message": "El evento no cumple el contrato de columnas o valores.", "detail": schema})
    if metrics["missing_trace_rate"] is not None and metrics["missing_trace_rate"] > slo["max_missing_trace_rate"]:
        flags.append({"severity": "block", "window": window, "kind": "missing_trace_rate", "message": "Hay eventos sin trace_id; no se puede investigar bien la ventana.", "value": metrics["missing_trace_rate"], "threshold": slo["max_missing_trace_rate"]})
    if metrics["latency_p95_ms"] is not None and metrics["latency_p95_ms"] > slo["max_latency_p95_ms"]:
        flags.append({"severity": "review", "window": window, "kind": "latency_p95", "message": "La latencia p95 supera el SLO.", "value": metrics["latency_p95_ms"], "threshold": slo["max_latency_p95_ms"]})
    if metrics["miss_rate"] is not None and metrics["miss_rate"] > slo["max_miss_rate"]:
        flags.append({"severity": "block", "window": window, "kind": "miss_rate", "message": "Demasiados casos prioritarios terminan en flujo normal.", "value": metrics["miss_rate"], "threshold": slo["max_miss_rate"]})
    if metrics["safety_capture"] is not None and metrics["safety_capture"] < slo["min_safety_capture"]:
        flags.append({"severity": "block", "window": window, "kind": "safety_capture", "message": "La captura segura cae por debajo del SLO.", "value": metrics["safety_capture"], "threshold": slo["min_safety_capture"]})
    if metrics["review_rate"] is not None and metrics["review_rate"] > slo["max_review_rate"]:
        flags.append({"severity": "review", "window": window, "kind": "review_rate", "message": "La carga de revisión puede superar capacidad operativa.", "value": metrics["review_rate"], "threshold": slo["max_review_rate"]})

    for drift in drifts:
        if drift["total_variation"] > slo["max_total_variation"]:
            flags.append({"severity": "review", "window": window, "kind": "drift_total_variation", "message": "La distribución actual se aleja de la referencia.", "column": drift["column"], "value": drift["total_variation"], "threshold": slo["max_total_variation"]})
        if drift["psi"] > slo["max_psi"]:
            flags.append({"severity": "review", "window": window, "kind": "drift_psi", "message": "El PSI indica cambio relevante frente a referencia.", "column": drift["column"], "value": drift["psi"], "threshold": slo["max_psi"]})

    critical = set(contract["critical_slices"])
    for row in slice_metrics:
        if row["slice_id"] not in critical:
            continue
        if row["miss_rate"] is not None and row["miss_rate"] > slo["max_miss_rate"]:
            flags.append({"severity": "block", "window": window, "kind": "critical_slice_miss_rate", "slice_id": row["slice_id"], "message": "Un slice crítico pierde demasiados casos prioritarios.", "value": row["miss_rate"], "threshold": slo["max_miss_rate"]})
        if row["latency_p95_ms"] is not None and row["latency_p95_ms"] > slo["max_latency_p95_ms"]:
            flags.append({"severity": "review", "window": window, "kind": "critical_slice_latency", "slice_id": row["slice_id"], "message": "Un slice crítico supera latencia p95.", "value": row["latency_p95_ms"], "threshold": slo["max_latency_p95_ms"]})
    return flags


def status_from_flags(flags):
    severities = {flag["severity"] for flag in flags}
    if "block" in severities:
        return "block"
    if "review" in severities:
        return "review"
    return "pass"


def build_report(reference_path, production_path, contract_path):
    reference_rows = read_csv(reference_path)
    production_rows = read_csv(production_path)
    contract = read_json(contract_path)
    schema = check_schema(reference_rows + production_rows, contract)
    windows = []
    all_flags = []

    for window in contract["production_windows"]:
        rows = [row for row in production_rows if row["window"] == window]
        metrics, slice_metrics = window_metrics(rows, contract)
        drifts = drift_report(reference_rows, rows, contract)
        flags = flag_window(window, metrics, slice_metrics, drifts, schema, contract)
        all_flags.extend(flags)
        windows.append({
            "window": window,
            "status": status_from_flags(flags),
            "metrics": metrics,
            "drift": drifts,
            "slice_metrics": slice_metrics,
            "flags": flags,
            "versions": {
                "pipeline": sorted({row["pipeline_version"] for row in rows}),
                "model": sorted({row["model_version"] for row in rows}),
                "data": sorted({row["data_version"] for row in rows}),
            },
        })

    return {
        "run_id": "f8-c06-dataops-monitoring-run",
        "contract_id": contract["contract_id"],
        "status": status_from_flags(all_flags),
        "inputs": {
            "reference": str(reference_path.relative_to(ROOT)),
            "production": str(production_path.relative_to(ROOT)),
            "contract": str(contract_path.relative_to(ROOT)),
            "reference_sha256": sha256_file(reference_path),
            "production_sha256": sha256_file(production_path),
            "contract_sha256": sha256_file(contract_path),
        },
        "contract": contract,
        "windows": windows,
        "flags": all_flags,
    }


def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_csv(path, fieldnames, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def scorecard_rows(report):
    rows = []
    for window in report["windows"]:
        metrics = window["metrics"]
        rows.append({
            "window": window["window"],
            "status": window["status"],
            "n": metrics["n"],
            "missing_trace_rate": metrics["missing_trace_rate"],
            "latency_p95_ms": metrics["latency_p95_ms"],
            "review_rate": metrics["review_rate"],
            "miss_rate": metrics["miss_rate"],
            "safety_capture": metrics["safety_capture"],
            "flag_count": len(window["flags"]),
        })
    return rows


def render_alerts(report):
    lines = ["# Alertas DataOps", "", f"Estado global: **{report['status']}**", ""]
    for window in report["windows"]:
        lines.extend([f"## Ventana {window['window']}", "", f"Estado: **{window['status']}**", ""])
        if not window["flags"]:
            lines.append("- Sin alertas.")
        for flag in window["flags"]:
            scope = flag.get("slice_id") or flag.get("column") or flag["kind"]
            lines.append(f"- `{flag['severity']}` · `{scope}`: {flag['message']} valor `{flag.get('value')}` frente a `{flag.get('threshold')}`.")
        lines.append("")
    return "\n".join(lines)


def render_decision(report):
    lines = [
        "# Decisión operativa DataOps",
        "",
        f"Estado global: **{report['status']}**.",
        "",
        "## Lectura",
        "",
        "Este gate no decide si el modelo es inteligente. Decide si la ventana de producción es suficientemente trazable, representativa y estable para sostener decisiones.",
        "",
        "| Ventana | Estado | n | Trace faltante | Latencia p95 | Revision | Perdida | Captura segura | Flags |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in scorecard_rows(report):
        lines.append(f"| {row['window']} | `{row['status']}` | {row['n']} | {row['missing_trace_rate']} | {row['latency_p95_ms']} | {row['review_rate']} | {row['miss_rate']} | {row['safety_capture']} | {row['flag_count']} |")
    lines.extend(["", "## Recomendación", ""])
    if report["status"] == "block":
        lines.append("No aumentes automatización ni uses está ventana para reentrenar sin investigar. Empieza por los flags `block`, corrige trazabilidad y revisa slices críticos.")
    elif report["status"] == "review":
        lines.append("Mantener operacion con revisión. No promover cambios de política hasta cerrar drift, latencia o carga humana.")
    else:
        lines.append("La ventana cumple el contrato. Conserva evidencia y sigue monitorizando los mismos SLIs.")
    return "\n".join(lines) + "\n"


def lineage_event(report):
    return {
        "eventType": "COMPLETE",
        "job": {"namespace": "ia-gente-curiosa", "name": "f8-c06-monitor-dataops"},
        "run": {"runId": report["run_id"]},
        "inputs": [
            {"name": report["inputs"]["reference"], "facets": {"sha256": report["inputs"]["reference_sha256"]}},
            {"name": report["inputs"]["production"], "facets": {"sha256": report["inputs"]["production_sha256"]}},
        ],
        "outputs": [
            {"name": "output/monitoring_report.json"},
            {"name": "output/slo_scorecard.csv"},
            {"name": "output/alerts.md"},
        ],
        "facets": {
            "status": report["status"],
            "contract": report["contract_id"],
        },
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference", type=Path, default=DEFAULT_REFERENCE)
    parser.add_argument("--production", type=Path, default=DEFAULT_PRODUCTION)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    report = build_report(args.reference.resolve(), args.production.resolve(), args.contract.resolve())
    if args.write:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        write_json(args.output_dir / "monitoring_report.json", report)
        write_csv(
            args.output_dir / "slo_scorecard.csv",
            ["window", "status", "n", "missing_trace_rate", "latency_p95_ms", "review_rate", "miss_rate", "safety_capture", "flag_count"],
            scorecard_rows(report),
        )
        write_json(args.output_dir / "lineage_event.json", lineage_event(report))
        (args.output_dir / "alerts.md").write_text(render_alerts(report), encoding="utf-8")
        (args.output_dir / "operational_decision.md").write_text(render_decision(report), encoding="utf-8")
    else:
        print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
