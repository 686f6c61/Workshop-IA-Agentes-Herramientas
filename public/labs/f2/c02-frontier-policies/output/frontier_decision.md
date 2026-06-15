# Decisión: políticas de frontera

Grafo: `frontier_policy_demo`. Inicio `S`, meta `G`.

| Algoritmo | Camino | Profundidad | Coste | Expandidos | Generados | Frontera máx. |
|---|---|---:|---:|---:|---:|---:|
| BFS | S -> B -> G | 2 | 22 | 8 | 8 | 5 |
| DFS | S -> A -> D -> G | 3 | 12 | 4 | 7 | 4 |
| UCS | S -> B -> F -> G | 3 | 6 | 6 | 10 | 5 |
| IDS | S -> B -> G | 2 | 22 | 12 | 13 | 4 |

## Trazas

- **BFS**: S -> A -> B -> C -> D -> E -> F -> G
- **DFS**: S -> A -> D -> G
- **UCS**: S -> A -> B -> D -> F -> G
- **IDS**: L0:S -> L1:S -> L1:A -> L1:B -> L1:C -> L2:S -> L2:A -> L2:D -> L2:E -> L2:B -> L2:F -> L2:G

## Lectura técnica

- El menor coste encontrado lo da **UCS** con coste 6.
- La menor profundidad encontrada la da **BFS** con profundidad 2.
- BFS optimiza pasos solo cuando los costes son uniformes.
- DFS depende del orden de sucesores y no debería usarse sin límite en espacios infinitos.
- UCS ordena por coste acumulado y es la referencia cuando los costes son positivos y no hay heurística.
- IDS reexplora nodos, pero controla memoria con límites crecientes.
