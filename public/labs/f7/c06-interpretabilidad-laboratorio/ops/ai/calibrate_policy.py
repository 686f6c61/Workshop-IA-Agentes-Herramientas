import argparse
import csv
import hashlib
import json
import math
import random
from pathlib import Path


def clamp(value, low=1e-6, high=1 - 1e-6):
    return min(high, max(low, value))


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_cases(path):
    with Path(path).open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    required = {"case_id", "split", "raw_score", "label", "slice"}
    missing = required - set(rows[0] if rows else [])
    if missing:
        raise ValueError(f"faltan columnas obligatorias: {sorted(missing)}")

    cases = []
    for row in rows:
        cases.append({
            **row,
            "raw_score": float(row["raw_score"]),
            "label": int(row["label"]),
        })
    return cases


def split_cases(cases, split):
    selected = [case for case in cases if case["split"] == split]
    if not selected:
        raise ValueError(f"split vacio: {split}")
    return selected


def brier(cases, score_key):
    return sum((case[score_key] - case["label"]) ** 2 for case in cases) / len(cases)


def log_loss(cases, score_key):
    total = 0.0
    for case in cases:
        p = clamp(case[score_key])
        y = case["label"]
        total += y * math.log(p) + (1 - y) * math.log(1 - p)
    return -total / len(cases)


def bin_index(score, bins):
    return min(bins - 1, int(clamp(score, 0.0, 0.999999) * bins))


def wilson_interval(successes, total, z=1.96):
    if total == 0:
        return [None, None]
    phat = successes / total
    denom = 1 + z * z / total
    center = (phat + z * z / (2 * total)) / denom
    margin = z * math.sqrt((phat * (1 - phat) + z * z / (4 * total)) / total) / denom
    return [round(max(0.0, center - margin), 4), round(min(1.0, center + margin), 4)]


def reliability(cases, score_key, bins):
    table = []
    for index in range(bins):
        lo = index / bins
        hi = (index + 1) / bins
        bucket = [case for case in cases if bin_index(case[score_key], bins) == index]
        positives = sum(case["label"] for case in bucket)
        if not bucket:
            table.append({
                "bin": index,
                "range": [round(lo, 2), round(hi, 2)],
                "count": 0,
                "confidence": None,
                "accuracy": None,
                "accuracy_wilson_95": [None, None],
                "gap": None,
            })
            continue
        confidence = sum(case[score_key] for case in bucket) / len(bucket)
        accuracy = positives / len(bucket)
        table.append({
            "bin": index,
            "range": [round(lo, 2), round(hi, 2)],
            "count": len(bucket),
            "confidence": round(confidence, 4),
            "accuracy": round(accuracy, 4),
            "accuracy_wilson_95": wilson_interval(positives, len(bucket)),
            "gap": round(abs(accuracy - confidence), 4),
        })
    return table


def ece(cases, score_key, bins):
    table = reliability(cases, score_key, bins)
    return sum(row["count"] / len(cases) * row["gap"] for row in table if row["count"])


def fit_histogram_calibrator(cases, bins):
    calibrator = []
    global_rate = sum(case["label"] for case in cases) / len(cases)
    for index in range(bins):
        bucket = [case for case in cases if bin_index(case["raw_score"], bins) == index]
        positives = sum(case["label"] for case in bucket)
        calibrated = (positives + 1) / (len(bucket) + 2) if bucket else global_rate
        calibrator.append({
            "bin": index,
            "count": len(bucket),
            "positives": positives,
            "calibrated_probability": round(calibrated, 6),
        })
    return calibrator


def apply_calibrator(cases, calibrator, bins):
    by_bin = {row["bin"]: row["calibrated_probability"] for row in calibrator}
    enriched = []
    for case in cases:
        copy = dict(case)
        copy["calibrated_score"] = by_bin[bin_index(case["raw_score"], bins)]
        enriched.append(copy)
    return enriched


def conformal_threshold(calibration_cases, alpha):
    nonconformity = []
    for case in calibration_cases:
        p = case["calibrated_score"]
        score = 1 - p if case["label"] == 1 else p
        nonconformity.append(score)
    nonconformity.sort()
    rank = min(len(nonconformity), math.ceil((len(nonconformity) + 1) * (1 - alpha)))
    return nonconformity[rank - 1]


def conformal_set(probability, q):
    labels = []
    if probability <= q:
        labels.append("normal")
    if 1 - probability <= q:
        labels.append("urgente")
    return labels or ["normal", "urgente"]


def decide(probability, low, high, q):
    labels = conformal_set(probability, q)
    if len(labels) > 1:
        return "review"
    if probability <= low:
        return "normal"
    if probability >= high:
        return "urgent"
    return "review"


def evaluate_thresholds(cases, q, policy):
    candidates = []
    grid = [round(i / 20, 2) for i in range(1, 20)]
    for low in grid:
        for high in grid:
            if low >= high:
                continue
            cost = 0.0
            auto = 0
            auto_errors = 0
            reviewed = 0
            confusion = {"tp": 0, "fp": 0, "fn": 0, "tn": 0}
            for case in cases:
                decision = decide(case["calibrated_score"], low, high, q)
                if decision == "review":
                    reviewed += 1
                    cost += policy["cost_review"]
                    continue

                auto += 1
                predicted = 1 if decision == "urgent" else 0
                actual = case["label"]
                if predicted == 1 and actual == 1:
                    confusion["tp"] += 1
                elif predicted == 1 and actual == 0:
                    confusion["fp"] += 1
                    auto_errors += 1
                    cost += policy["cost_false_positive"]
                elif predicted == 0 and actual == 1:
                    confusion["fn"] += 1
                    auto_errors += 1
                    cost += policy["cost_false_negative"]
                else:
                    confusion["tn"] += 1

            review_rate = reviewed / len(cases)
            auto_coverage = auto / len(cases)
            auto_error_rate = auto_errors / auto if auto else 0.0
            passes = (
                review_rate <= policy["max_review_rate"]
                and auto_coverage >= policy["min_auto_coverage"]
                and auto_error_rate <= policy["max_auto_error_rate"]
            )
            candidates.append({
                "low": low,
                "high": high,
                "cost": round(cost, 4),
                "review_rate": round(review_rate, 4),
                "auto_coverage": round(auto_coverage, 4),
                "auto_error_rate": round(auto_error_rate, 4),
                "auto_error_wilson_95": wilson_interval(auto_errors, auto),
                "confusion_auto": confusion,
                "passes": passes,
            })
    valid = [item for item in candidates if item["passes"]]
    valid.sort(key=lambda item: (item["cost"], item["review_rate"], -item["auto_coverage"], -item["high"], item["low"]))
    return valid[0] if valid else min(candidates, key=lambda item: item["cost"])


def prediction_if_accepted(case, q, min_confidence):
    probability = case["calibrated_score"]
    labels = conformal_set(probability, q)
    if len(labels) > 1:
        return None
    confidence = max(probability, 1 - probability)
    if confidence < min_confidence:
        return None
    return 1 if probability >= 0.5 else 0


def risk_coverage_curve(cases, q, policy):
    rows = []
    for min_confidence in [round(i / 20, 2) for i in range(10, 20)]:
        accepted = []
        total_cost = 0.0
        errors = 0
        for case in cases:
            predicted = prediction_if_accepted(case, q, min_confidence)
            if predicted is None:
                continue
            accepted.append(case)
            actual = case["label"]
            if predicted == 1 and actual == 0:
                errors += 1
                total_cost += policy["cost_false_positive"]
            elif predicted == 0 and actual == 1:
                errors += 1
                total_cost += policy["cost_false_negative"]
        coverage = len(accepted) / len(cases)
        risk = total_cost / len(accepted) if accepted else None
        rows.append({
            "min_confidence": min_confidence,
            "coverage": round(coverage, 4),
            "accepted": len(accepted),
            "errors": errors,
            "error_rate_wilson_95": wilson_interval(errors, len(accepted)),
            "risk": round(risk, 4) if risk is not None else None,
        })
    return rows


def bootstrap_metrics(cases, score_key, bins, rounds, seed):
    rng = random.Random(seed)
    brier_values = []
    ece_values = []
    for _ in range(rounds):
        sample = [cases[rng.randrange(len(cases))] for _ in range(len(cases))]
        brier_values.append(brier(sample, score_key))
        ece_values.append(ece(sample, score_key, bins))
    return {
        "rounds": rounds,
        "seed": seed,
        "brier_p05_p50_p95": percentile_summary(brier_values),
        "ece_p05_p50_p95": percentile_summary(ece_values),
    }


def percentile_summary(values):
    ordered = sorted(values)
    def pick(q):
        index = min(len(ordered) - 1, max(0, round(q * (len(ordered) - 1))))
        return round(ordered[index], 4)
    return [pick(0.05), pick(0.50), pick(0.95)]


def metrics_block(cases, score_key, bins, policy):
    return {
        "brier": round(brier(cases, score_key), 4),
        "log_loss": round(log_loss(cases, score_key), 4),
        "ece": round(ece(cases, score_key, bins), 4),
        "reliability": reliability(cases, score_key, bins),
        "bootstrap": bootstrap_metrics(
            cases,
            score_key,
            bins,
            policy["bootstrap_rounds"],
            policy["random_seed"],
        ),
    }


def slice_report(cases, score_key, bins):
    rows = []
    for name in sorted({case["slice"] for case in cases}):
        group = [case for case in cases if case["slice"] == name]
        positives = sum(case["label"] for case in group)
        rows.append({
            "slice": name,
            "count": len(group),
            "base_rate": round(positives / len(group), 4),
            "base_rate_wilson_95": wilson_interval(positives, len(group)),
            "brier": round(brier(group, score_key), 4),
            "ece": round(ece(group, score_key, bins), 4),
        })
    return rows


def base_rate(cases):
    return sum(case["label"] for case in cases) / len(cases)


def operational_checks(report, policy, calibration_cases, evaluation_cases):
    checks = []
    observed_slices = {case["slice"] for case in calibration_cases + evaluation_cases}
    configured_slices = set(policy["valid_slices"])
    new_slices = sorted(observed_slices - configured_slices)
    if new_slices:
        checks.append({"name": "new_slices", "passes": False, "detail": new_slices})

    for row in report["slice_report"]:
        checks.append({
            "name": f"slice_min_cases:{row['slice']}",
            "passes": row["count"] >= policy["min_slice_cases"],
            "detail": {"count": row["count"], "minimum": policy["min_slice_cases"]},
        })

    checks.append({
        "name": "calibrated_ece",
        "passes": report["calibrated_metrics"]["ece"] <= policy["max_calibrated_ece"],
        "detail": {"ece": report["calibrated_metrics"]["ece"], "maximum": policy["max_calibrated_ece"]},
    })
    checks.append({
        "name": "recommended_policy",
        "passes": report["recommended_policy"]["passes"],
        "detail": report["recommended_policy"],
    })
    return checks


def build_manifest(report, policy, cases_path, policy_path, calibration_cases, evaluation_cases):
    return {
        "model_version": policy["model_version"],
        "prompt_version": policy["prompt_version"],
        "retrieval_version": policy["retrieval_version"],
        "score_name": policy["score_name"],
        "score_semantics": policy["score_semantics"],
        "calibrator_type": report["calibrator"]["type"],
        "calibrator_version": policy["calibrator_version"],
        "policy_version": policy["policy_version"],
        "owner": policy["owner"],
        "dataset_hash_sha256": sha256_file(cases_path),
        "policy_hash_sha256": sha256_file(policy_path),
        "observed_slices": sorted({case["slice"] for case in calibration_cases + evaluation_cases}),
        "valid_slices": policy["valid_slices"],
        "known_bad_slices": policy["known_bad_slices"],
        "dataset_counts": {
            "calibration": len(calibration_cases),
            "evaluation": len(evaluation_cases),
        },
        "base_rates": {
            "calibration": round(base_rate(calibration_cases), 4),
            "evaluation": round(base_rate(evaluation_cases), 4),
        },
        "quality_gate": {
            "passes": all(check["passes"] for check in report["operational_checks"]),
            "checks": report["operational_checks"],
        },
        "metrics": {
            "raw_ece": report["raw_metrics"]["ece"],
            "calibrated_ece": report["calibrated_metrics"]["ece"],
            "raw_brier": report["raw_metrics"]["brier"],
            "calibrated_brier": report["calibrated_metrics"]["brier"],
        },
        "recommended_policy": report["recommended_policy"],
        "recalibration_triggers": policy["recalibration_triggers"],
    }


def render_decision(report, manifest):
    rec = report["recommended_policy"]
    gate = "pasa" if manifest["quality_gate"]["passes"] else "no pasa"
    lines = [
        "# Decisión de calibración",
        "",
        f"Estado del gate: **{gate}**.",
        "",
        "## Política recomendada",
        "",
        f"- `low`: {rec['low']}",
        f"- `high`: {rec['high']}",
        f"- tasa de revisión: {rec['review_rate']}",
        f"- cobertura automática: {rec['auto_coverage']}",
        f"- error automático: {rec['auto_error_rate']} con intervalo Wilson 95 % `{rec['auto_error_wilson_95']}`",
        f"- coste estimado: {rec['cost']}",
        "",
        "## Evidencia mínima",
        "",
        f"- ECE bruto: {report['raw_metrics']['ece']}",
        f"- ECE calibrado: {report['calibrated_metrics']['ece']}",
        f"- Brier bruto: {report['raw_metrics']['brier']}",
        f"- Brier calibrado: {report['calibrated_metrics']['brier']}",
        f"- hash dataset: `{manifest['dataset_hash_sha256'][:12]}`",
        f"- hash política: `{manifest['policy_hash_sha256'][:12]}`",
        "",
        "## Lectura operativa",
        "",
        "Automatiza solo fuera de la zona gris y conserva revisión cuando el conjunto conformal no permite una clase única.",
        "Si cambia el modelo, el prompt, el retrieval, el dominio o la mezcla de tickets, recalibra antes de conservar estos umbrales.",
    ]
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", default="evals/calibration_cases.csv")
    parser.add_argument("--policy", default="policies/calibration_policy.json")
    parser.add_argument("--output", default="output/calibration_report.json")
    parser.add_argument("--manifest-output", default="output/calibration_manifest.json")
    parser.add_argument("--decision-output", default="output/calibration_decision.md")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    policy = json.loads(Path(args.policy).read_text(encoding="utf-8"))
    cases = load_cases(args.cases)
    calibration = split_cases(cases, "calibration")
    evaluation = split_cases(cases, "evaluation")
    calibrator = fit_histogram_calibrator(calibration, policy["bins"])
    calibration_calibrated = apply_calibrator(calibration, calibrator, policy["bins"])
    evaluation_calibrated = apply_calibrator(evaluation, calibrator, policy["bins"])
    q = conformal_threshold(calibration_calibrated, policy["alpha"])
    recommended = evaluate_thresholds(evaluation_calibrated, q, policy)

    report = {
        "raw_metrics": metrics_block(evaluation, "raw_score", policy["bins"], policy),
        "calibrated_metrics": metrics_block(evaluation_calibrated, "calibrated_score", policy["bins"], policy),
        "slice_report": slice_report(evaluation_calibrated, "calibrated_score", policy["bins"]),
        "calibrator": {
            "type": "histogram_laplace",
            "bins": policy["bins"],
            "mapping": calibrator,
        },
        "conformal": {
            "alpha": policy["alpha"],
            "target_coverage": round(1 - policy["alpha"], 4),
            "q": round(q, 4),
        },
        "risk_coverage_curve": risk_coverage_curve(evaluation_calibrated, q, policy),
        "recommended_policy": recommended,
    }
    report["operational_checks"] = operational_checks(report, policy, calibration_calibrated, evaluation_calibrated)
    manifest = build_manifest(report, policy, args.cases, args.policy, calibration_calibrated, evaluation_calibrated)
    report["manifest_preview"] = {
        "dataset_hash_sha256": manifest["dataset_hash_sha256"],
        "policy_hash_sha256": manifest["policy_hash_sha256"],
        "quality_gate_passes": manifest["quality_gate"]["passes"],
    }

    rendered = json.dumps(report, indent=2, ensure_ascii=False)
    print(rendered)
    if args.write:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(rendered + "\n", encoding="utf-8")
        Path(args.manifest_output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.manifest_output).write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        Path(args.decision_output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.decision_output).write_text(render_decision(report, manifest), encoding="utf-8")


if __name__ == "__main__":
    main()
