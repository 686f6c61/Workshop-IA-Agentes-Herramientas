import argparse
import json
import sys
from pathlib import Path


def read_jsonl(path):
    rows = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def write_json(path, payload):
    Path(path).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def metric_status(event):
    value = event["value"]
    slo = event["slo"]
    if event["metric"] in {"latency_p95_ms", "review_queue_age_p95_minutes"}:
        return "breach" if value > slo else "pass"
    return "breach" if value < slo else "pass"


def mitigation_for(metric):
    mapping = {
        "latency_p95_ms": "mover ruta crítica a provider_b y reducir canary",
        "citation_acceptance_rate": "volver al índice estable y añadir caso a regresión RAG",
        "review_queue_age_p95_minutes": "activar cola de solo revisión crítica y ampliar owner temporal",
    }
    return mapping.get(metric, "abrir investigacion con owner")


def build_report(events):
    metrics = [event for event in events if event.get("type") == "metric"]
    traces = [event for event in events if event.get("type") == "trace"]
    changes = [event for event in events if event.get("type") == "change"]
    findings = []
    for event in metrics:
        status = metric_status(event)
        findings.append({
            "metric": event["metric"],
            "value": event["value"],
            "slo": event["slo"],
            "status": status,
            "mitigation": mitigation_for(event["metric"]) if status == "breach" else "mantener vigilancia",
        })

    breach_count = sum(item["status"] == "breach" for item in findings)
    trace_attrs_ok = all(all(key in trace for key in ["trace_id", "run_id", "model_id", "prompt_version", "route_id", "index_version", "release_id"]) for trace in traces)
    status = "recovered" if breach_count == 0 and trace_attrs_ok else "degraded_controlled" if trace_attrs_ok else "not_reconstructable"

    return {
        "status": status,
        "breach_count": breach_count,
        "trace_attrs_ok": trace_attrs_ok,
        "changes": changes,
        "findings": findings,
        "evidence_to_keep": [
            "métricas por release y ruta",
            "trace_id con modelo, prompt, ruta e índice",
            "muestra de respuestas con citas",
            "decisión de canary y rollback",
            "caso de regresión generado"
        ],
    }


def render_decision(report):
    lines = [
        "# Decisión de continuidad",
        "",
        f"Estado: **{report['status']}**.",
        "",
        "## Síntomas",
        "",
        "| Métrica | Valor | SLO | Estado | Mitigación |",
        "|---|---:|---:|---|---|",
    ]
    for item in report["findings"]:
        lines.append(f"| `{item['metric']}` | {item['value']} | {item['slo']} | {item['status']} | {item['mitigation']} |")
    lines.extend([
        "",
        "## Orden de actuación",
        "",
        "1. Reducir canary para limitar exposición.",
        "2. Cambiar ruta crítica a fallback si la latencia queda fuera de SLO.",
        "3. Volver al índice estable si cae aceptación de citas.",
        "4. Proteger cola humana con prioridades explícitas.",
        "5. Convertir el caso en regresión antes de cerrar.",
    ])
    return "\n".join(lines) + "\n"


def render_postmortem(report):
    lines = [
        "# Postmortem técnico",
        "",
        "## Resumen",
        "",
        f"Estado final del drill: `{report['status']}`.",
        "",
        "## Evidencia preservada",
        "",
    ]
    for item in report["evidence_to_keep"]:
        lines.append(f"- {item}.")
    lines.extend([
        "",
        "## Acciones",
        "",
        "1. Añadir regresión RAG para la pregunta afectada.",
        "2. Revisar dashboard de cola por release.",
        "3. Ensayar rollback de índice en ventana controlada.",
    ])
    return "\n".join(lines) + "\n"


def regression_case(report):
    return {
        "case_id": "reg_support_rag_continuity_2026_06_07",
        "source": "continuity_drill",
        "must_pass": {
            "latency_p95_ms_max": 4200,
            "citation_acceptance_rate_min": 0.9,
            "review_queue_age_p95_minutes_max": 30,
            "trace_attrs_required": True
        },
        "observed_findings": report["findings"],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--events", default="data/continuity_events.jsonl")
    parser.add_argument("--output-dir", default="output")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--fail-on-not-recovered", action="store_true")
    args = parser.parse_args()

    report = build_report(read_jsonl(args.events))
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if args.write:
        out = Path(args.output_dir)
        out.mkdir(parents=True, exist_ok=True)
        write_json(out / "continuity_report.json", report)
        write_json(out / "ci_continuity_gate.json", {
            "status": report["status"],
            "breach_count": report["breach_count"],
            "trace_attrs_ok": report["trace_attrs_ok"],
        })
        write_json(out / "regression_case.json", regression_case(report))
        (out / "continuity_decision.md").write_text(render_decision(report), encoding="utf-8")
        (out / "postmortem.md").write_text(render_postmortem(report), encoding="utf-8")
    if args.fail_on_not_recovered and report["status"] != "recovered":
        sys.exit(2)


if __name__ == "__main__":
    main()
