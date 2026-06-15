#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PLAN = ROOT / "contracts" / "analysis_plan.json"
DEFAULT_METRICS = ROOT / "contracts" / "metric_catalog.json"
DEFAULT_FLAG = ROOT / "contracts" / "feature_flag_contract.json"
DEFAULT_OUTPUT = ROOT / "output"


def read_json(path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def validate(plan, catalog, flag):
    metrics = {item["name"]: item for item in catalog["metrics"]}
    checks = []
    required_plan_fields = [
        "hypothesis",
        "unit",
        "population",
        "treatment",
        "control",
        "primary_metric",
        "metric_window",
        "guardrail_metrics",
        "planned_looks",
        "decision_rules",
    ]
    for field in required_plan_fields:
        checks.append({
            "check": f"plan_field:{field}",
            "status": "pass" if plan.get(field) not in (None, "", []) else "block",
            "message": f"Campo {field} presente en analysis_plan.json.",
        })

    primary = plan.get("primary_metric")
    checks.append({
        "check": "primary_metric_in_catalog",
        "status": "pass" if primary in metrics and metrics[primary]["type"] == "primary" else "block",
        "message": "La metrica primaria debe existir en metric_catalog.json y tener type=primary.",
    })

    for metric in plan.get("guardrail_metrics", []):
        checks.append({
            "check": f"guardrail_in_catalog:{metric}",
            "status": "pass" if metric in metrics and metrics[metric]["type"] == "guardrail" else "block",
            "message": "Cada guardrail del plan debe existir en el catalogo con type=guardrail.",
        })

    checks.append({
        "check": "one_primary_metric",
        "status": "pass" if plan.get("multiple_comparison_policy", {}).get("primary_metric_count") == 1 else "review",
        "message": "Debe haber una metrica primaria clara; el resto se reporta como guardrail o diagnostico.",
    })
    checks.append({
        "check": "exposure_fields",
        "status": "pass" if "exposed_at" in flag.get("required_exposure_fields", []) else "block",
        "message": "La flag debe exigir campo de exposición real.",
    })
    checks.append({
        "check": "targeting_key_matches_unit",
        "status": "pass" if flag.get("targeting_key") == plan.get("unit") else "review",
        "message": "La unidad del plan debe coincidir con el targeting_key o estar justificada.",
    })

    statuses = {item["status"] for item in checks}
    status = "block" if "block" in statuses else "review" if "review" in statuses else "pass"
    return {"status": status, "checks": checks}


def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def render(report):
    lines = [
        "# Validación de diseño experimental",
        "",
        f"Estado: **{report['status']}**.",
        "",
        "| Check | Estado | Mensaje |",
        "|---|---|---|",
    ]
    for item in report["checks"]:
        lines.append(f"| `{item['check']}` | `{item['status']}` | {item['message']} |")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--metrics", type=Path, default=DEFAULT_METRICS)
    parser.add_argument("--flag", type=Path, default=DEFAULT_FLAG)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    report = validate(read_json(args.plan), read_json(args.metrics), read_json(args.flag))
    if args.write:
        write_json(args.output_dir / "experiment_design_validation.json", report)
        (args.output_dir / "experiment_design_validation.md").write_text(render(report), encoding="utf-8")
    else:
        print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
