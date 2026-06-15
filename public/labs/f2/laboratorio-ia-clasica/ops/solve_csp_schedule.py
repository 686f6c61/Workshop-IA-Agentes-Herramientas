#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = ROOT / "data" / "csp_schedule.json"
DEFAULT_OUTPUT_DIR = ROOT / "output"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_domains(data):
    base_domain = [(slot, room) for slot in data["slots"] for room in data["rooms"]]
    return {
        "repaso": base_domain,
        "practica": [(slot, "Lab") for slot in data["slots"]],
        "tutoria": [(slot, room) for slot in data["slots"] if slot.startswith("mar") for room in data["rooms"]]
    }


def is_consistent(assignment, slot_order):
    used_slots = [value[0] for value in assignment.values()]
    if len(used_slots) != len(set(used_slots)):
        return False, "dos sesiones comparten hora"
    if "practica" in assignment and assignment["practica"][1] != "Lab":
        return False, "la práctica no usa laboratorio"
    if "tutoria" in assignment and not assignment["tutoria"][0].startswith("mar"):
        return False, "la tutoría no está en martes"
    if "repaso" in assignment and "practica" in assignment:
        if slot_order[assignment["repaso"][0]] >= slot_order[assignment["practica"][0]]:
            return False, "repaso no va antes de práctica"
    return True, "ok"


def select_unassigned(sessions, domains, assignment):
    candidates = [session for session in sessions if session not in assignment]
    return min(candidates, key=lambda session: len(domains[session]))


def solve(data):
    sessions = data["sessions"]
    domains = build_domains(data)
    slot_order = {slot: index for index, slot in enumerate(data["slots"])}
    trace = []

    def backtrack(assignment):
        if len(assignment) == len(sessions):
            trace.append({"event": "solution", "assignment": assignment})
            return assignment
        session = select_unassigned(sessions, domains, assignment)
        trace.append({"event": "select_variable", "session": session, "domain_size": len(domains[session])})
        for value in domains[session]:
            candidate = {**assignment, session: value}
            ok, reason = is_consistent(candidate, slot_order)
            trace.append({"event": "try_value", "session": session, "value": value, "ok": ok, "reason": reason})
            if ok:
                result = backtrack(candidate)
                if result:
                    return result
        trace.append({"event": "backtrack", "assignment": assignment})
        return None

    solution = backtrack({})
    return solution, trace


def render_decision(solution, trace):
    lines = [
        "# Decisión CSP",
        "",
        "Decisión: `solucion_valida`.",
        "",
        "| Sesión | Hora | Sala |",
        "|---|---|---|",
    ]
    for session, value in solution.items():
        lines.append(f"| `{session}` | `{value[0]}` | `{value[1]}` |")
    lines.extend([
        "",
        "## Por qué cumple",
        "",
        "- No hay dos sesiones en la misma hora.",
        "- `practica` queda en `Lab`.",
        "- `repaso` ocurre antes que `practica`.",
        "- `tutoria` queda en martes.",
        "",
        "## Lectura técnica",
        "",
        f"La búsqueda deja `{len(trace)}` eventos de traza. Elegir antes las variables más restringidas reduce ramas inútiles y hace visible la poda.",
        "",
    ])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--fail-on-no-solution", action="store_true")
    args = parser.parse_args()

    data = read_json(args.data)
    solution, trace = solve(data)
    report = {
        "status": "solucion_valida" if solution else "sin_solucion",
        "solution": solution,
        "trace_event_count": len(trace)
    }
    if args.write:
        write_json(args.output_dir / "csp_solution.json", report)
        (args.output_dir / "csp_trace.jsonl").write_text(
            "\n".join(json.dumps(row, ensure_ascii=False) for row in trace) + "\n",
            encoding="utf-8"
        )
        if solution:
            (args.output_dir / "csp_decision.md").write_text(render_decision(solution, trace), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.fail_on_no_solution and not solution:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
