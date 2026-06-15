# Decisión de readiness operacional

Servicio: `support-rag`.
Release: `support-rag@2.0.0`.
Gate: **ready**.
Score: `1.0`.

## Checks

| Sección | Estado | Peso | Siguiente acción |
|---|---|---:|---|
| `identity` | pasa | 4 / 4 | ok |
| `slo` | pasa | 8 / 8 | ok |
| `observability` | pasa | 7 / 7 | ok |
| `rollback` | pasa | 6 / 6 | ok |
| `evalops` | pasa | 6 / 6 | ok |
| `incident` | pasa | 5 / 5 | ok |
| `continuity` | pasa | 5 / 5 | ok |
| `handoff` | pasa | 4 / 4 | ok |

## Decisión

Publicaría la release si el gate de EvalOps también compara baseline contra candidate el mismo día.
