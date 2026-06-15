# Decisión de readiness operacional

Servicio: `support-rag`.
Release: `support-rag@2.0.0`.
Gate: **not_ready**.
Score: `0.0889`.

## Checks

| Sección | Estado | Peso | Siguiente acción |
|---|---|---:|---|
| `identity` | pasa | 4 / 4 | ok |
| `slo` | falta | 0 / 8 | añadir coste p95 y edad máxima de cola de revisión |
| `observability` | falta | 0 / 7 | completar atributos de traza, dashboards y alertas |
| `rollback` | falta | 0 / 6 | añadir comando probado, fecha de prueba y tiempo máximo de rollback |
| `evalops` | falta | 0 / 6 | añadir datasets de regresión, muestra de producción, baseline y candidate |
| `incident` | falta | 0 / 5 | añadir matriz de severidad y cadencia de comunicación |
| `continuity` | falta | 0 / 5 | añadir RPO, rutas de fallback y drill de continuidad |
| `handoff` | falta | 0 / 4 | añadir tarjeta de aprobación con campos mínimos |

## Decisión

No publicaría. Primero completaría manifiesto, observabilidad, rollback, continuidad y handoff.
