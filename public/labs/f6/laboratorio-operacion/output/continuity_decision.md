# Decisión de continuidad

Estado: **degraded_controlled**.

## Síntomas

| Métrica | Valor | SLO | Estado | Mitigación |
|---|---:|---:|---|---|
| `latency_p95_ms` | 6900 | 4200 | breach | mover ruta crítica a provider_b y reducir canary |
| `citation_acceptance_rate` | 0.71 | 0.9 | breach | volver al índice estable y añadir caso a regresión RAG |
| `review_queue_age_p95_minutes` | 52 | 30 | breach | activar cola de solo revisión crítica y ampliar owner temporal |

## Orden de actuación

1. Reducir canary para limitar exposición.
2. Cambiar ruta crítica a fallback si la latencia queda fuera de SLO.
3. Volver al índice estable si cae aceptación de citas.
4. Proteger cola humana con prioridades explícitas.
5. Convertir el caso en regresión antes de cerrar.
