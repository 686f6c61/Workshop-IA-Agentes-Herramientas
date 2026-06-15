# Entrega del kit: Kit F1 C07: pérdida, optimizador y validación

## 0. Archivos del ZIP que he usado

- Entradas: no aplica.
- Contratos o políticas: `contracts/training_grid.json`.
- Código ejecutado: `ops/run_training_grid.py`.
- Evidencias generadas: `output/training_decision.md` y `output/training_report.json`.

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
