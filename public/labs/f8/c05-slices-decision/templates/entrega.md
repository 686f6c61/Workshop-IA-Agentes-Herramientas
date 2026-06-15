# Entrega del kit: Kit F8 C05: slices, sesgos y decisión algorítmica

## 0. Archivos del ZIP que he usado

- Entradas: `data/decision_predictions.csv`.
- Contratos o políticas: `contracts/bias_audit_playbook.md`, `contracts/slice_decision_policy.json` y `contracts/slice_decision_policy_review_band.json`.
- Código ejecutado: `ops/audit_decision_slices.py`, `ops/audit_with_fairlearn.py` y `ops/compare_mitigation.py`.
- Evidencias generadas: `output/mitigation_before_after.md`, `output/slice_audit_card.md`, `output/slice_decision.md`, `output/fairlearn_metricframe.json`, `output/mitigation_before_after.json` y `output/slice_audit_report.json`.

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
