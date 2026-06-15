#!/usr/bin/env python3
import json
from pathlib import Path


ROUTES = [
    {"task": "faq_policy", "primary": "rag_fast", "fallback": "rag_safe", "max_cost_eur": 0.03},
    {"task": "student_balance", "primary": "tool_sql", "fallback": "human_review", "max_cost_eur": 0.02},
    {"task": "complex_case", "primary": "agent_supervised", "fallback": "human_review", "max_cost_eur": 0.12},
]


def choose(task, estimated_cost):
    route = next((item for item in ROUTES if item["task"] == task), None)
    if route is None:
        return {"task": task, "route": "human_review", "reason": "unknown_task"}
    if estimated_cost > route["max_cost_eur"]:
        return {"task": task, "route": route["fallback"], "reason": "budget_exceeded"}
    return {"task": task, "route": route["primary"], "reason": "within_budget"}


if __name__ == "__main__":
    cases = [
        choose("faq_policy", 0.02),
        choose("student_balance", 0.05),
        choose("complex_case", 0.09),
        choose("unknown", 0.01),
    ]
    report = {"routes": ROUTES, "cases": cases, "decision": "routing_policy_reviewable"}
    out = Path("output/routing_policy_report.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
