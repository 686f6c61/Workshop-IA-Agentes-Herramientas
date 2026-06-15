# Runbook técnico: `support-rag`

Este runbook es la versión que viviría cerca del código. Está pensado para guardias e ingeniería: comandos, señales y decisiones concretas.

## Señales que abren incidente

| Señal | Umbral | Primera comprobación |
|---|---:|---|
| `latency_p95_ms` | `> 4200` | comparar por `release_id`, `route_id` y proveedor |
| `citation_acceptance_rate` | `< 0.90` | revisar índice, top_k y fuentes recuperadas |
| `review_queue_age_p95_minutes` | `> 30` | activar modo solo crítico |
| `contract_fail_rate` | `> 0.006` | bloquear candidate y revisar schema |

## Comandos del laboratorio

```bash
python3 ops/operational_readiness.py --write
python3 ops/run_continuity_drill.py --write
python3 ops/ai/release_gate.py --write
```

## Orden de mitigación

1. Reducir canary a `0%`.
2. Cambiar ruta crítica a fallback seguro.
3. Restaurar índice estable.
4. Activar cola de revisión solo para casos críticos.
5. Preservar trazas y generar caso de regresión.

## Cierre

No se cierra hasta que el gate de continuidad recuperado pase, exista `postmortem.md` y el caso de regresión esté listo para EvalOps.
