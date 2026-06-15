#!/usr/bin/env python3
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def main():
    cases = json.loads((ROOT / "evals/rag_eval_cases.json").read_text(encoding="utf-8"))
    policy = json.loads((ROOT / "ops/ai/rag_eval_policy.json").read_text(encoding="utf-8"))
    rows = []
    for case in cases:
        gold = set(case["gold_chunks"])
        got = {item["chunk_id"] for item in case["retrieved"]}
        recall = 1.0 if not gold else len(gold & got) / len(gold)
        claims = case["answer"]["claims"]
        grounded = 1.0 if not claims else sum(bool(c["supporting_chunks"]) for c in claims) / len(claims)
        citation_ok = 1.0 if set(case["answer"]["citations"]).issubset(got) else 0.0
        abstention_ok = 1.0 if case["answer"]["abstained"] == (not case["answerable"]) else 0.0
        rows.append({"case_id": case["case_id"], "recall": recall, "grounded": grounded, "citation_ok": citation_ok, "abstention_ok": abstention_ok})
    avg = lambda key: round(sum(row[key] for row in rows) / len(rows), 4)
    summary = {"recall": avg("recall"), "groundedness": avg("grounded"), "citation_acceptance": avg("citation_ok"), "abstention_accuracy": avg("abstention_ok")}
    checks = {
        "recall_ok": summary["recall"] >= policy["min_recall_at_k"],
        "groundedness_ok": summary["groundedness"] >= policy["min_groundedness"],
        "citation_ok": summary["citation_acceptance"] >= policy["min_citation_acceptance"],
        "abstention_ok": summary["abstention_accuracy"] >= policy["min_abstention_accuracy"],
    }
    report = {"summary": summary, "rows": rows, "checks": checks, "decision": "promote_rag_eval" if all(checks.values()) else "fix_rag_before_release"}
    (ROOT / "output/rag_scorecard.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (ROOT / "output/rag_decision.md").write_text(f"# Decisión RAG\n\nEstado: `{report['decision']}`.\n\nResumen: `{summary}`.\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
