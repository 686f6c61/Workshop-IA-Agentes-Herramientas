# Serving runbook

## Antes de aumentar tráfico

- Comprobar que `serving_decision.md` está en `pass`.
- Revisar `drift_scorecard.csv` por slice, no solo el agregado.
- Confirmar que la política de reserva está versionada y disponible.
- Confirmar que la feature flag puede bajar exposición sin redesplegar.

## Si el gate bloquea

- Decisión de rollback: `route_all_to_fallback_policy`.
- Tiempo máximo de restauración: `10` minutos.
- Congelar el tramo actual y no aumentar tráfico.
- Guardar reporte, ventana actual y plan usado.
- Abrir revisión técnica con slices bloqueados y condiciones incumplidas.

## Condiciones declaradas

- `serving_status=block`
- `p95_latency_ms_over_slo`
- `evidence_pass_rate_below_slo`
- `population_stability_index_over_limit`
- `fallback_rate_over_limit`
