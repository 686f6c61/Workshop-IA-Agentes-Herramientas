# Entrega del kit: Kit F8 C03: splits, muestreo y leakage

## 0. Archivos del ZIP que he usado

- Entradas: `data/model_predictions.csv` y `data/support_split_cases.csv`.
- Contratos o políticas: `contracts/evaluation_use_policy.md`, `contracts/preprocessing_policy.json`, `contracts/rag_llm_eval_policy.json` y `contracts/split_policy.json`.
- Código ejecutado: `ops/evaluate_test_slices.py`, `ops/preprocessing_fit_audit.py` y `ops/split_audit.py`.
- Evidencias generadas: `output/evaluation_slice_decision.md`, `output/preprocessing_fit_decision.md`, `output/split_decision.md`, `output/evaluation_slice_report.json`, `output/preprocessing_fit_report.json` y `output/split_manifest.json`.

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
