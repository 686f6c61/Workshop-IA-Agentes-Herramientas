# Entrega del kit: Kit F8 C01: contrato de dataset y linaje

## 0. Archivos del ZIP que he usado

- Entradas: `data/production_sample.csv`, `data/support_cases.csv`, `data/preference_pairs.jsonl` y `data/rag_documents.jsonl`.
- Contratos o políticas: `contracts/data_contract.json` y `contracts/odcs_like_contract.yaml`.
- Código ejecutado: `ops/data/audit_dataset_contract.py` y `ops/data/compare_drift.py`.
- Evidencias generadas: `output/data_release_decision.md`, `output/dataset_card.md`, `output/drift_decision.md`, `output/data_quality_report.json`, `output/data_release_gate.json` y `output/drift_report.json`.

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
