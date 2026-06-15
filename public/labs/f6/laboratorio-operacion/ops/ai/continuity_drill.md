# Continuity drill: degradación de servicio IA

## Objetivo

Ensayar una degradación controlada del servicio `support-rag` para comprobar si el equipo sabe detectar síntomas, aplicar mitigaciones y dejar evidencia suficiente para no repetir el fallo.

## Escenario

Durante una ventana de canary, la ruta principal `provider_a` sube a 6,9 segundos de p95, el índice RAG candidato reduce la aceptación de citas al 71 % y la cola de revisión alcanza 52 minutos de p95.

## Roles

| Rol | Responsabilidad |
|---|---|
| Incident lead | Coordina decisiones y marca tiempos. |
| Operación | Revisa SLI, SLO, trazas y presupuesto de error. |
| IA/RAG | Comprueba índice, citas, retrieval y casos de regresión. |
| Producto | Decide si se degrada funcionalidad o se limita tráfico. |

## Pasos

1. Ejecuta `python3 ops/run_continuity_drill.py --write`.
2. Abre `output/continuity_decision.md` y localiza qué SLO se rompe.
3. Aplica tres decisiones: mover tráfico a `provider_b`, volver al índice estable y activar `review_queue_only` para casos no críticos.
4. Registra un caso nuevo en `evals/regression_cases.jsonl`.
5. Actualiza `postmortem.md` con causa, impacto, decisiones y acciones preventivas.

## Criterio de cierre

El ensayo se considera cerrado cuando hay decisión de continuidad, postmortem, caso de regresión y evidencia de que el gate de CI puede detectar el mismo patrón.
