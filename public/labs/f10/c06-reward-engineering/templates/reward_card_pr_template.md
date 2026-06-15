# Cambio de reward card

## Contexto

- Reward card anterior:
- Reward card nueva:
- Política o modelo afectado:
- Dataset de evaluación:
- Graders y verificadores:

## Qué cambia

| Elemento | Antes | Ahora | Motivo |
|---|---|---|---|
| Objetivo |  |  |  |
| Términos |  |  |  |
| Pesos |  |  |  |
| Restricciones duras |  |  |  |
| Casos |  |  |  |
| Umbral |  |  |  |

## Evidencia

Pega o enlaza los artefactos generados por el kit:

- `output/reward_card_decision.md`
- `output/reward_card_audit_report.json`
- `output/case_scorecard.csv`
- `output/sensitivity_report.csv`
- `output/threshold_calibration.csv`
- `output/threshold_recommendation.md`
- `output/grader_confusion_matrix.csv`
- `output/trace_validation_report.json`

## Lectura de sensibilidad

- Casos que cambian de ganador:
- Cambio esperado o inesperado:
- Decisión tomada:

## Calibración de umbral

- Umbral recomendado por slice:
- Falsos pases aceptables:
- Falsos bloqueos aceptables:
- Casos que requieren revisión humana:

## Trazas y operación

- Campos nuevos de traza:
- Versiones que se guardan:
- Métricas que se monitorizan tras publicar:
- Criterio de rollback:

## Riesgo residual

- Qué no cubre esta reward card:
- Qué slices siguen poco representados:
- Qué verificadores necesitan más evaluación:

## Checklist

- [ ] `python3 ops/audit_reward_card.py --write` devuelve `status=pass`.
- [ ] `python3 ops/fail_ci_if_blocked.py --report output/reward_card_audit_report.json` devuelve código 0.
- [ ] `python3 ops/reward_weight_sweep.py` genera sensibilidad revisada.
- [ ] `python3 ops/calibrate_thresholds.py --write` genera umbrales revisados.
- [ ] `python3 ops/validate_trace.py --write` valida una traza de ejemplo.
- [ ] La matriz del verificador tiene falsos pases revisados.
- [ ] Los cambios de ganador estan explicados.
- [ ] La reward card y el dataset quedan versionados juntos.
