# Maduración de métricas

## Deltas por ventana

| Ventana | Métrica | Control | Treatment | Delta |
|---|---|---:|---:|---:|
| `day_1` | `resolved_rate` | `0.5` | `0.833333` | `0.333333` |
| `day_1` | `followup_needed_rate` | `0.666667` | `0.666667` | `0.0` |
| `day_1` | `student_satisfied_rate` | `0.333333` | `0.333333` | `0.0` |
| `day_7` | `resolved_rate` | `0.5` | `0.833333` | `0.333333` |
| `day_7` | `followup_needed_rate` | `0.5` | `0.166667` | `-0.333333` |
| `day_7` | `student_satisfied_rate` | `0.5` | `0.833333` | `0.333333` |

## Lectura

Una metrica temprana puede contar una historia incompleta. En este ejemplo, satisfaction mejora claramente en day_7 porque algunos casos que parecian incomodos en day_1 se estabilizan después.
