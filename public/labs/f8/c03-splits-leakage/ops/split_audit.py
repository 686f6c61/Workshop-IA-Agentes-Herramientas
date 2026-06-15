#!/usr/bin/env python3
import argparse
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET = ROOT / "data" / "support_split_cases.csv"
DEFAULT_POLICY = ROOT / "contracts" / "split_policy.json"
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


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def relative_path(path):
    path = path.resolve()
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def write_csv(path, fieldnames, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def normalize_text(value):
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def tokens(value):
    return set(normalize_text(value).split())


def jaccard(left, right):
    left_tokens = tokens(left)
    right_tokens = tokens(right)
    if not left_tokens and not right_tokens:
        return 1.0
    if not left_tokens or not right_tokens:
        return 0.0
    return len(left_tokens & right_tokens) / len(left_tokens | right_tokens)


def parse_day(row):
    return date.fromisoformat(row["created_at"])


def stable_score(value):
    return sum((index + 1) * ord(char) for index, char in enumerate(value))


def split_sizes(total, ratios):
    train = round(total * ratios["train"])
    validation = round(total * ratios["validation"])
    if train + validation >= total:
        validation = max(1, total - train - 1)
    test = total - train - validation
    return train, validation, test


def assign_by_order(rows, ordered_rows, policy):
    train_size, validation_size, _ = split_sizes(len(rows), policy["target_ratios"])
    assignments = {}
    for index, row in enumerate(ordered_rows):
        if index < train_size:
            split = "train"
        elif index < train_size + validation_size:
            split = "validation"
        else:
            split = "test"
        assignments[row["case_id"]] = split
    return assignments


def random_row(rows, policy):
    ordered = sorted(rows, key=lambda row: stable_score(row["case_id"]))
    return assign_by_order(rows, ordered, policy)


def stratified_label(rows, policy):
    assignments = {}
    buckets = defaultdict(list)
    for row in rows:
        buckets[row["label"]].append(row)
    for label_rows in buckets.values():
        ordered = sorted(label_rows, key=lambda row: stable_score(row["case_id"]))
        train_size, validation_size, _ = split_sizes(len(label_rows), policy["target_ratios"])
        for index, row in enumerate(ordered):
            if index < train_size:
                split = "train"
            elif index < train_size + validation_size:
                split = "validation"
            else:
                split = "test"
            assignments[row["case_id"]] = split
    return assignments


def group_holdout(rows, policy):
    groups = sorted({row["student_id"] for row in rows}, key=stable_score)
    train_size, validation_size, _ = split_sizes(len(groups), policy["target_ratios"])
    group_split = {}
    for index, group in enumerate(groups):
        if index < train_size:
            split = "train"
        elif index < train_size + validation_size:
            split = "validation"
        else:
            split = "test"
        group_split[group] = split
    return {row["case_id"]: group_split[row["student_id"]] for row in rows}


def time_cutoff(rows, policy):
    ordered = sorted(rows, key=lambda row: (parse_day(row), row["case_id"]))
    return assign_by_order(rows, ordered, policy)


def time_group_holdout(rows, policy):
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["student_id"]].append(row)
    groups = sorted(grouped, key=lambda group: (max(parse_day(row) for row in grouped[group]), group))
    train_size, validation_size, _ = split_sizes(len(groups), policy["target_ratios"])
    group_split = {}
    for index, group in enumerate(groups):
        if index < train_size:
            split = "train"
        elif index < train_size + validation_size:
            split = "validation"
        else:
            split = "test"
        group_split[group] = split
    return {row["case_id"]: group_split[row["student_id"]] for row in rows}


def distribution(rows, assignments, column):
    counts = Counter(row[column] for row in rows)
    total = sum(counts.values()) or 1
    global_dist = {key: counts[key] / total for key in sorted(counts)}
    by_split = {}
    for split in ["train", "validation", "test"]:
        split_rows = [row for row in rows if assignments[row["case_id"]] == split]
        split_counts = Counter(row[column] for row in split_rows)
        split_total = sum(split_counts.values()) or 1
        dist = {key: split_counts.get(key, 0) / split_total for key in sorted(global_dist)}
        by_split[split] = {
            "distribution": {key: round(value, 6) for key, value in dist.items()},
            "total_variation_vs_global": round(total_variation(global_dist, dist), 6),
        }
    return {
        "global_distribution": {key: round(value, 6) for key, value in global_dist.items()},
        "by_split": by_split,
    }


def total_variation(left, right):
    keys = sorted(set(left) | set(right))
    return 0.5 * sum(abs(left.get(key, 0.0) - right.get(key, 0.0)) for key in keys)


def overlap_pairs(rows, assignments, field):
    by_value = defaultdict(list)
    for row in rows:
        by_value[row[field]].append(row)
    findings = []
    for value, items in by_value.items():
        splits = sorted({assignments[item["case_id"]] for item in items})
        if len(splits) > 1:
            findings.append(
                {
                    "kind": f"{field}_overlap",
                    "value": value,
                    "splits": "|".join(splits),
                    "case_ids": "|".join(sorted(item["case_id"] for item in items)),
                }
            )
    return findings


def text_leakage(rows, assignments, threshold):
    findings = []
    for index, left in enumerate(rows):
        for right in rows[index + 1 :]:
            left_split = assignments[left["case_id"]]
            right_split = assignments[right["case_id"]]
            if left_split == right_split:
                continue
            left_text = normalize_text(left["text"])
            right_text = normalize_text(right["text"])
            if left_text == right_text:
                findings.append(
                    {
                        "kind": "exact_text",
                        "value": "1.0",
                        "splits": f"{left_split}|{right_split}",
                        "case_ids": f"{left['case_id']}|{right['case_id']}",
                    }
                )
                continue
            score = jaccard(left["text"], right["text"])
            if score >= threshold:
                findings.append(
                    {
                        "kind": "near_text",
                        "value": str(round(score, 6)),
                        "splits": f"{left_split}|{right_split}",
                        "case_ids": f"{left['case_id']}|{right['case_id']}",
                    }
                )
    return findings


def temporal_findings(rows, assignments):
    train_dates = [parse_day(row) for row in rows if assignments[row["case_id"]] == "train"]
    test_dates = [parse_day(row) for row in rows if assignments[row["case_id"]] == "test"]
    if not train_dates or not test_dates:
        return []
    min_test = min(test_dates)
    future_train = [
        row
        for row in rows
        if assignments[row["case_id"]] == "train" and parse_day(row) > min_test
    ]
    if not future_train:
        return []
    return [
        {
            "kind": "future_train_vs_test",
            "value": min_test.isoformat(),
            "splits": "train|test",
            "case_ids": "|".join(row["case_id"] for row in future_train),
        }
    ]


def analyze_strategy(name, rows, assignments, policy):
    findings = []
    findings.extend(overlap_pairs(rows, assignments, "student_id"))
    findings.extend(overlap_pairs(rows, assignments, "source_id"))
    findings.extend(text_leakage(rows, assignments, policy["near_duplicate_jaccard_threshold"]))
    findings.extend(temporal_findings(rows, assignments))
    label_dist = distribution(rows, assignments, "label")
    high_label_tv = {
        split: detail
        for split, detail in label_dist["by_split"].items()
        if detail["total_variation_vs_global"] > policy["max_label_total_variation"]
    }
    test_labels = {row["label"] for row in rows if assignments[row["case_id"]] == "test"}
    missing_test_labels = sorted(set(policy["required_test_labels"]) - test_labels)

    counts_by_kind = Counter(item["kind"] for item in findings)
    blocking = []
    if counts_by_kind["student_id_overlap"] > policy["max_group_overlap_pairs"]:
        blocking.append("student_group_overlap")
    if counts_by_kind["source_id_overlap"] > policy["max_source_overlap_pairs"]:
        blocking.append("source_overlap")
    if counts_by_kind["exact_text"] > policy["max_exact_text_leaks"]:
        blocking.append("exact_text_leakage")
    if counts_by_kind["near_text"] > policy["max_near_text_leaks"]:
        blocking.append("near_text_leakage")
    if counts_by_kind["future_train_vs_test"] > policy["max_future_train_rows_vs_test"]:
        blocking.append("temporal_leakage")

    review = []
    if high_label_tv:
        review.append("label_distribution_shift")
    if missing_test_labels:
        review.append("missing_required_test_labels")

    gate = "block" if blocking else ("review" if review else "pass")

    return {
        "strategy": name,
        "split_counts": dict(Counter(assignments.values())),
        "label_distribution": label_dist,
        "missing_test_labels": missing_test_labels,
        "findings": findings,
        "blocking_failures": blocking,
        "review_failures": review,
        "gate": gate,
    }


def choose_strategy(results, policy):
    by_name = {result["strategy"]: result for result in results}
    for name in policy["preferred_strategy_order"]:
        if by_name[name]["gate"] == "pass":
            return name
    for name in policy["preferred_strategy_order"]:
        if by_name[name]["gate"] == "review":
            return name
    return min(results, key=lambda result: (len(result["blocking_failures"]), len(result["review_failures"])))["strategy"]


def build_report(rows, policy):
    strategies = {
        "random_row": random_row(rows, policy),
        "stratified_label": stratified_label(rows, policy),
        "group_holdout": group_holdout(rows, policy),
        "time_cutoff": time_cutoff(rows, policy),
        "time_group_holdout": time_group_holdout(rows, policy),
    }
    results = [analyze_strategy(name, rows, assignments, policy) for name, assignments in strategies.items()]
    chosen = choose_strategy(results, policy)
    return {
        "policy_id": policy["policy_id"],
        "row_count": len(rows),
        "strategies": results,
        "chosen_strategy": chosen,
        "recommendation": recommendation(next(result for result in results if result["strategy"] == chosen)),
    }, strategies


def build_manifest(rows, policy, report, strategies, dataset_path, policy_path):
    chosen_result = next(result for result in report["strategies"] if result["strategy"] == report["chosen_strategy"])
    chosen_assignments = strategies[report["chosen_strategy"]]
    assignments_by_split = {split: [] for split in ["train", "validation", "test"]}
    assignment_rows = []

    for row in sorted(rows, key=lambda item: item["case_id"]):
        split = chosen_assignments[row["case_id"]]
        assignments_by_split[split].append(row["case_id"])
        assignment_rows.append(
            {
                "case_id": row["case_id"],
                "split": split,
                "group": row[policy["split_keys"]["group"]],
                "source": row[policy["split_keys"]["source"]],
                "created_at": row[policy["split_keys"]["time"]],
                "label": row[policy["split_keys"]["label"]],
            }
        )

    finding_counts = Counter(finding["kind"] for finding in chosen_result["findings"])
    split_counts = {split: len(case_ids) for split, case_ids in assignments_by_split.items()}

    return {
        "manifest_version": "1.0",
        "policy_id": policy["policy_id"],
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "owner": policy["owner"],
        "evaluation_question": policy["evaluation_question"],
        "dataset": {
            "path": relative_path(dataset_path),
            "sha256": sha256_file(dataset_path),
            "row_count": len(rows),
        },
        "policy": {
            "path": relative_path(policy_path),
            "sha256": sha256_file(policy_path),
        },
        "split_contract": {
            "selected_strategy": report["chosen_strategy"],
            "gate": chosen_result["gate"],
            "recommendation": report["recommendation"],
            "target_ratios": policy["target_ratios"],
            "actual_counts": split_counts,
            "keys": policy["split_keys"],
            "blocking_failures": chosen_result["blocking_failures"],
            "review_failures": chosen_result["review_failures"],
            "finding_counts": dict(sorted(finding_counts.items())),
        },
        "allowed_split_use": policy["allowed_split_use"],
        "forbidden_test_use": policy["forbidden_test_use"],
        "preprocessing_contract": policy["preprocessing_contract"],
        "rag_llm_eval_contract": policy["rag_llm_eval_contract"],
        "assignments_by_split": assignments_by_split,
        "assignments": assignment_rows,
    }


def recommendation(result):
    if result["gate"] == "pass":
        return f"usar {result['strategy']} y versionar asignaciones"
    if result["gate"] == "review":
        return f"revisar {','.join(result['review_failures'])} antes de cerrar {result['strategy']}"
    return f"no usar {result['strategy']} sin corregir {','.join(result['blocking_failures'])}"


def write_outputs(output_dir, rows, report, strategies, policy, dataset_path, policy_path):
    write_json(output_dir / "split_report.json", report)
    write_json(output_dir / "split_manifest.json", build_manifest(rows, policy, report, strategies, dataset_path, policy_path))
    comparison = []
    findings_rows = []
    for result in report["strategies"]:
        comparison.append(
            {
                "strategy": result["strategy"],
                "gate": result["gate"],
                "blocking_failures": ";".join(result["blocking_failures"]),
                "review_failures": ";".join(result["review_failures"]),
                "train": result["split_counts"].get("train", 0),
                "validation": result["split_counts"].get("validation", 0),
                "test": result["split_counts"].get("test", 0),
            }
        )
        for finding in result["findings"]:
            findings_rows.append({"strategy": result["strategy"], **finding})
    write_csv(output_dir / "strategy_comparison.csv", ["strategy", "gate", "blocking_failures", "review_failures", "train", "validation", "test"], comparison)
    write_csv(output_dir / "leakage_findings.csv", ["strategy", "kind", "value", "splits", "case_ids"], findings_rows)
    assignments_rows = []
    for row in rows:
        item = {"case_id": row["case_id"], "created_at": row["created_at"], "student_id": row["student_id"], "label": row["label"]}
        for strategy, assignments in strategies.items():
            item[strategy] = assignments[row["case_id"]]
        assignments_rows.append(item)
    write_csv(output_dir / "split_assignments.csv", ["case_id", "created_at", "student_id", "label", "random_row", "stratified_label", "group_holdout", "time_cutoff", "time_group_holdout"], assignments_rows)
    write_decision(output_dir / "split_decision.md", report)


def write_decision(path, report):
    chosen = next(result for result in report["strategies"] if result["strategy"] == report["chosen_strategy"])
    lines = [
        "# Decisión de split",
        "",
        f"Estrategia recomendada: **{report['chosen_strategy']}**.",
        f"Gate: **{chosen['gate']}**.",
        "",
        "## Lectura",
        "",
        report["recommendation"] + ".",
        "",
        "## Comparación",
        "",
        "| Estrategia | Gate | Bloqueos | Revisiones |",
        "|---|---|---|---|",
    ]
    for result in report["strategies"]:
        lines.append(
            f"| `{result['strategy']}` | `{result['gate']}` | {', '.join(result['blocking_failures']) or 'ninguno'} | {', '.join(result['review_failures']) or 'ninguna'} |"
        )
    lines.extend(
        [
            "",
            "## Próxima acción",
            "",
            "Si la estrategia elegida no queda en `pass`, revisa la política, el agrupamiento, la ventana temporal o el dataset fuente antes de usar esa evaluación.",
            "",
            "Antes de publicar resultados, guarda también `split_manifest.json`: contiene hashes, estrategia, contrato de uso y asignaciones por split.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    rows = read_csv(args.dataset)
    policy = read_json(args.policy)
    report, strategies = build_report(rows, policy)
    if args.write:
        write_outputs(args.output_dir, rows, report, strategies, policy, args.dataset, args.policy)
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
