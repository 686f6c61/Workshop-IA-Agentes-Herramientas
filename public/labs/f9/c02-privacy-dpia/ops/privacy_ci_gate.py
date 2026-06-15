#!/usr/bin/env python3
import argparse
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "contracts" / "privacy_policy.json"
OUTPUT = ROOT / "output"
INVENTORY = OUTPUT / "data_flow_inventory.json"
TRACES = OUTPUT / "redacted_trace_sample.jsonl"
RETENTION = OUTPUT / "retention_plan.csv"
GATE_JSON = OUTPUT / "ci_privacy_gate.json"
GATE_MD = OUTPUT / "ci_privacy_gate.md"

EMAIL_RE = re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(?:(?:\+34\s*)?)\b(?:\d[\s-]?){9}\b")
DNI_RE = re.compile(r"\b\d{8}[A-Z]\b")


def load_json(path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_jsonl(path):
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for index, line in enumerate(handle, start=1):
            line = line.strip()
            if line:
                rows.append((index, json.loads(line)))
    return rows


def load_csv(path):
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def text_has_identifier(value):
    if not isinstance(value, str):
        return False
    return bool(EMAIL_RE.search(value) or PHONE_RE.search(value) or DNI_RE.search(value))


def collect_findings(policy, inventory, traces, retention_rows):
    findings = []
    ci = policy["ci_rules"]
    flows = inventory["flows"]
    release = inventory["release"]

    for line_number, trace in traces:
        for key in ci["forbidden_trace_keys"]:
            if key in trace:
                findings.append({
                    "severity": "fail",
                    "check": "trace_forbidden_key",
                    "where": f"redacted_trace_sample.jsonl:{line_number}",
                    "message": f"la traza conserva la clave prohibida `{key}`",
                })
        for key in ci["required_trace_keys"]:
            if key not in trace:
                findings.append({
                    "severity": "fail",
                    "check": "trace_required_key",
                    "where": f"redacted_trace_sample.jsonl:{line_number}",
                    "message": f"la traza no conserva la clave operativa `{key}`",
                })
        for key, value in trace.items():
            if text_has_identifier(value):
                findings.append({
                    "severity": "fail",
                    "check": "trace_identifier",
                    "where": f"redacted_trace_sample.jsonl:{line_number}.{key}",
                    "message": "la traza redactada todavía contiene correo, teléfono o identificador directo",
                })

    if ci["fail_if_retention_action_reduce"]:
        for row in retention_rows:
            if row["action"] == "reducir":
                findings.append({
                    "severity": "fail",
                    "check": "retention_too_long",
                    "where": f"retention_plan.csv:{row['flow_id']}",
                    "message": f"retención {row['retention_days']} días supera el valor esperado {row['default_days']} para `{row['memory_type']}`",
                })

    for flow in flows:
        if flow["privacy_band"] == "alto" and not flow["owner"]:
            findings.append({
                "severity": "fail",
                "check": "high_flow_without_owner",
                "where": flow["flow_id"],
                "message": "flujo alto sin owner",
            })
        if ci["fail_if_dpia_flow_without_evidence"] and flow["needs_dpia_precheck"] and not flow["evidence"]:
            findings.append({
                "severity": "fail",
                "check": "dpia_without_evidence",
                "where": flow["flow_id"],
                "message": "flujo con señal EIPD/DPIA sin evidencia declarada",
            })
        if ci["fail_if_training_personal_data"] and flow["model_training"] and flow["privacy_factors"]["criticality"] >= 4:
            findings.append({
                "severity": "fail",
                "check": "training_personal_data",
                "where": flow["flow_id"],
                "message": "uso de datos personales para entrenamiento o ajuste sin decisión específica cerrada",
            })

    if release["decision"] == "revisar_antes_de_publicar":
        findings.append({
            "severity": "fail",
            "check": "release_gate",
            "where": "privacy_release_gate.md",
            "message": "el gate de privacidad indica revisar antes de publicar",
        })

    return findings


def render_md(report):
    lines = [
        "# Gate CI de privacidad",
        "",
        f"Estado: `{report['status']}`",
        "",
        "Este gate comprueba que la privacidad no queda como intención editorial: revisa trazas redactadas, retención, flujos altos, señales EIPD/DPIA y entrenamiento con datos personales.",
        "",
        "## Hallazgos",
        "",
    ]
    if not report["findings"]:
        lines.append("- Sin hallazgos bloqueantes.")
    else:
        lines.extend([
            "| Severidad | Check | Dónde | Mensaje |",
            "|---|---|---|---|",
        ])
        for item in report["findings"]:
            lines.append(f"| {item['severity']} | `{item['check']}` | `{item['where']}` | {item['message']} |")
    lines.extend([
        "",
        "## Cómo convertirlo en CI real",
        "",
        "1. Genera el paquete con `python3 ops/build_privacy_pack.py --write`.",
        "2. Ejecuta `python3 ops/privacy_ci_gate.py --write --fail-on-blocker` en tu pipeline.",
        "3. Falla el release si el estado es `fail`.",
        "",
    ])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="escribe output/ci_privacy_gate.*")
    parser.add_argument("--fail-on-blocker", action="store_true", help="devuelve código 1 si hay hallazgos bloqueantes")
    args = parser.parse_args()

    policy = load_json(POLICY)
    inventory = load_json(INVENTORY)
    traces = load_jsonl(TRACES)
    retention_rows = load_csv(RETENTION)
    findings = collect_findings(policy, inventory, traces, retention_rows)
    report = {
        "status": "fail" if findings else "pass",
        "findings": findings,
        "checked_files": [
            str(INVENTORY.relative_to(ROOT)),
            str(TRACES.relative_to(ROOT)),
            str(RETENTION.relative_to(ROOT)),
        ],
    }

    if args.write:
        OUTPUT.mkdir(parents=True, exist_ok=True)
        GATE_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        GATE_MD.write_text(render_md(report), encoding="utf-8")

    print(f"estado: {report['status']}")
    print(f"hallazgos: {len(findings)}")

    if args.fail_on_blocker and findings:
        sys.exit(1)


if __name__ == "__main__":
    main()
