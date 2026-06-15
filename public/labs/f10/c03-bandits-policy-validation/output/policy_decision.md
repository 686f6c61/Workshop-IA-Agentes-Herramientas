# Decisión de política bandit

Estado: `pass`
Política seleccionada: `greedy`
Rondas simuladas: 60

| Política | Gate | Recompensa | Regret | Exploración | Coste medio |
|---|---:|---:|---:|---:|---:|
| `greedy` | `True` | 46.63 | 0.27 | 0.05 | 0.1865 |
| `epsilon_greedy` | `True` | 45.95 | 0.95 | 0.1333 | 0.1973 |
| `ucb` | `False` | 43.08 | 3.82 | 0.4833 | 0.2927 |
| `thompson_sampling` | `True` | 46.63 | 0.27 | 0.05 | 0.1865 |

## Lectura

`greedy` pasa los gates y puede proponerse como piloto limitado con feature flag, trazas y rollback.

## Condiciones antes de producción

1. Registrar `action_probability`, contexto, reward y razón de selección en cada ronda.
2. Mantener política estable de reserva para rollback.
3. Revisar regret y coste por ventana.
4. No explorar en slices marcados por contrato.
5. Guardar `bandit_trace.jsonl` para evaluación offline posterior.
