# Memo técnico de decision de datos

Decisión recomendada: `review`.

## Motivo

No hay controles bloqueantes, pero quedan revisiones abiertas. El sistema solo podría avanzar con alcance limitado y nuevo gate.

## Checks abiertos

| Check | Estado | Valor | Umbral |
|---|---|---:|---:|
| `latency_p95_ms` | `review` | `730.0` | `720` |
| `test_accuracy` | `review` | `0.6` | `0.75` |
| `critical_slice_miss_rate:language=en` | `review` | `0.8` | `0.25` |
| `critical_slice_miss_rate:segment=practicas` | `review` | `0.75` | `0.25` |
| `critical_slice_miss_rate:source=form` | `review` | `0.666667` | `0.25` |

## Recomendación operativa

No se cambian umbrales después de mirar el resultado. Se corrige trazabilidad, ingesta, slices o experimento, y después se repite el gate con el mismo contrato.
