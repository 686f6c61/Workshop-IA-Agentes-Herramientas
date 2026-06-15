import argparse
import csv
import hashlib
import json
import math
from pathlib import Path


def sigmoid(x):
    return 1 / (1 + math.exp(-x))


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_rows(path):
    with Path(path).open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    parsed = []
    for row in rows:
        item = {"case_id": row["case_id"], "label": int(row["label"])}
        for key, value in row.items():
            if key not in {"case_id", "label"}:
                item[key] = float(value)
        parsed.append(item)
    return parsed


def logit(row, model):
    total = model["intercept"]
    for feature, weight in model["weights"].items():
        total += weight * row[feature]
    return total


def predict(row, model, threshold):
    score = sigmoid(logit(row, model))
    return {
        "score": score,
        "prediction": 1 if score >= threshold else 0,
    }


def predict_with_feature_subset(row, model, threshold, keep_features):
    modified = dict(row)
    for feature in model["weights"]:
        if feature not in keep_features:
            modified[feature] = 0.0
    return predict(modified, model, threshold)


def local_explanation(row, model, threshold):
    base = model["intercept"]
    contributions = []
    for feature, weight in model["weights"].items():
        value = row[feature]
        contribution = weight * value
        contributions.append({
            "feature": feature,
            "value": value,
            "weight": weight,
            "contribution_logit": contribution,
            "direction": "sube" if contribution > 0 else "baja" if contribution < 0 else "neutral",
        })
    contributions.sort(key=lambda item: abs(item["contribution_logit"]), reverse=True)
    pred = predict(row, model, threshold)
    return {
        "case_id": row["case_id"],
        "label": row["label"],
        "intercept": base,
        "logit": logit(row, model),
        "score": round(pred["score"], 6),
        "prediction": pred["prediction"],
        "top_features": contributions,
    }


def deletion_test(row, model, threshold):
    original = predict(row, model, threshold)
    explanation = local_explanation(row, model, threshold)
    top = explanation["top_features"][0]
    modified = dict(row)
    modified[top["feature"]] = 0.0
    after = predict(modified, model, threshold)
    return {
        "case_id": row["case_id"],
        "removed_feature": top["feature"],
        "original_score": round(original["score"], 6),
        "after_score": round(after["score"], 6),
        "score_drop": round(original["score"] - after["score"], 6),
        "prediction_changed": original["prediction"] != after["prediction"],
    }


def top_k_fidelity(row, model, threshold, k=2):
    original = predict(row, model, threshold)
    explanation = local_explanation(row, model, threshold)
    top_features = [item["feature"] for item in explanation["top_features"][:k]]

    without_top = dict(row)
    for feature in top_features:
        without_top[feature] = 0.0
    without_top_pred = predict(without_top, model, threshold)
    only_top_pred = predict_with_feature_subset(row, model, threshold, set(top_features))

    return {
        "case_id": row["case_id"],
        "k": k,
        "top_features": top_features,
        "original_score": round(original["score"], 6),
        "without_top_score": round(without_top_pred["score"], 6),
        "only_top_score": round(only_top_pred["score"], 6),
        "comprehensiveness": round(original["score"] - without_top_pred["score"], 6),
        "sufficiency_delta": round(abs(original["score"] - only_top_pred["score"]), 6),
    }


def accuracy(rows, model, threshold):
    correct = 0
    for row in rows:
        correct += 1 if predict(row, model, threshold)["prediction"] == row["label"] else 0
    return correct / len(rows)


def permutation_importance(rows, model, threshold):
    base = accuracy(rows, model, threshold)
    results = []
    for feature in model["weights"]:
        values = [row[feature] for row in rows]
        shifted = values[1:] + values[:1]
        perturbed = []
        for row, value in zip(rows, shifted):
            copy = dict(row)
            copy[feature] = value
            perturbed.append(copy)
        score = accuracy(perturbed, model, threshold)
        results.append({
            "feature": feature,
            "baseline_accuracy": round(base, 4),
            "permuted_accuracy": round(score, 4),
            "drop": round(base - score, 4),
        })
    results.sort(key=lambda item: item["drop"], reverse=True)
    return results


def top_feature_distribution(rows, model, threshold):
    counts = {}
    for row in rows:
        top = local_explanation(row, model, threshold)["top_features"][0]["feature"]
        counts[top] = counts.get(top, 0) + 1
    total = len(rows)
    return [
        {"feature": feature, "count": count, "share": round(count / total, 4)}
        for feature, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    ]


def pearson(xs, ys):
    n = len(xs)
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    num = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    den_x = math.sqrt(sum((x - mean_x) ** 2 for x in xs))
    den_y = math.sqrt(sum((y - mean_y) ** 2 for y in ys))
    if den_x == 0 or den_y == 0:
        return 0.0
    return num / (den_x * den_y)


def feature_correlation_report(rows, model):
    features = list(model["weights"])
    pairs = []
    for i, first in enumerate(features):
        for second in features[i + 1:]:
            corr = pearson([row[first] for row in rows], [row[second] for row in rows])
            pairs.append({
                "feature_a": first,
                "feature_b": second,
                "correlation": round(corr, 4),
                "abs_correlation": round(abs(corr), 4),
            })
    pairs.sort(key=lambda item: item["abs_correlation"], reverse=True)
    return pairs


def perturb_row(row, feature_ranges):
    variants = []
    for feature, bounds in feature_ranges.items():
        lo, hi = bounds
        value = row[feature]
        if hi <= 1:
            continue
        delta = max(1.0, (hi - lo) * 0.05)
        for sign in [-1, 1]:
            copy = dict(row)
            copy[feature] = min(hi, max(lo, value + sign * delta))
            variants.append(copy)
    return variants


def stability(rows, model, threshold, feature_ranges):
    scores = []
    for row in rows:
        original_top = local_explanation(row, model, threshold)["top_features"][0]["feature"]
        variants = perturb_row(row, feature_ranges)
        if not variants:
            continue
        same = 0
        for variant in variants:
            variant_top = local_explanation(variant, model, threshold)["top_features"][0]["feature"]
            same += 1 if variant_top == original_top else 0
        scores.append(same / len(variants))
    return {
        "cases": len(scores),
        "top1_agreement": round(sum(scores) / len(scores), 4) if scores else None,
    }


def counterfactual(row, model, threshold, actionable_features):
    original = predict(row, model, threshold)
    target_prediction = 0 if original["prediction"] == 1 else 1
    candidates = []
    for feature, spec in actionable_features.items():
        modified = dict(row)
        modified[feature] = float(spec["target"])
        after = predict(modified, model, threshold)
        candidates.append({
            "changes": [{feature: spec["target"]}],
            "description": spec["description"],
            "after_score": round(after["score"], 6),
            "after_prediction": after["prediction"],
            "reaches_target": after["prediction"] == target_prediction,
        })
    # Pares de cambios accionables.
    features = list(actionable_features)
    for i, first in enumerate(features):
        for second in features[i + 1:]:
            modified = dict(row)
            modified[first] = float(actionable_features[first]["target"])
            modified[second] = float(actionable_features[second]["target"])
            after = predict(modified, model, threshold)
            candidates.append({
                "changes": [{first: actionable_features[first]["target"]}, {second: actionable_features[second]["target"]}],
                "description": f"{actionable_features[first]['description']} + {actionable_features[second]['description']}",
                "after_score": round(after["score"], 6),
                "after_prediction": after["prediction"],
                "reaches_target": after["prediction"] == target_prediction,
            })
    candidates.sort(key=lambda item: (not item["reaches_target"], len(item["changes"]), item["after_score"]))
    return {
        "case_id": row["case_id"],
        "original_prediction": original["prediction"],
        "original_score": round(original["score"], 6),
        "target_prediction": target_prediction,
        "best": candidates[0] if candidates else None,
        "candidates": candidates,
    }


def audit_checks(report, policy):
    checks = []
    max_drop = max(item["score_drop"] for item in report["deletion_tests"])
    checks.append({
        "name": "deletion_top_feature_drop",
        "passes": max_drop >= policy["audit_thresholds"]["min_top_feature_drop"],
        "detail": {"max_drop": max_drop, "minimum": policy["audit_thresholds"]["min_top_feature_drop"]},
    })
    max_perm = max(item["drop"] for item in report["permutation_importance"])
    checks.append({
        "name": "permutation_importance_drop",
        "passes": max_perm >= policy["audit_thresholds"]["min_permutation_drop"],
        "detail": {"max_drop": max_perm, "minimum": policy["audit_thresholds"]["min_permutation_drop"]},
    })
    checks.append({
        "name": "stability_top1",
        "passes": report["stability"]["top1_agreement"] >= policy["audit_thresholds"]["min_stability_top1"],
        "detail": {"top1_agreement": report["stability"]["top1_agreement"], "minimum": policy["audit_thresholds"]["min_stability_top1"]},
    })
    checks.append({
        "name": "counterfactual_available",
        "passes": any(item["best"] and item["best"]["reaches_target"] for item in report["counterfactuals"]),
        "detail": "al menos un caso tiene contrafactual accionable que cambia la decisión",
    })
    avg_comprehensiveness = sum(item["comprehensiveness"] for item in report["top_k_fidelity"]) / len(report["top_k_fidelity"])
    checks.append({
        "name": "comprehensiveness_top2",
        "passes": avg_comprehensiveness >= policy["audit_thresholds"]["min_comprehensiveness_top2"],
        "detail": {
            "average": round(avg_comprehensiveness, 6),
            "minimum": policy["audit_thresholds"]["min_comprehensiveness_top2"],
        },
    })
    avg_sufficiency = sum(item["sufficiency_delta"] for item in report["top_k_fidelity"]) / len(report["top_k_fidelity"])
    checks.append({
        "name": "sufficiency_top2",
        "passes": avg_sufficiency <= policy["audit_thresholds"]["max_sufficiency_delta_top2"],
        "detail": {
            "average": round(avg_sufficiency, 6),
            "maximum": policy["audit_thresholds"]["max_sufficiency_delta_top2"],
        },
    })
    max_corr = report["feature_correlation_report"][0]["abs_correlation"] if report["feature_correlation_report"] else 0.0
    checks.append({
        "name": "feature_proxy_scan",
        "passes": max_corr <= policy["audit_thresholds"]["max_abs_feature_correlation"],
        "detail": {
            "max_abs_correlation": max_corr,
            "maximum": policy["audit_thresholds"]["max_abs_feature_correlation"],
            "top_pair": report["feature_correlation_report"][0] if report["feature_correlation_report"] else None,
        },
    })
    return checks


def build_explanation_contract(report, policy):
    sample = report["local_explanations"][0]
    return {
        "model_version": policy["model_version"],
        "explanation_policy_version": policy["explanation_policy_version"],
        "owner": policy["owner"],
        "purpose": policy["explanation_contract"]["purpose"],
        "allowed_consumers": policy["explanation_contract"]["allowed_consumers"],
        "not_for": policy["explanation_contract"]["not_for"],
        "required_fields": policy["explanation_contract"]["required_fields"],
        "logging_required": policy["production_monitoring"]["log_explanations"],
        "monitoring": policy["production_monitoring"],
        "data_hash_sha256": report["data_hash_sha256"],
        "policy_hash_sha256": report["policy_hash_sha256"],
        "sample_explanation_event": {
            "case_id": sample["case_id"],
            "model_version": policy["model_version"],
            "score": sample["score"],
            "prediction": sample["prediction"],
            "top_features": sample["top_features"][:3],
            "data_hash_sha256": report["data_hash_sha256"],
            "policy_hash_sha256": report["policy_hash_sha256"],
        },
    }


def build_ci_gate(report):
    return {
        "gate": "pass" if all(check["passes"] for check in report["audit_checks"]) else "fail",
        "checks": report["audit_checks"],
        "top_feature_distribution": report["top_feature_distribution"],
        "recommendation": "permitir uso interno con monitorización" if all(check["passes"] for check in report["audit_checks"]) else "bloquear o revisar explicación",
    }


def render_model_card(report, policy, data_hash):
    lines = [
        "# Fragmento de model card: interpretabilidad",
        "",
        f"Modelo: `{policy['model_version']}`.",
        f"Política de explicación: `{policy['explanation_policy_version']}`.",
        f"Dataset hash: `{data_hash}`.",
        "",
        "## Uso previsto",
        "",
        "Priorizar tickets académicos para revisión operativa. No debe usarse como decisión final sin revisar política, datos y umbral.",
        "",
        "## Explicaciones disponibles",
        "",
        "- Contribuciones locales por feature para cada caso.",
        "- Importancia global por permutación.",
        "- Pruebas de borrado de feature superior.",
        "- Suficiencia y comprehensiveness de las dos features principales.",
        "- Estabilidad ante pequeñas perturbaciones numéricas.",
        "- Contrafactuales accionables limitados a campos modificables.",
        "- Escaneo simple de correlaciones para detectar proxies obvios.",
        "",
        "## Resultado de auditoría",
        "",
    ]
    for check in report["audit_checks"]:
        state = "pasa" if check["passes"] else "no pasa"
        lines.append(f"- `{check['name']}`: {state}.")
    return "\n".join(lines) + "\n"


def render_decision(report):
    gate = "defendible" if all(check["passes"] for check in report["audit_checks"]) else "requiere_revision"
    first = report["local_explanations"][0]
    top3 = first["top_features"][:3]
    top_global = report["permutation_importance"][0]
    best_counterfactual = next((item for item in report["counterfactuals"] if item["best"] and item["best"]["reaches_target"]), None)
    lines = [
        "# Decisión de interpretabilidad",
        "",
        f"Estado: **{gate}**.",
        "",
        "## Lectura ejecutiva",
        "",
        "La explicación local es defendible para diagnóstico interno porque no se acepta por intuición: se contrasta con borrado de features, importancia global, estabilidad, contrafactuales accionables, suficiencia y contrato de uso.",
        "El contrato limita su consumo a ingeniería, soporte N2 y producto. No es una decisión final, no es una comunicación automática a usuario y no sustituye revisión operativa.",
        "",
        "## Caso de referencia",
        "",
        f"El caso `{first['case_id']}` tiene score `{first['score']}` y predicción `{first['prediction']}`.",
        "",
        "| Feature | Valor | Peso | Contribución logit | Dirección |",
        "|---|---:|---:|---:|---|",
    ]
    for item in top3:
        lines.append(f"| `{item['feature']}` | `{item['value']}` | `{item['weight']}` | `{round(item['contribution_logit'], 6)}` | {item['direction']} |")
    lines.extend([
        "",
        "## Lectura global",
        "",
        f"La feature con mayor caída por permutación es `{top_global['feature']}` con drop `{top_global['drop']}`. Eso no prueba causalidad, pero sí indica que el modelo depende de esa señal para mantener rendimiento.",
        f"La estabilidad top-1 es `{report['stability']['top1_agreement']}`. Si este valor fuera bajo, la explicación cambiaría demasiado ante perturbaciones pequeñas y no sería buen soporte para una release.",
        "",
        "## Contrafactual útil",
        "",
    ])
    if best_counterfactual:
        lines.extend([
            f"El caso `{best_counterfactual['case_id']}` tiene un cambio accionable que modifica la decisión:",
            "",
            f"- score original: `{best_counterfactual['original_score']}`.",
            f"- predicción original: `{best_counterfactual['original_prediction']}`.",
            f"- cambio propuesto: `{best_counterfactual['best']['description']}`.",
            f"- score después del cambio: `{best_counterfactual['best']['after_score']}`.",
            f"- predicción después del cambio: `{best_counterfactual['best']['after_prediction']}`.",
        ])
    else:
        lines.append("No aparece ningún contrafactual accionable que cambie la decisión. En una release real esto exigiría revisión.")
    lines.extend([
        "",
        "## Checks",
        "",
        "| Check | Estado | Lectura |",
        "|---|---|---|",
    ]
    )
    for check in report["audit_checks"]:
        state = "pasa" if check["passes"] else "no pasa"
        lines.append(f"| `{check['name']}` | {state} | `{check['detail']}` |")
    lines.extend([
        "",
        "## Decisión profesional",
        "",
        "Usaría esta explicación para depurar, revisar casos y preparar un fragmento de model card. No la usaría como mensaje automático a usuario final ni como justificación única de una acción.",
        "",
        "## Siguiente iteración",
        "",
        "1. Monitorizar distribución de top features en producción.",
        "2. Revisar la pareja de features más correlacionada si se acerca al máximo permitido.",
        "3. Mantener el contrato de explicación versionado junto al modelo y los datos.",
        "4. Convertir estos checks en gate de CI para que una release no cambie explicaciones sin evidencia.",
    ])
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data/ticket_features.csv")
    parser.add_argument("--policy", default="policies/interpretability_policy.json")
    parser.add_argument("--output", default="output/interpretability_report.json")
    parser.add_argument("--card-output", default="output/model_card_interpretability.md")
    parser.add_argument("--decision-output", default="output/interpretability_decision.md")
    parser.add_argument("--contract-output", default="output/explanation_contract.json")
    parser.add_argument("--gate-output", default="output/ci_explanation_gate.json")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    rows = load_rows(args.data)
    policy = json.loads(Path(args.policy).read_text(encoding="utf-8"))
    model = policy["model"]
    threshold = policy["threshold"]

    report = {
        "model_version": policy["model_version"],
        "threshold": threshold,
        "accuracy": round(accuracy(rows, model, threshold), 4),
        "local_explanations": [local_explanation(row, model, threshold) for row in rows],
        "deletion_tests": [deletion_test(row, model, threshold) for row in rows],
        "top_k_fidelity": [top_k_fidelity(row, model, threshold, k=2) for row in rows],
        "permutation_importance": permutation_importance(rows, model, threshold),
        "top_feature_distribution": top_feature_distribution(rows, model, threshold),
        "feature_correlation_report": feature_correlation_report(rows, model),
        "stability": stability(rows, model, threshold, policy["feature_ranges"]),
        "counterfactuals": [counterfactual(row, model, threshold, policy["actionable_features"]) for row in rows],
        "data_hash_sha256": sha256_file(args.data),
        "policy_hash_sha256": sha256_file(args.policy),
    }
    report["audit_checks"] = audit_checks(report, policy)
    explanation_contract = build_explanation_contract(report, policy)
    ci_gate = build_ci_gate(report)

    rendered = json.dumps(report, indent=2, ensure_ascii=False)
    print(rendered)
    if args.write:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(rendered + "\n", encoding="utf-8")
        Path(args.card_output).write_text(render_model_card(report, policy, report["data_hash_sha256"]), encoding="utf-8")
        Path(args.decision_output).write_text(render_decision(report), encoding="utf-8")
        Path(args.contract_output).write_text(json.dumps(explanation_contract, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        Path(args.gate_output).write_text(json.dumps(ci_gate, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
