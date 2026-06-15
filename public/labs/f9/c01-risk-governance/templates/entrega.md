# Entrega del kit: Kit f9/c01: registro de riesgos, controles y evidencias

## 0. Archivos del ZIP que he usado

- Entradas: `data/risk_scenarios.csv`.
- Contratos o políticas: `contracts/ai_system_context.json` y `contracts/control_policy.json`.
- Código ejecutado: `ops/build_risk_register.py`.
- Evidencias generadas: `output/evidence_pack/evidence_index.md`, `output/evidence_pack/privacy_review.md`, `output/release_gate.md`, `output/risk_register.md`, `output/evidence_pack/release_manifest.json` y `output/risk_register.json`.

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
