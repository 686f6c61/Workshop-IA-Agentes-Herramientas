# Decisión C10: Evaluación de agentes y gates

Estado: `valid`.

## Evidencias

- OK: métricas de trayectoria. No se mira solo la respuesta final.
- OK: gates pasan. La versión puede avanzar a canary.
- OK: coste limitado. El gate incluye presupuesto.
- OK: latencia limitada. El gate incluye experiencia de usuario.

## Qué te llevas

Un gate de evaluación que mira trayectoria, permisos, coste y latencia.

## Decisión

La versión puede pasar a canary: ruta, tools, aprobación, trazas, coste y latencia cumplen el contrato mínimo.
