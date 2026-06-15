# Serving runbook

## Antes de aumentar tráfico

- Comprobar que `serving_decision.md` está en `pass`.
- Revisar `drift_scorecard.csv` por slice, no solo el agregado.
- Confirmar que la política de reserva está versionada y disponible.
- Confirmar que la feature flag puede bajar exposición sin redesplegar.

## Si el gate bloquea

- Decisión de rollback: `manual_redeploy`.
- Tiempo máximo de restauración: `90` minutos.
- Congelar el tramo actual y no aumentar tráfico.
- Guardar reporte, ventana actual y plan usado.
- Abrir revisión técnica con slices bloqueados y condiciones incumplidas.

## Condiciones declaradas

- No hay condiciones suficientes declaradas.
