# Decisión de política bandit

Decisión: `piloto_limitado`.
Política seleccionada: `greedy`.

| Política | Recompensa acumulada | Regret | Revisión humana |
|---|---:|---:|---:|
| `greedy` | 23.0 | 0.22 | 0.0333 |
| `epsilon_greedy` | 22.54 | 0.68 | 0.0667 |
| `ucb` | 21.21 | 2.01 | 0.3333 |

## Motivo

`greedy` alcanza recompensa acumulada `23.0`, regret `0.22` y mantiene revisión humana en `0.0333` del tráfico simulado.

## Límites de piloto

- Activar solo en solicitudes de baja criticidad.
- Mantener política fija de reserva y runbook de rollback.
- Cortar exploración si el regret de ventana supera el umbral.
- Guardar traza de ronda, acción, recompensa y razón de selección.
