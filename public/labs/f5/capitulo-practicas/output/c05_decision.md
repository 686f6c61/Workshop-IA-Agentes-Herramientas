# Decisión C05: Decision record de arquitectura agentic

Estado: `valid`.

## Evidencias

- OK: opciones comparadas. No se elige arquitectura por nombre de moda.
- OK: pesos explícitos. La decisión declara qué importa.
- OK: workflow gana para caso regulado. La trazabilidad pesa más que la flexibilidad.
- OK: queda alternativa. Hay plan si aumenta complejidad multi-paso.

## Qué te llevas

Un ADR para elegir arquitectura agentic por pesos, no por moda.

## Decisión

Para un proceso académico con permisos y trazas, la recomendación inicial es workflow; si aparecen tareas abiertas, se reevalúa planner-executor.
