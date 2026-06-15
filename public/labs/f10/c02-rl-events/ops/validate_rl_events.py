#!/usr/bin/env python3
import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EVENTS = ROOT / "data" / "events.jsonl"
DEFAULT_CONTRACT = ROOT / "contracts" / "rl_event_contract.json"
DEFAULT_OUTPUT = ROOT / "output"


TYPE_CHECKERS = {
    "str": lambda value: isinstance(value, str),
    "int": lambda value: isinstance(value, int) and not isinstance(value, bool),
    "number": lambda value: isinstance(value, (int, float)) and not isinstance(value, bool),
    "bool": lambda value: isinstance(value, bool),
    "dict": lambda value: isinstance(value, dict),
    "list": lambda value: isinstance(value, list),
    "datetime": lambda value: isinstance(value, str) and parse_time(value) is not None,
}


def parse_time(value):
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except Exception:
        return None


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_events(path):
    events = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        event = json.loads(line)
        event["_line_number"] = line_number
        events.append(event)
    return events


def stable_hash(obj):
    payload = json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def add_error(errors, event, message):
    errors.append({
        "line": event.get("_line_number"),
        "event_id": event.get("event_id"),
        "episode_id": event.get("episode_id"),
        "message": message,
    })


def validate_event_shape(events, contract):
    errors = []
    warnings = []
    required = contract["required_fields"]
    field_types = contract["field_types"]
    allowed_actions = set(contract["allowed_actions"])
    required_reward_terms = set(contract["required_reward_terms"])
    min_probability = contract["minimum_action_probability"]
    max_delay_hours = contract["maximum_reward_delay_hours"]

    seen_ids = set()
    for event in events:
        for field in required:
            if field not in event:
                add_error(errors, event, f"missing required field: {field}")

        event_id = event.get("event_id")
        if event_id in seen_ids:
            add_error(errors, event, "duplicate event_id")
        seen_ids.add(event_id)

        for field, expected in field_types.items():
            if field in event and not TYPE_CHECKERS[expected](event[field]):
                add_error(errors, event, f"field {field} should be {expected}")

        if event.get("schema_version") != contract["schema_version"]:
            add_error(errors, event, "schema_version does not match contract")

        action = event.get("action")
        available = event.get("available_actions", [])
        if isinstance(available, list):
            if action not in available:
                add_error(errors, event, "action is not in available_actions")
            unknown = sorted(set(available) - allowed_actions)
            if unknown:
                add_error(errors, event, f"available_actions contains unknown actions: {unknown}")
        if action not in allowed_actions:
            add_error(errors, event, "action is not in allowed_actions catalog")

        probability = event.get("action_probability")
        if isinstance(probability, (int, float)) and not isinstance(probability, bool):
            if probability < 0 or probability > 1:
                add_error(errors, event, "action_probability is outside [0, 1]")
            elif probability < min_probability:
                warnings.append({
                    "event_id": event.get("event_id"),
                    "message": "action_probability below configured minimum",
                    "value": probability,
                })

        reward_terms = event.get("reward_terms", {})
        if isinstance(reward_terms, dict):
            missing_terms = sorted(required_reward_terms - set(reward_terms))
            if missing_terms:
                add_error(errors, event, f"missing reward_terms: {missing_terms}")

        event_time = parse_time(event.get("event_time", ""))
        ingestion_time = parse_time(event.get("ingestion_time", ""))
        reward_time = parse_time(event.get("reward_time", ""))
        if event_time and ingestion_time and event_time > ingestion_time:
            add_error(errors, event, "event_time is after ingestion_time")
        if event_time and reward_time and event_time > reward_time:
            add_error(errors, event, "event_time is after reward_time")
        if event_time and reward_time:
            delay_hours = (reward_time - event_time).total_seconds() / 3600
            if delay_hours > max_delay_hours:
                warnings.append({
                    "event_id": event.get("event_id"),
                    "message": "reward delay exceeds configured window",
                    "delay_hours": round(delay_hours, 3),
                })

    return errors, warnings


def group_episodes(events):
    grouped = defaultdict(list)
    for event in events:
        episode_id = event.get("episode_id", "__missing_episode__")
        grouped[episode_id].append(event)
    return {episode_id: sorted(items, key=lambda e: e.get("t", 10**9)) for episode_id, items in grouped.items()}


def validate_episodes(episodes):
    errors = []
    for episode_id, events in episodes.items():
        expected_t = list(range(len(events)))
        actual_t = [event.get("t") for event in events]
        if actual_t != expected_t:
            errors.append({
                "episode_id": episode_id,
                "message": f"episode t sequence should be {expected_t}, got {actual_t}",
            })
        terminal_positions = [idx for idx, event in enumerate(events) if event.get("terminal")]
        if not terminal_positions:
            errors.append({"episode_id": episode_id, "message": "episode has no terminal event"})
        elif terminal_positions[-1] != len(events) - 1:
            errors.append({"episode_id": episode_id, "message": "events appear after terminal event"})
    return errors


def compute_returns(episodes, gamma):
    returns = {}
    for episode_id, events in episodes.items():
        total = 0.0
        for idx, event in enumerate(events):
            total += (gamma ** idx) * float(event.get("reward", 0.0))
        returns[episode_id] = round(total, 6)
    return returns


def compute_coverage(events, contract):
    total = len(events)
    state_action = Counter((event.get("state_id", "__missing_state__"), event.get("action", "__missing_action__")) for event in events)
    state_counts = Counter(event.get("state_id", "__missing_state__") for event in events)
    action_counts = Counter(event.get("action", "__missing_action__") for event in events)

    state_action_rows = []
    for (state, action), count in sorted(state_action.items()):
        state_action_rows.append({
            "state_id": state,
            "action": action,
            "count": count,
            "share": round(count / total, 6) if total else 0.0,
        })

    critical_pairs = [tuple(pair) for pair in contract["critical_state_action_pairs"]]
    low_coverage = []
    for state, action in critical_pairs:
        count = state_action.get((state, action), 0)
        if count < contract["minimum_events_per_critical_pair"]:
            low_coverage.append({
                "state_id": state,
                "action": action,
                "count": count,
                "minimum": contract["minimum_events_per_critical_pair"],
            })

    return {
        "state_counts": dict(sorted(state_counts.items())),
        "action_counts": dict(sorted(action_counts.items())),
        "state_action": state_action_rows,
        "low_coverage_pairs": low_coverage,
    }


def build_snapshot(episodes, gamma, returns):
    snapshot = {
        "snapshot_type": "rl_trajectory_snapshot",
        "gamma": gamma,
        "episodes": [],
    }
    for episode_id, events in sorted(episodes.items()):
        snapshot["episodes"].append({
            "episode_id": episode_id,
            "return": returns[episode_id],
            "steps": [
                {
                    "t": event.get("t"),
                    "state_id": event.get("state_id"),
                    "action": event.get("action"),
                    "action_probability": event.get("action_probability"),
                    "reward": event.get("reward"),
                    "next_state_id": event.get("next_state_id"),
                    "terminal": event.get("terminal"),
                    "policy_version": event.get("policy_version"),
                    "reward_version": event.get("reward_version"),
                    "trace_id": event.get("trace_id"),
                }
                for event in events
            ],
        })
    snapshot["snapshot_hash"] = stable_hash(snapshot)
    return snapshot


def decide(shape_errors, episode_errors, warnings, coverage, contract):
    if contract["decision_policy"]["block_on_schema_errors"] and shape_errors:
        return "block"
    if contract["decision_policy"]["block_on_time_errors"] and episode_errors:
        return "block"
    if contract["decision_policy"]["review_on_low_coverage"] and coverage["low_coverage_pairs"]:
        return "review"
    if contract["decision_policy"]["review_on_low_propensity"] and warnings:
        return "review"
    return "pass"


def write_decision(path, report):
    lines = [
        "# Decisión técnica: eventos RL",
        "",
        f"Estado: `{report['status']}`",
        "",
        f"Eventos revisados: {report['summary']['events']}",
        f"Episodios revisados: {report['summary']['episodes']}",
        f"Snapshot hash: `{report['snapshot_hash']}`",
        "",
        "## Interpretación",
        "",
    ]
    if report["status"] == "pass":
        lines.append("El snapshot cumple el contrato mínimo y puede usarse como base para análisis, evaluación offline pequeña o práctica de laboratorio.")
    elif report["status"] == "review":
        lines.append("El snapshot no está roto, pero necesita revisión antes de sostener una decisión fuerte. Mira cobertura y avisos.")
    else:
        lines.append("El snapshot queda bloqueado. No debería usarse para entrenamiento ni comparación de políticas hasta corregir errores.")

    lines.extend(["", "## Checks principales", ""])
    for name, passed in report["checks"].items():
        lines.append(f"- {name}: `{passed}`")

    lines.extend(["", "## Retornos por episodio", ""])
    for episode_id, value in sorted(report["episode_returns"].items()):
        lines.append(f"- `{episode_id}`: {value}")

    if report["coverage"]["low_coverage_pairs"]:
        lines.extend(["", "## Cobertura que exige revisión", ""])
        for item in report["coverage"]["low_coverage_pairs"]:
            lines.append(f"- `{item['state_id']} -> {item['action']}` tiene {item['count']} eventos; mínimo esperado {item['minimum']}.")

    lines.extend([
        "",
        "## Qué cambiaría en un proyecto real",
        "",
        "1. Aumentaría cobertura en parejas estado-acción críticas antes de automatizar más.",
        "2. Guardaría este reporte junto al snapshot que alimente evaluación o entrenamiento.",
        "3. Convertiría cada error repetido en un test de CI del pipeline de datos.",
    ])

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_csv_coverage(path, coverage):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["state_id", "action", "count", "share"])
        writer.writeheader()
        writer.writerows(coverage["state_action"])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--events", type=Path, default=DEFAULT_EVENTS)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    contract = load_json(args.contract)
    events = load_events(args.events)
    shape_errors, warnings = validate_event_shape(events, contract)
    episodes = group_episodes(events)
    episode_errors = validate_episodes(episodes)
    returns = compute_returns(episodes, contract["gamma"])
    coverage = compute_coverage(events, contract)
    snapshot = build_snapshot(episodes, contract["gamma"], returns)
    status = decide(shape_errors, episode_errors, warnings, coverage, contract)

    report = {
        "status": status,
        "summary": {
            "events": len(events),
            "episodes": len(episodes),
            "contract_version": contract["contract_version"],
            "schema_version": contract["schema_version"],
            "gamma": contract["gamma"],
        },
        "checks": {
            "shape_ok": not shape_errors,
            "episodes_ok": not episode_errors,
            "coverage_ok": not coverage["low_coverage_pairs"],
            "warnings_ok": not warnings,
        },
        "errors": {
            "shape": shape_errors,
            "episodes": episode_errors,
        },
        "warnings": warnings,
        "episode_returns": returns,
        "coverage": coverage,
        "lineage": {
            "policy_versions": sorted({event.get("policy_version", "__missing_policy_version__") for event in events}),
            "reward_versions": sorted({event.get("reward_version", "__missing_reward_version__") for event in events}),
            "environment_versions": sorted({event.get("environment_version", "__missing_environment_version__") for event in events}),
        },
        "snapshot_hash": snapshot["snapshot_hash"],
    }

    if args.write:
        args.output.mkdir(parents=True, exist_ok=True)
        (args.output / "rl_event_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        (args.output / "trajectory_snapshot.json").write_text(json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        write_decision(args.output / "rl_event_decision.md", report)
        write_csv_coverage(args.output / "coverage_state_action.csv", coverage)
        print(f"status={status}")
        print(f"episodes={len(episodes)}")
        print(f"events={len(events)}")
        print(f"snapshot_hash={snapshot['snapshot_hash']}")
    else:
        print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
