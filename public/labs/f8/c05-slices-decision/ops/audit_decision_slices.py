#!/usr/bin/env python3
import argparse
import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = ROOT / "data" / "decision_predictions.csv"
DEFAULT_POLICY = ROOT / "contracts" / "slice_decision_policy.json"
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


def pct(value):
    return round(value, 4)


def as_float(value):
    return float(str(value).replace(",", "."))


def as_int(value):
    return int(float(value))


def decide(score, policy):
    high = policy["thresholds"]["positive_if_score_gte"]
    low = policy["thresholds"]["negative_if_score_lt"]
    labels = policy["decision_labels"]
    if score >= high:
        return labels["positive"]
    if score < low:
        return labels["negative"]
    return labels["review"]


def wilson_interval(successes, n, z=1.96):
    if n == 0:
        return [None, None]
    p = successes / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    margin = z * math.sqrt((p * (1 - p) + z * z / (4 * n)) / n) / denom
    return [pct(max(0, centre - margin)), pct(min(1, centre + margin))]


def prepare_rows(rows, policy):
    result = []
    for row in rows:
        score = as_float(row[policy["score_field"]])
        truth = as_int(row[policy["label_field"]])
        decision = decide(score, policy)
        enriched = dict(row)
        enriched["score"] = score
        enriched["true_priority"] = truth
        enriched["latency_ms"] = as_float(row["latency_ms"])
        enriched["decision"] = decision
        result.append(enriched)
    return result


def metrics_for(rows, policy, slice_id="overall", field=None, value=None):
    labels = policy["decision_labels"]
    positive = labels["positive"]
    negative = labels["negative"]
    review = labels["review"]
    costs = policy["costs"]

    n = len(rows)
    positives = sum(1 for row in rows if row["true_priority"] == 1)
    negatives = n - positives
    tp = sum(1 for row in rows if row["true_priority"] == 1 and row["decision"] == positive)
    fn = sum(1 for row in rows if row["true_priority"] == 1 and row["decision"] == negative)
    urgent_review = sum(1 for row in rows if row["true_priority"] == 1 and row["decision"] == review)
    fp = sum(1 for row in rows if row["true_priority"] == 0 and row["decision"] == positive)
    tn = sum(1 for row in rows if row["true_priority"] == 0 and row["decision"] == negative)
    nonurgent_review = sum(1 for row in rows if row["true_priority"] == 0 and row["decision"] == review)
    reviews = urgent_review + nonurgent_review
    automated = n - reviews
    priority_count = tp + fp

    total_cost = fn * costs["false_negative"] + fp * costs["false_positive"] + reviews * costs["review"]
    latencies = sorted(row["latency_ms"] for row in rows)
    p95_index = max(0, min(len(latencies) - 1, math.ceil(0.95 * len(latencies)) - 1)) if latencies else 0

    auto_recall = tp / positives if positives else None
    miss_rate = fn / positives if positives else None
    safety_capture = (tp + urgent_review) / positives if positives else None
    false_positive_rate = fp / negatives if negatives else None
    precision = tp / priority_count if priority_count else None

    return {
        "slice_id": slice_id,
        "field": field,
        "value": value,
        "n": n,
        "positives": positives,
        "negatives": negatives,
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
        "review": reviews,
        "automated": automated,
        "priority_rate": pct(priority_count / n) if n else None,
        "review_rate": pct(reviews / n) if n else None,
        "automation_rate": pct(automated / n) if n else None,
        "auto_recall": pct(auto_recall) if auto_recall is not None else None,
        "auto_recall_interval": wilson_interval(tp, positives) if positives else [None, None],
        "miss_rate": pct(miss_rate) if miss_rate is not None else None,
        "safety_capture": pct(safety_capture) if safety_capture is not None else None,
        "false_positive_rate": pct(false_positive_rate) if false_positive_rate is not None else None,
        "precision": pct(precision) if precision is not None else None,
        "cost_total": pct(total_cost),
        "cost_per_case": pct(total_cost / n) if n else None,
        "latency_p95_ms": latencies[p95_index] if latencies else None,
    }


def group_rows(rows, fields):
    groups = defaultdict(list)
    for row in rows:
        key = "|".join(f"{field}={row[field]}" for field in fields)
        groups[key].append(row)
    return groups


def flatten_for_csv(metrics):
    result = []
    for row in metrics:
        flat = dict(row)
        interval = flat.pop("auto_recall_interval", [None, None])
        flat["auto_recall_low"] = interval[0]
        flat["auto_recall_high"] = interval[1]
        result.append(flat)
    return result


def valid_for_metric(metric, row, policy):
    minimums = policy["minimums"]
    if row["n"] < minimums["slice_n"]:
        return False
    if metric in {"auto_recall", "miss_rate", "safety_capture"}:
        return row["positives"] >= minimums["positive_n"]
    if metric == "false_positive_rate":
        return row["negatives"] >= minimums["negative_n"]
    return True


def compute_disparities(slice_metrics, policy):
    metrics = [
        "auto_recall",
        "miss_rate",
        "false_positive_rate",
        "review_rate",
        "priority_rate",
        "cost_per_case",
    ]
    disparities = {}
    for metric in metrics:
        candidates = [
            row
            for row in slice_metrics
            if row["field"] != "overall" and row.get(metric) is not None and valid_for_metric(metric, row, policy)
        ]
        if len(candidates) < 2:
            disparities[metric] = {"status": "insufficient_slices", "count": len(candidates)}
            continue
        ordered = sorted(candidates, key=lambda row: row[metric])
        low = ordered[0]
        high = ordered[-1]
        disparities[metric] = {
            "min_slice": low["slice_id"],
            "min": low[metric],
            "max_slice": high["slice_id"],
            "max": high[metric],
            "gap": pct(high[metric] - low[metric]),
            "count": len(candidates),
        }
    return disparities


def build_flags(overall, slice_metrics, disparities, policy):
    flags = []
    minimums = policy["minimums"]
    gates = policy["gates"]

    if overall["safety_capture"] is not None and overall["safety_capture"] < gates["min_global_safety_capture"]:
        flags.append({
            "severity": "block",
            "kind": "global_safety_capture",
            "message": "La captura global de casos prioritarios queda por debajo del mínimo.",
            "value": overall["safety_capture"],
            "threshold": gates["min_global_safety_capture"],
        })
    if overall["miss_rate"] is not None and overall["miss_rate"] > gates["max_global_miss_rate"]:
        flags.append({
            "severity": "block",
            "kind": "global_miss_rate",
            "message": "La tasa global de casos prioritarios enviados a flujo normal es demasiado alta.",
            "value": overall["miss_rate"],
            "threshold": gates["max_global_miss_rate"],
        })
    if overall["latency_p95_ms"] and overall["latency_p95_ms"] > gates["max_latency_p95_ms"]:
        flags.append({
            "severity": "review",
            "kind": "latency_p95",
            "message": "La latencia p95 supera el objetivo operativo.",
            "value": overall["latency_p95_ms"],
            "threshold": gates["max_latency_p95_ms"],
        })

    disparity_gate_map = {
        "auto_recall": "max_auto_recall_gap",
        "miss_rate": "max_miss_rate_gap",
        "false_positive_rate": "max_false_positive_rate_gap",
        "review_rate": "max_review_rate_gap",
        "cost_per_case": "max_cost_per_case_gap",
    }
    for metric, gate_name in disparity_gate_map.items():
        disparity = disparities.get(metric, {})
        if "gap" in disparity and disparity["gap"] > gates[gate_name]:
            flags.append({
                "severity": "review",
                "kind": f"{metric}_gap",
                "message": f"La diferencia entre slices en {metric} supera el gate.",
                "value": disparity["gap"],
                "threshold": gates[gate_name],
                "min_slice": disparity.get("min_slice"),
                "max_slice": disparity.get("max_slice"),
            })

    for row in slice_metrics:
        if row["field"] == "overall":
            continue
        if row["n"] < minimums["slice_n"]:
            flags.append({
                "severity": "review",
                "kind": "small_slice",
                "slice_id": row["slice_id"],
                "message": "Slice con muestra insuficiente para sostener una conclusion.",
                "value": row["n"],
                "threshold": minimums["slice_n"],
            })
        if row["slice_id"] in policy["critical_slices"] and row["miss_rate"] is not None and row["miss_rate"] > 0:
            flags.append({
                "severity": "block",
                "kind": "critical_slice_miss",
                "slice_id": row["slice_id"],
                "message": "Un slice crítico contiene casos prioritarios enviados a flujo normal.",
                "value": row["miss_rate"],
                "threshold": 0,
            })

    return flags


def decide_release(flags):
    severities = {flag["severity"] for flag in flags}
    if "block" in severities:
        return "block"
    if "review" in severities:
        return "review"
    return "pass"


def render_decision(report):
    status = report["release_status"]
    lines = [
        "# Decisión de auditoria por slices",
        "",
        f"- Estado: **{status}**",
        f"- Dataset: `{report['inputs']['data_sha256'][:12]}`",
        f"- Politica: `{report['inputs']['policy_sha256'][:12]}`",
        f"- Split evaluado: `{report['policy']['evaluation_split']}`",
        f"- Umbrales: priorizar si score >= `{report['policy']['thresholds']['positive_if_score_gte']}`, normal si score < `{report['policy']['thresholds']['negative_if_score_lt']}`",
        "",
        "## Lectura",
    ]
    overall = report["overall"]
    lines.extend([
        "",
        f"La muestra evaluada tiene {overall['n']} casos, {overall['positives']} prioritarios y {overall['negatives']} no prioritarios.",
        f"La captura segura global es {overall['safety_capture']}, la tasa de perdida operativa es {overall['miss_rate']} y la tasa de revisión es {overall['review_rate']}.",
        "La media global no basta: la decisión queda determinada por los slices críticos y por las diferencias de comportamiento entre segmentos.",
        "",
        "## Principales señales",
    ])
    if report["flags"]:
        for flag in report["flags"][:10]:
            label = flag.get("slice_id", flag["kind"])
            lines.append(f"- `{flag['severity']}` · `{label}`: {flag['message']} valor `{flag.get('value')}` frente a `{flag.get('threshold')}`.")
    else:
        lines.append("- No se han detectado flags.")
    lines.extend([
        "",
        "## Recomendación",
    ])
    if status == "block":
        lines.append("No automatices está política en su forma actual. Amplia muestra en slices críticos, revisa umbrales con validation y separa la decisión automatica de los casos que necesitan revisión.")
    elif status == "review":
        lines.append("La política puede estudiarse, pero no debería aumentar automatización hasta resolver flags de muestra, disparidad o coste.")
    else:
        lines.append("La política supera los gates definidos. Aun asi, conserva el reporte y monitoriza los mismos slices en producción.")
    lines.extend([
        "",
        "## Entregables",
        "",
        "- `slice_audit_report.json` para maquina.",
        "- `slice_metrics.csv` para analisis.",
        "- `slice_audit_card.md` para documentación.",
    ])
    return "\n".join(lines) + "\n"


def render_card(report):
    lines = [
        "# Slice audit card",
        "",
        f"- Estado: **{report['release_status']}**",
        f"- Unidad evaluada: `{report['unit']}`",
        f"- Campos auditados: `{', '.join(report['policy']['audit_fields'])}`",
        f"- Campos usados solo para auditoria: `{', '.join(report['policy']['fields_not_for_model'])}`",
        f"- Slices críticos: `{', '.join(report['policy']['critical_slices'])}`",
        "",
        "## Uso previsto",
        "",
        "Auditar una política de triaje antes de permitir más automatización.",
        "",
        "## Límites",
        "",
        "El reporte no demuestra justicia universal. Mide el comportamiento de está muestra, con estos campos, estos umbrales y este contrato.",
        "",
        "## Próxima acción",
        "",
    ]
    if report["release_status"] == "block":
        lines.append("Recolectar más datos en slices críticos y volver a evaluar con umbrales congelados desde validation.")
    else:
        lines.append("Revisar flags, documentar excepciones y conectar estos mismos slices con monitorizacion.")
    return "\n".join(lines) + "\n"


def build_report(data_path, policy_path):
    raw_rows = read_csv(data_path)
    policy = read_json(policy_path)
    rows = prepare_rows(raw_rows, policy)
    eval_rows = [row for row in rows if row["split"] == policy["evaluation_split"]]
    if not eval_rows:
        raise ValueError("No rows found for evaluation split")

    overall = metrics_for(eval_rows, policy)
    slice_metrics = []
    for field in policy["audit_fields"]:
        for value, grouped in sorted(group_rows(eval_rows, [field]).items()):
            clean_value = value.split("=", 1)[1]
            slice_metrics.append(metrics_for(grouped, policy, value, field, clean_value))
    for fields in policy["intersectional_slices"]:
        for slice_id, grouped in sorted(group_rows(eval_rows, fields).items()):
            slice_metrics.append(metrics_for(grouped, policy, slice_id, "+".join(fields), slice_id))

    disparities = compute_disparities(slice_metrics, policy)
    flags = build_flags(overall, slice_metrics, disparities, policy)
    release_status = decide_release(flags)

    return {
        "unit": "decision_policy_on_test_predictions",
        "release_status": release_status,
        "inputs": {
            "data_path": str(data_path.relative_to(ROOT)),
            "policy_path": str(policy_path.relative_to(ROOT)),
            "data_sha256": sha256_file(data_path),
            "policy_sha256": sha256_file(policy_path),
        },
        "policy": policy,
        "overall": overall,
        "slice_metrics": slice_metrics,
        "disparities": disparities,
        "flags": flags,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    report = build_report(args.data, args.policy)
    if args.write:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        write_json(args.output_dir / "slice_audit_report.json", report)
        write_csv(
            args.output_dir / "slice_metrics.csv",
            [
                "slice_id",
                "field",
                "value",
                "n",
                "positives",
                "negatives",
                "tp",
                "fp",
                "fn",
                "tn",
                "review",
                "automated",
                "priority_rate",
                "review_rate",
                "automation_rate",
                "auto_recall",
                "auto_recall_low",
                "auto_recall_high",
                "miss_rate",
                "safety_capture",
                "false_positive_rate",
                "precision",
                "cost_total",
                "cost_per_case",
                "latency_p95_ms",
            ],
            flatten_for_csv([report["overall"]] + report["slice_metrics"]),
        )
        (args.output_dir / "slice_decision.md").write_text(render_decision(report), encoding="utf-8")
        (args.output_dir / "slice_audit_card.md").write_text(render_card(report), encoding="utf-8")
    else:
        print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
