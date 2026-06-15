from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "output/computer_use_report.json"
ASSUMPTIONS_PATH = ROOT / "data/capacity_assumptions.json"
OUTPUT = ROOT / "output"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def task_estimate(task: dict, assumptions: dict) -> dict:
    per_step = assumptions["per_step"]
    pricing = assumptions["pricing"]
    human = assumptions["human_review"]
    steps = max(1, int(task["metrics"]["steps_total"]))
    observations = steps + 1

    input_tokens = observations * per_step["screenshot_input_tokens"]
    output_tokens = steps * per_step["action_output_tokens"]
    model_cost = (input_tokens / 1_000_000) * pricing["input_usd_per_million_tokens"]
    model_cost += (output_tokens / 1_000_000) * pricing["output_usd_per_million_tokens"]

    automation_seconds = steps * (
        per_step["model_seconds"]
        + per_step["browser_action_seconds"]
        + per_step["observation_seconds"]
    )
    approval_count = int(task["metrics"]["approval_count"])
    human_seconds = approval_count * human["seconds_per_approval"]
    human_cost = (human_seconds / 3600) * human["operator_hourly_cost_usd"]

    return {
        "task_id": task["task_id"],
        "decision": task["decision"],
        "steps_total": steps,
        "input_tokens_est": round(input_tokens, 2),
        "output_tokens_est": round(output_tokens, 2),
        "automation_seconds_est": round(automation_seconds, 2),
        "human_seconds_est": round(human_seconds, 2),
        "model_cost_usd_est": round(model_cost, 6),
        "human_cost_usd_est": round(human_cost, 4),
        "total_cost_usd_est": round(model_cost + human_cost, 4),
    }


def scenario_estimate(scenario: dict, task_estimates: dict[str, dict]) -> dict:
    tasks_per_day = scenario["tasks_per_day"]
    weighted = []
    for task_id, weight in scenario["task_mix"].items():
        estimate = task_estimates[task_id]
        weighted.append((weight, estimate))

    avg_seconds = sum(weight * item["automation_seconds_est"] for weight, item in weighted)
    avg_human_seconds = sum(weight * item["human_seconds_est"] for weight, item in weighted)
    avg_cost = sum(weight * item["total_cost_usd_est"] for weight, item in weighted)
    daily_automation_hours = (tasks_per_day * avg_seconds) / 3600
    daily_human_hours = (tasks_per_day * avg_human_seconds) / 3600
    available_worker_hours = scenario["browser_workers"] * scenario["business_hours"]

    return {
        "scenario_id": scenario["scenario_id"],
        "description": scenario["description"],
        "tasks_per_day": tasks_per_day,
        "browser_workers": scenario["browser_workers"],
        "avg_seconds_per_task_est": round(avg_seconds, 2),
        "daily_automation_hours_est": round(daily_automation_hours, 2),
        "daily_human_review_hours_est": round(daily_human_hours, 2),
        "daily_cost_usd_est": round(tasks_per_day * avg_cost, 2),
        "worker_utilization_est": round(daily_automation_hours / available_worker_hours, 3),
        "capacity_gate": "review" if daily_automation_hours > available_worker_hours * 0.7 else "pass",
    }


def main() -> None:
    report = load_json(REPORT_PATH)
    assumptions = load_json(ASSUMPTIONS_PATH)
    OUTPUT.mkdir(exist_ok=True)

    estimates = [task_estimate(task, assumptions) for task in report["results"]]
    estimates_by_task = {item["task_id"]: item for item in estimates}
    scenarios = [scenario_estimate(scenario, estimates_by_task) for scenario in assumptions["scenarios"]]

    payload = {
        "schema_version": "1.0",
        "assumptions": assumptions,
        "task_estimates": estimates,
        "scenario_estimates": scenarios,
        "warning": "No es una factura real. Es un modelo operativo para discutir capacidad, latencia, revisión humana y coste.",
    }
    (OUTPUT / "capacity_report.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    with (OUTPUT / "capacity_matrix.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(estimates[0].keys()))
        writer.writeheader()
        writer.writerows(estimates)

    lines = [
        "# Estimación de capacidad para computer use",
        "",
        "Estas cifras son una maqueta razonada. Cambia latencias, precios y mezcla de tareas por los datos reales de tu proveedor, tu navegador y tu operación.",
        "",
        "| Tarea | Decisión | Pasos | Segundos auto. | Segundos humanos | Coste total estimado |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for item in estimates:
        lines.append(
            f"| `{item['task_id']}` | `{item['decision']}` | {item['steps_total']} | "
            f"{item['automation_seconds_est']} | {item['human_seconds_est']} | ${item['total_cost_usd_est']} |"
        )
    lines.extend(["", "## Escenarios", "", "| Escenario | Tareas/día | Workers | Horas auto. | Horas revisión | Coste/día | Gate |", "|---|---:|---:|---:|---:|---:|---|"])
    for item in scenarios:
        lines.append(
            f"| `{item['scenario_id']}` | {item['tasks_per_day']} | {item['browser_workers']} | "
            f"{item['daily_automation_hours_est']} | {item['daily_human_review_hours_est']} | "
            f"${item['daily_cost_usd_est']} | `{item['capacity_gate']}` |"
        )
    lines.extend(
        [
            "",
            "## Lectura de ingeniería",
            "",
            "- Si la utilización de workers supera el 70%, no lo vendas como estable: faltan cola, backpressure, workers o menos pasos por tarea.",
            "- Si sube la revisión humana, quizá el sistema es seguro, pero no necesariamente rentable.",
            "- Si el coste por tarea parece bajo pero la latencia por paso es alta, el problema será experiencia de usuario y SLO.",
            "- Si una tarea necesita aprobación frecuente, diseña una tarjeta de aprobación clara antes de producción.",
        ]
    )
    (OUTPUT / "capacity_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"OK: capacidad estimada en {OUTPUT}")


if __name__ == "__main__":
    main()
