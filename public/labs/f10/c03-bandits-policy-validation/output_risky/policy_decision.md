# Decisión de política bandit

Estado: `review`
Política seleccionada: `greedy`
Rondas simuladas: 60

| Política | Gate | Recompensa | Regret | Exploración | Coste medio |
|---|---:|---:|---:|---:|---:|
| `greedy` | `False` | 40.68 | 3.37 | 0.0333 | 0.1865 |
| `epsilon_greedy` | `False` | 40.33 | 3.72 | 0.0833 | 0.1908 |
| `ucb` | `False` | 40.09 | 3.96 | 0.5667 | 0.3533 |
| `thompson_sampling` | `False` | 40.5 | 3.55 | 0.4 | 0.3403 |

## Lectura

Ninguna política pasa todos los gates. La decisión correcta es revisar reward, límites o escenario antes de mover tráfico.

## Condiciones antes de producción

1. Registrar `action_probability`, contexto, reward y razón de selección en cada ronda.
2. Mantener política estable de reserva para rollback.
3. Revisar regret y coste por ventana.
4. No explorar en slices marcados por contrato.
5. Guardar `bandit_trace.jsonl` para evaluación offline posterior.
