# Rollback plan: support-rag

## Disparadores

- `latency_p95_ms` supera 4200 ms durante la ventana de canary.
- `citation_acceptance_rate` cae por debajo de 0.90.
- `review_queue_age_p95_minutes` supera 30 minutos.
- El gate de readiness devuelve `block_release`.

## Acciones

1. Reducir canary al 0 % para la versión candidata.
2. Cambiar routing crítico a `provider_b`.
3. Restaurar `index_version=stable`.
4. Activar `review_queue_only` para casos no críticos.
5. Registrar decisión en `incident_state.md`.

## Verificación

El rollback se considera válido cuando `output/continuity_report.json` muestra SLO recuperado o cuando el incident lead documenta una razón explícita para mantener la degradación controlada.
