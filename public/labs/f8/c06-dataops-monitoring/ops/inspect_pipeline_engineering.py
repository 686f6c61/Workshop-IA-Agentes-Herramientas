#!/usr/bin/env python3
import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EVENTS = ROOT / "data" / "production_events.csv"
DEFAULT_SPANS = ROOT / "data" / "trace_spans.csv"
DEFAULT_CONTRACT = ROOT / "contracts" / "pipeline_engineering_contract.json"
DEFAULT_MONITORING = ROOT / "output" / "monitoring_report.json"
DEFAULT_OUTPUT = ROOT / "output"


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def read_json(path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def as_float(value):
    return float(str(value).replace(",", "."))


def pct(value):
    return round(value, 6)


def group_by(rows, field):
    result = defaultdict(list)
    for row in rows:
        result[row[field]].append(row)
    return dict(result)


def idempotency_key(row, fields):
    return "|".join(f"{field}={row.get(field, '')}" for field in fields)


def inspect(events, spans, contract):
    spans_by_trace = group_by(spans, "trace_id")
    spans_by_event = group_by(spans, "event_id")
    event_by_id = {row["event_id"]: row for row in events}
    required_spans = contract["required_spans"]
    required_trace_event_ids = set(contract.get("required_trace_event_ids", []))
    span_order = {name: index for index, name in enumerate(contract["span_order"])}
    span_slos = contract["span_slos_ms"]
    trace_slos = contract["trace_slos"]

    idempotency_counts = Counter(idempotency_key(row, contract["idempotency_key"]) for row in events)
    duplicate_keys = [
        {"key": key, "count": count}
        for key, count in sorted(idempotency_counts.items())
        if count > 1
    ]

    event_checks = []
    flags = []

    for event in events:
        event_id = event["event_id"]
        trace_id = event.get("trace_id", "")
        event_spans = spans_by_event.get(event_id, [])
        span_names = [span["span_name"] for span in event_spans]
        requires_span_detail = event_id in required_trace_event_ids or bool(event_spans)
        missing_spans = [name for name in required_spans if name not in set(span_names)] if requires_span_detail else []
        ordered = sorted(event_spans, key=lambda span: as_float(span["start_ms"]))
        order_indexes = [span_order.get(span["span_name"], 999) for span in ordered]
        order_ok = order_indexes == sorted(order_indexes)
        total_duration = None
        if ordered:
            total_duration = max(as_float(span["start_ms"]) + as_float(span["duration_ms"]) for span in ordered) - min(as_float(span["start_ms"]) for span in ordered)

        slow_spans = []
        for span in event_spans:
            limit = span_slos.get(span["span_name"])
            duration = as_float(span["duration_ms"])
            if limit is not None and duration > limit:
                slow_spans.append({
                    "span_name": span["span_name"],
                    "duration_ms": duration,
                    "threshold_ms": limit,
                })

        check = {
            "event_id": event_id,
            "window": event["window"],
            "trace_id": trace_id,
            "span_count": len(event_spans),
            "requires_span_detail": requires_span_detail,
            "missing_spans": missing_spans,
            "order_ok": order_ok,
            "total_duration_ms": total_duration,
            "slow_spans": slow_spans,
        }
        event_checks.append(check)

        if not trace_id:
            flags.append({"severity": "block", "event_id": event_id, "kind": "missing_trace_id", "message": "El evento no tiene trace_id."})
        if missing_spans:
            flags.append({"severity": "block", "event_id": event_id, "kind": "missing_required_spans", "message": "Faltan spans obligatorios.", "value": missing_spans})
        if not order_ok:
            flags.append({"severity": "review", "event_id": event_id, "kind": "span_order", "message": "Los spans no respetan el orden esperado."})
        if total_duration is not None and total_duration > trace_slos["max_total_trace_duration_ms"]:
            flags.append({"severity": "review", "event_id": event_id, "kind": "trace_duration", "message": "La duracion total de la traza supera el SLO.", "value": pct(total_duration), "threshold": trace_slos["max_total_trace_duration_ms"]})
        for slow in slow_spans:
            flags.append({"severity": "review", "event_id": event_id, "kind": "slow_span", "message": "Un span supera su SLO.", "span_name": slow["span_name"], "value": slow["duration_ms"], "threshold": slow["threshold_ms"]})

    if duplicate_keys:
        flags.append({"severity": "block", "kind": "duplicate_idempotency_key", "message": "Hay claves de idempotencia duplicadas.", "value": duplicate_keys, "threshold": trace_slos["max_duplicate_idempotency_keys"]})

    required_trace_events = [row for row in event_checks if row["requires_span_detail"]]
    missing_required_span_events = [row for row in required_trace_events if row["missing_spans"]]
    events_without_trace = [row for row in events if not row.get("trace_id")]
    summary = {
        "events": len(events),
        "traces": len(spans_by_trace),
        "events_requiring_span_detail": len(required_trace_events),
        "events_without_trace": len(events_without_trace),
        "events_missing_required_spans": len(missing_required_span_events),
        "missing_required_span_rate": pct(len(missing_required_span_events) / len(required_trace_events)) if required_trace_events else 0,
        "duplicate_idempotency_keys": len(duplicate_keys),
        "flags": len(flags),
    }

    return {
        "status": status_from_flags(flags),
        "summary": summary,
        "contract": contract,
        "event_checks": event_checks,
        "flags": flags,
    }


def status_from_flags(flags):
    severities = {flag["severity"] for flag in flags}
    if "block" in severities:
        return "block"
    if "review" in severities:
        return "review"
    return "pass"


def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    fieldnames = ["event_id", "window", "trace_id", "span_count", "requires_span_detail", "missing_spans", "order_ok", "total_duration_ms", "slow_spans"]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            out = dict(row)
            out["missing_spans"] = ",".join(out["missing_spans"])
            out["slow_spans"] = ";".join(f"{item['span_name']}:{item['duration_ms']}>{item['threshold_ms']}" for item in out["slow_spans"])
            writer.writerow(out)


def render_postmortem(engineering_report, monitoring_report=None):
    lines = [
        "# Postmortem DataOps",
        "",
        "## Resumen",
        "",
        f"Estado de ingeniería: **{engineering_report['status']}**.",
        f"Eventos revisados: `{engineering_report['summary']['events']}`.",
        f"Eventos sin traza: `{engineering_report['summary']['events_without_trace']}`.",
        f"Eventos con spans obligatorios faltantes: `{engineering_report['summary']['events_missing_required_spans']}`.",
        "",
        "## Impacto",
        "",
    ]
    if monitoring_report:
        lines.append(f"El gate operativo global queda en `{monitoring_report['status']}`. La ventana que requiere investigacion es `2026-06-08`, porque combina drift, latencia, perdida operativa y trazabilidad incompleta.")
    else:
        lines.append("El impacto debe completarse con el reporte de monitorizacion.")

    lines.extend([
        "",
        "## Timeline técnico",
        "",
        "| Paso | Evidencia |",
        "|---|---|",
        "| Deteccion | `monitor_dataops.py` genera alertas y scorecard. |",
        "| Trazabilidad | `inspect_pipeline_engineering.py` revisa spans, orden, duracion e idempotencia. |",
        "| Diagnóstico | Se cruzan slices críticos con eventos y trazas lentas o incompletas. |",
        "| Accion | Se actualiza contrato, runbook o pipeline y se repite la ventana. |",
        "",
        "## Señales técnicas",
        "",
        "| Evento | Ventana | Problema |",
        "|---|---|---|",
    ])
    for flag in engineering_report["flags"][:12]:
        event_id = flag.get("event_id", "pipeline")
        window = ""
        for check in engineering_report["event_checks"]:
            if check["event_id"] == event_id:
                window = check["window"]
                break
        problem = flag["kind"]
        if "span_name" in flag:
            problem += f": {flag['span_name']}"
        lines.append(f"| `{event_id}` | `{window}` | `{problem}` |")

    lines.extend([
        "",
        "## Causa probable",
        "",
        "La ventana combina un cambio fuerte de distribución con una versión de pipeline que pierde trazabilidad en al menos un evento y presenta spans de scoring lentos. No se concluye que el modelo sea el unico problema: también fallan operacion, cobertura y observabilidad.",
        "",
        "## Acciones correctivas",
        "",
        "1. Hacer `trace_id` obligatorio antes de emitir decisiones.",
        "2. Anadir test de contrato para spans `ingest`, `validate`, `score`, `decide` y `emit`.",
        "3. Revisar latencia de `score` en `pipe-1.4.2`.",
        "4. Repetir la ventana en modo replay antes de aumentar automatización.",
        "5. Mantener `2026-06-08` fuera de reentrenamiento hasta cerrar el gate.",
        "",
        "## Criterio de cierre",
        "",
        "El incidente se cierra cuando la misma ventana reprocesada tiene trazas completas, spans dentro de SLO o excepción documentada, slices críticos revisados y scorecard sin `block`.",
    ])
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--events", type=Path, default=DEFAULT_EVENTS)
    parser.add_argument("--spans", type=Path, default=DEFAULT_SPANS)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--monitoring-report", type=Path, default=DEFAULT_MONITORING)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    events = read_csv(args.events)
    spans = read_csv(args.spans)
    contract = read_json(args.contract)
    report = inspect(events, spans, contract)
    monitoring_report = read_json(args.monitoring_report) if args.monitoring_report.exists() else None

    if args.write:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        write_json(args.output_dir / "trace_correlation_report.json", report)
        write_csv(args.output_dir / "trace_scorecard.csv", report["event_checks"])
        (args.output_dir / "incident_postmortem.md").write_text(render_postmortem(report, monitoring_report), encoding="utf-8")
    else:
        print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
