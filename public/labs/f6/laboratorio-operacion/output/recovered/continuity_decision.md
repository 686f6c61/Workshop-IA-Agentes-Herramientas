# Decisión de continuidad

Estado: **recovered**.

## Síntomas

| Métrica | Valor | SLO | Estado | Mitigación |
|---|---:|---:|---|---|
| `latency_p95_ms` | 3900 | 4200 | pass | mantener vigilancia |
| `citation_acceptance_rate` | 0.91 | 0.9 | pass | mantener vigilancia |
| `review_queue_age_p95_minutes` | 27 | 30 | pass | mantener vigilancia |

## Orden de actuación

1. Reducir canary para limitar exposición.
2. Cambiar ruta crítica a fallback si la latencia queda fuera de SLO.
3. Volver al índice estable si cae aceptación de citas.
4. Proteger cola humana con prioridades explícitas.
5. Convertir el caso en regresión antes de cerrar.
