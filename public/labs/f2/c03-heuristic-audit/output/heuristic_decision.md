# Decisión: auditoría de heurísticas

Grafo: `rutas-con-heuristicas`. Inicio `S`, meta `G`.

## Coste óptimo real desde cada nodo

| Nodo | h*(n) | Lectura |
|---|---:|---|
| A | 9 | Referencia para auditar h(n). |
| B | 4 | Referencia para auditar h(n). |
| C | 1 | Referencia para auditar h(n). |
| D | 10 | Referencia para auditar h(n). |
| E | 1 | Referencia para auditar h(n). |
| F | 2 | Referencia para auditar h(n). |
| G | 0 | Referencia para auditar h(n). |
| S | 6 | Referencia para auditar h(n). |

## Auditoría de heurísticas

| Heurística | Admisible | Consistente | Meta a cero | Violaciones | Domina a |
|---|---|---|---|---:|---|
| h_zero | sí | sí | sí | 0 | nadie |
| h_safe | sí | sí | sí | 0 | h_zero |
| h_exact_demo | sí | sí | sí | 0 | h_zero, h_safe |
| h_bad_overestimate | no | no | sí | 3 | nadie |

## Búsquedas comparadas

| Algoritmo | Heurística | w | Camino | Coste | Óptimo | Expandidos | Generados | Frontera máx. |
|---|---|---:|---|---:|---|---:|---:|---:|
| UCS | h_zero | 1.0 | S -> B -> F -> G | 6 | sí | 7 | 10 | 5 |
| A* con h_zero | h_zero | 1.0 | S -> B -> F -> G | 6 | sí | 7 | 10 | 5 |
| A* con h_safe | h_safe | 1.0 | S -> B -> F -> G | 6 | sí | 5 | 9 | 5 |
| A* con h_exact_demo | h_exact_demo | 1.0 | S -> B -> F -> G | 6 | sí | 4 | 7 | 4 |
| Greedy con h_safe | h_safe | 1.0 | S -> C -> G | 7 | no | 3 | 5 | 3 |
| Weighted A* con h_safe | h_safe | 2.0 | S -> C -> G | 7 | no | 4 | 7 | 4 |
| A* con h_bad_overestimate | h_bad_overestimate | 1.0 | S -> C -> G | 7 | no | 4 | 7 | 4 |

## Trazas

- **UCS**: S(g=0, h=0, f=0) -> A(g=1, h=0, f=1) -> B(g=2, h=0, f=2) -> D(g=2, h=0, f=2) -> F(g=4, h=0, f=4) -> C(g=6, h=0, f=6) -> G(g=6, h=0, f=6)
- **A* con h_zero**: S(g=0, h=0, f=0) -> A(g=1, h=0, f=1) -> B(g=2, h=0, f=2) -> D(g=2, h=0, f=2) -> F(g=4, h=0, f=4) -> C(g=6, h=0, f=6) -> G(g=6, h=0, f=6)
- **A* con h_safe**: S(g=0, h=4, f=4) -> A(g=1, h=3, f=4) -> B(g=2, h=4, f=6) -> F(g=4, h=2, f=6) -> G(g=6, h=0, f=6)
- **A* con h_exact_demo**: S(g=0, h=6, f=6) -> B(g=2, h=4, f=6) -> F(g=4, h=2, f=6) -> G(g=6, h=0, f=6)
- **Greedy con h_safe**: S(g=0, h=4, f=4) -> C(g=6, h=1, f=1) -> G(g=7, h=0, f=0)
- **Weighted A* con h_safe**: S(g=0, h=4, f=8.0) -> A(g=1, h=3, f=7.0) -> C(g=6, h=1, f=8.0) -> G(g=7, h=0, f=7.0)
- **A* con h_bad_overestimate**: S(g=0, h=4, f=4) -> A(g=1, h=3, f=4) -> C(g=6, h=1, f=7) -> G(g=7, h=0, f=7)

## Lectura técnica

- `h_zero` convierte A* en UCS: no informa nada, pero conserva optimalidad.
- `h_safe` no sobreestima y es consistente: A* mantiene garantías y reduce expansiones frente a una búsqueda sin información.
- `h_exact_demo` coincide con `h*(n)`: enseña el límite ideal, aunque calcularlo normalmente equivale a resolver el problema.
- Greedy mira solo `h(n)`: en este grafo llega a `S -> C -> G` con coste 7, una solución rápida pero peor que la óptima.
- Weighted A* con `w=2.0` también devuelve coste 7: al inflar la heurística, expande menos, pero sacrifica la garantía de optimalidad.
- `h_bad_overestimate` sobreestima nodos clave. Sirve como contraejemplo: si una heurística no pasa auditoría, no debe sostener promesas de coste mínimo.
