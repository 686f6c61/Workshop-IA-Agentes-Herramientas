# Entrega del kit: Kit F10 C06: reward engineering y verificadores

## 0. Archivos del ZIP que he usado

- Entradas: `data/reward_run_trace.json`, `data/reward_run_trace_bad.json`, `data/reward_spec.json` y `data/reward_spec_bad.json`.
- Contratos o políticas: `contracts/reward_card_contract.json` y `contracts/reward_run_trace_contract.json`.
- Código ejecutado: `ops/audit_reward_card.py`, `ops/calibrate_thresholds.py`, `ops/fail_ci_if_blocked.py` y `ops/reward_weight_sweep.py`.
- Evidencias generadas: `output/reward_card.md`, `output/reward_card_decision.md`, `output/threshold_recommendation.md`, `output/reward_card_audit_report.json`, `output/trace_validation_report.json` y `output/case_scorecard.csv`.

## 1. Contexto

Describe en tres o cuatro líneas qué caso has decidido estudiar y por qué se parece a un problema real de clase, producto, datos, operación o investigación aplicada.

## 2. Qué he ejecutado

```bash
make run
make test
```

Anota si ambos comandos pasan. Si algo falla, explica qué falla antes de interpretar resultados.

## 3. Qué he cambiado

Indica qué dato, contrato, política, plantilla, umbral o código has tocado. No basta decir "he cambiado el JSON": explica qué representa ese cambio y qué pasaría si ese supuesto apareciera en un sistema real.

## 4. Resultado

Resume los artefactos generados en `output/`: decisión, métricas, trazas, tablas, gates o informes.

## 5. Decisión técnica

Escribe qué harías en un proyecto real: publicar, bloquear, pedir revisión humana, recoger más datos, cambiar un umbral, repetir evaluación o preparar un piloto.

## 6. Riesgos y límites

Explica qué no demuestra el kit, qué supuesto podría romperse y qué dato adicional pedirías antes de confiar más.

## 7. Próximo paso

Propón una mejora pequeña y ejecutable: un caso nuevo, un test, una métrica, una consulta, una política, un runbook o un gate de CI.
