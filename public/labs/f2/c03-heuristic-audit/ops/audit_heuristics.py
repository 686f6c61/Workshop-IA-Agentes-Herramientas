#!/usr/bin/env python3
import argparse
import heapq
import json
from math import inf
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EPSILON = 1e-9


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def nodes(graph):
    found = set(graph["edges"])
    for edges in graph["edges"].values():
        for edge in edges:
            found.add(edge["to"])
    return sorted(found)


def reverse_edges(graph):
    reverse = {node: [] for node in nodes(graph)}
    for source, edges in graph["edges"].items():
        for edge in edges:
            reverse.setdefault(edge["to"], []).append({"to": source, "cost": edge["cost"]})
    return reverse


def dijkstra_to_goal(graph):
    goal = graph["goal"]
    reverse = reverse_edges(graph)
    distances = {node: inf for node in nodes(graph)}
    distances[goal] = 0
    heap = [(0, goal)]
    while heap:
        cost, current = heapq.heappop(heap)
        if cost > distances[current] + EPSILON:
            continue
        for edge in reverse.get(current, []):
            candidate = cost + edge["cost"]
            if candidate + EPSILON < distances[edge["to"]]:
                distances[edge["to"]] = candidate
                heapq.heappush(heap, (candidate, edge["to"]))
    return distances


def reconstruct(parent, goal):
    if goal not in parent:
        return []
    path = [goal]
    while parent[path[-1]] is not None:
        path.append(parent[path[-1]])
    return list(reversed(path))


def path_cost(graph, path):
    if not path:
        return None
    total = 0
    for left, right in zip(path, path[1:]):
        for edge in graph["edges"].get(left, []):
            if edge["to"] == right:
                total += edge["cost"]
                break
        else:
            return None
    return total


def priority_for(kind, g_cost, h_value, weight):
    if kind == "ucs":
        return g_cost
    if kind == "greedy":
        return h_value
    if kind == "astar":
        return g_cost + h_value
    if kind == "weighted_astar":
        return g_cost + weight * h_value
    raise ValueError(f"algoritmo desconocido: {kind}")


def search(graph, kind, heuristic_name="h_zero", weight=1.0, label=None):
    start, goal = graph["start"], graph["goal"]
    heuristic = graph["heuristics"][heuristic_name]
    counter = 0
    start_priority = priority_for(kind, 0, heuristic[start], weight)
    frontier = [(start_priority, counter, start)]
    parent = {start: None}
    best_g = {start: 0}
    closed = set()
    trace = []
    generated = 1
    max_frontier = 1

    while frontier:
        _, _, current = heapq.heappop(frontier)
        if current in closed:
            continue
        closed.add(current)
        current_g = best_g[current]
        current_h = heuristic[current]
        current_priority = priority_for(kind, current_g, current_h, weight)
        trace.append(
            {
                "node": current,
                "g": current_g,
                "h": current_h,
                "priority": round(current_priority, 4),
            }
        )
        if current == goal:
            break

        for edge in graph["edges"].get(current, []):
            nxt = edge["to"]
            candidate_g = current_g + edge["cost"]
            if nxt in closed:
                continue
            if nxt not in best_g or candidate_g + EPSILON < best_g[nxt]:
                best_g[nxt] = candidate_g
                parent[nxt] = current
                counter += 1
                priority = priority_for(kind, candidate_g, heuristic[nxt], weight)
                heapq.heappush(frontier, (priority, counter, nxt))
                generated += 1
        max_frontier = max(max_frontier, len(frontier))

    path = reconstruct(parent, goal)
    cost = path_cost(graph, path)
    return {
        "algorithm": label or kind,
        "kind": kind,
        "heuristic": heuristic_name,
        "weight": weight,
        "found": bool(path),
        "path": path,
        "cost": cost,
        "expanded": len(trace),
        "generated": generated,
        "max_frontier": max_frontier,
        "trace": trace,
    }


def audit_heuristic(graph, heuristic_name, h_star):
    heuristic = graph["heuristics"][heuristic_name]
    all_nodes = nodes(graph)
    missing = [node for node in all_nodes if node not in heuristic]
    negative = [node for node in all_nodes if node in heuristic and heuristic[node] < -EPSILON]
    goal_zero = graph["goal"] in heuristic and abs(heuristic[graph["goal"]]) <= EPSILON

    admissibility_violations = []
    for node in all_nodes:
        if node not in heuristic:
            continue
        if heuristic[node] > h_star[node] + EPSILON:
            admissibility_violations.append(
                {"node": node, "h": heuristic[node], "h_star": h_star[node]}
            )

    consistency_violations = []
    for source, edges in graph["edges"].items():
        if source not in heuristic:
            continue
        for edge in edges:
            target = edge["to"]
            if target not in heuristic:
                continue
            allowed = edge["cost"] + heuristic[target]
            if heuristic[source] > allowed + EPSILON:
                consistency_violations.append(
                    {
                        "edge": f"{source}->{target}",
                        "h_source": heuristic[source],
                        "cost": edge["cost"],
                        "h_target": heuristic[target],
                        "allowed": allowed,
                    }
                )

    return {
        "heuristic": heuristic_name,
        "missing_nodes": missing,
        "negative_nodes": negative,
        "goal_zero": goal_zero,
        "admissible": not missing and not negative and not admissibility_violations,
        "consistent": not missing and not consistency_violations,
        "admissibility_violations": admissibility_violations,
        "consistency_violations": consistency_violations,
        "dominates": [],
    }


def add_dominance(graph, audits):
    by_name = {audit["heuristic"]: audit for audit in audits}
    admissible_names = [
        audit["heuristic"]
        for audit in audits
        if audit["admissible"] and audit["goal_zero"] and not audit["negative_nodes"]
    ]
    for left in admissible_names:
        left_h = graph["heuristics"][left]
        for right in admissible_names:
            if left == right:
                continue
            right_h = graph["heuristics"][right]
            greater_or_equal = all(left_h[node] + EPSILON >= right_h[node] for node in nodes(graph))
            strictly_greater = any(left_h[node] > right_h[node] + EPSILON for node in nodes(graph))
            if greater_or_equal and strictly_greater:
                by_name[left]["dominates"].append(right)
    return audits


def format_path(path):
    return " -> ".join(path) if path else "sin solución"


def format_trace(row):
    parts = []
    for item in row["trace"]:
        parts.append(
            f"{item['node']}(g={item['g']}, h={item['h']}, f={item['priority']})"
        )
    return " -> ".join(parts)


def render_markdown(graph, h_star, audits, searches):
    def si_no(value):
        return "sí" if value else "no"

    lines = [
        "# Decisión: auditoría de heurísticas",
        "",
        f"Grafo: `{graph['name']}`. Inicio `{graph['start']}`, meta `{graph['goal']}`.",
        "",
        "## Coste óptimo real desde cada nodo",
        "",
        "| Nodo | h*(n) | Lectura |",
        "|---|---:|---|",
    ]
    for node, value in sorted(h_star.items()):
        if value == inf:
            value_text = "∞"
            reading = "No llega a la meta."
        else:
            value_text = str(value)
            reading = "Referencia para auditar h(n)."
        lines.append(f"| {node} | {value_text} | {reading} |")

    lines.extend(
        [
            "",
            "## Auditoría de heurísticas",
            "",
            "| Heurística | Admisible | Consistente | Meta a cero | Violaciones | Domina a |",
            "|---|---|---|---|---:|---|",
        ]
    )
    for audit in audits:
        violations = len(audit["admissibility_violations"]) + len(audit["consistency_violations"])
        dominates = ", ".join(audit["dominates"]) if audit["dominates"] else "nadie"
        lines.append(
            f"| {audit['heuristic']} | {si_no(audit['admissible'])} | {si_no(audit['consistent'])} | "
            f"{si_no(audit['goal_zero'])} | {violations} | {dominates} |"
        )

    lines.extend(["", "## Búsquedas comparadas", ""])
    lines.extend(
        [
            "| Algoritmo | Heurística | w | Camino | Coste | Óptimo | Expandidos | Generados | Frontera máx. |",
            "|---|---|---:|---|---:|---|---:|---:|---:|",
        ]
    )
    optimal_cost = h_star[graph["start"]]
    for row in searches:
        optimal = row["found"] and abs(row["cost"] - optimal_cost) <= EPSILON
        lines.append(
            f"| {row['algorithm']} | {row['heuristic']} | {row['weight']} | {format_path(row['path'])} | "
            f"{row['cost']} | {si_no(optimal)} | {row['expanded']} | {row['generated']} | {row['max_frontier']} |"
        )

    lines.extend(["", "## Trazas", ""])
    for row in searches:
        lines.append(f"- **{row['algorithm']}**: {format_trace(row)}")

    lines.extend(["", "## Lectura técnica", ""])
    lines.append("- `h_zero` convierte A* en UCS: no informa nada, pero conserva optimalidad.")
    lines.append("- `h_safe` no sobreestima y es consistente: A* mantiene garantías y reduce expansiones frente a una búsqueda sin información.")
    lines.append("- `h_exact_demo` coincide con `h*(n)`: enseña el límite ideal, aunque calcularlo normalmente equivale a resolver el problema.")
    lines.append("- Greedy mira solo `h(n)`: en este grafo llega a `S -> C -> G` con coste 7, una solución rápida pero peor que la óptima.")
    lines.append("- Weighted A* con `w=2.0` también devuelve coste 7: al inflar la heurística, expande menos, pero sacrifica la garantía de optimalidad.")
    lines.append("- `h_bad_overestimate` sobreestima nodos clave. Sirve como contraejemplo: si una heurística no pasa auditoría, no debe sostener promesas de coste mínimo.")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--fail-on-invalid", action="store_true")
    args = parser.parse_args()

    graph = load_json(ROOT / "data" / "heuristic_graph.json")
    policy = load_json(ROOT / "contracts" / "heuristic_policy.json")
    h_star = dijkstra_to_goal(graph)
    audits = [audit_heuristic(graph, name, h_star) for name in graph["heuristics"]]
    audits = add_dominance(graph, audits)

    weight = policy["weighted_astar_weight"]
    searches = [
        search(graph, "ucs", "h_zero", 1.0, "UCS"),
        search(graph, "astar", "h_zero", 1.0, "A* con h_zero"),
        search(graph, "astar", "h_safe", 1.0, "A* con h_safe"),
        search(graph, "astar", "h_exact_demo", 1.0, "A* con h_exact_demo"),
        search(graph, "greedy", "h_safe", 1.0, "Greedy con h_safe"),
        search(graph, "weighted_astar", "h_safe", weight, "Weighted A* con h_safe"),
        search(graph, "astar", "h_bad_overestimate", 1.0, "A* con h_bad_overestimate"),
    ]

    report = {
        "graph": graph["name"],
        "start": graph["start"],
        "goal": graph["goal"],
        "h_star": h_star,
        "audits": audits,
        "searches": searches,
    }

    output_dir = ROOT / "output"
    if args.write:
        output_dir.mkdir(exist_ok=True)
        (output_dir / "heuristic_report.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (output_dir / "heuristic_decision.md").write_text(
            render_markdown(graph, h_star, audits, searches) + "\n",
            encoding="utf-8",
        )

    audits_by_name = {audit["heuristic"]: audit for audit in audits}
    optimal_cost = h_star[graph["start"]]
    required_errors = []
    for name in policy["required_heuristics"]:
        audit = audits_by_name[name]
        if not (audit["admissible"] and audit["consistent"] and audit["goal_zero"]):
            required_errors.append(f"{name} no pasa auditoría")

    for name in policy["demo_inadmissible_heuristics"]:
        if audits_by_name[name]["admissible"]:
            required_errors.append(f"{name} debería fallar como contraejemplo")

    search_by_algorithm = {row["algorithm"]: row for row in searches}
    for name in ["UCS", "A* con h_zero", "A* con h_safe", "A* con h_exact_demo"]:
        row = search_by_algorithm[name]
        if not row["found"] or abs(row["cost"] - optimal_cost) > EPSILON:
            required_errors.append(f"{name} no devuelve el coste óptimo {optimal_cost}")

    weighted = search_by_algorithm["Weighted A* con h_safe"]
    if weighted["cost"] <= optimal_cost + EPSILON:
        required_errors.append("Weighted A* debería mostrar pérdida de optimalidad en este fixture")

    if len(searches) < policy["minimum_searches"]:
        required_errors.append("faltan búsquedas comparadas")

    print(f"heuristicas: {len(audits)}")
    print(f"busquedas: {len(searches)}")
    print(f"coste_optimo: {optimal_cost}")
    print(f"errores_gate: {len(required_errors)}")
    print(f"salida: {output_dir if args.write else 'no escrita'}")

    if args.fail_on_invalid and required_errors:
        for error in required_errors:
            print(f"ERROR: {error}")
        raise SystemExit(2)


if __name__ == "__main__":
    main()
