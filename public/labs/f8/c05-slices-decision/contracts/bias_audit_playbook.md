# Playbook de auditoria de sesgos

Este documento acompana el contrato `slice_decision_policy.json`. Sirve para preparar una revisión antes de automatizar una decisión.

## 1. Unidad de decision

Escribe la unidad exacta que se decide:

```text
Unidad: caso de soporte académico
Decisión: priorizar, flujo normal o revisar
Score: riesgo de que el caso requiera atencion prioritaria
```

No mezcles unidades. Un usuario, un caso, un documento, un chunk y una sesion no son equivalentes.

## 2. Fuentes de sesgo que debes revisar

| Fuente | Pregunta de control | Evidencia mínima |
|---|---|---|
| Cobertura | Hay suficientes ejemplos por slice? | Conteos, positivos, negativos e intervalo. |
| Seleccion | Test se parece al uso real? | Comparación train/test/producción. |
| Medicion | El proxy mide el concepto correcto? | Definicion, linaje y revisión de dominio. |
| Etiquetado | La etiqueta se aplica igual en todos los slices? | Politica de anotación y desacuerdo por slice. |
| Representacion | La feature o embedding cubre el segmento? | OOV, top-k, vecinos, calidad por slice. |
| Agregacion | Un promedio oculta subpoblaciones? | Métrica global frente a intersecciones. |
| Politica | El umbral produce consecuencias aceptables? | Coste, revisión, capacidad y gates. |

## 3. Señales detectables

| Señal | Gate sugerido |
|---|---|
| `n` menor que el mínimo | `review` hasta ampliar muestra. |
| `miss_rate` alto en slice crítico | `block` si casos importantes pasan a flujo normal. |
| `auto_recall_gap` alto | `review` y analisis de causa. |
| `review_rate_gap` alto | Revisar capacidad humana y friccion por segmento. |
| `false_positive_rate_gap` alto | Revisar coste de priorizar de más. |
| OOV o top-k pobre | Revisar representación, corpus o encoder. |

## 4. Herramientas por fase

No empieces por comprar o instalar. Empieza por ubicar la fase del problema.

| Fase | Herramientas candidatas | Evidencia que deberían producir | Pregunta de control |
|---|---|---|---|
| Auditoria offline con CSV | Fairlearn, Aequitas, AI Fairness 360 | Métricas por slice, disparidades, tamaño de muestra, tabla exportable. | Puedo reproducir el reporte con el mismo dataset y política? |
| TensorFlow/TFX | Fairness Indicators, What-If Tool | Visualizacion por slices, intervalos y ejemplos problematicos. | Los slices se definen antes de mirar el resultado? |
| Cloud AWS | SageMaker Clarify | Reporte de sesgo, explicabilidad, evaluación y monitorizacion integrada. | El job queda versionado y conectado con release? |
| Cloud Azure | Responsible AI dashboard | Error analysis, fairness, importancia de variables y contrafactuales. | Puedo convertir el panel en una decisión `pass`, `review` o `block`? |
| Produccion con trafico | Evidently, Fiddler, Arize, WhyLabs | Alertas, drift, calidad, slices, trazas, comparación con baseline. | La alerta tiene owner, SLO y runbook? |
| LLM, agente o RAG | Giskard, Evidently, Arize Phoenix, evals propias | Casos de prueba, regresiones de comportamiento, trazas y resultados por criterio. | Los casos representan tareas reales del dominio? |

Regla de adopción: una herramienta debe decir que fila, que slice, que metrica, que versión, que baseline y que acción toca. Si solo muestra una gráfica, aún falta trabajo de ingeniería.

## 5. Mitigacion: elegir la palanca correcta

| Problema observado | Palanca preferente | Accion concreta | Riesgo si eliges mal |
|---|---|---|---|
| Slice con poca muestra | Datos | Recoger más ejemplos o mandar a `review`. | Sacar conclusiones fuertes con poca evidencia. |
| Etiquetas inconsistentes | Medicion | Reescribir guía de etiquetado y medir desacuerdo. | Optimizar contra una verdad mal definida. |
| Proxy fuerte | Representacion | Revisar features, embeddings y correlaciones. | Borrar una columna y dejar proxies vivos. |
| Score útil pero acción injusta | Politica | Ajustar bandas de revisión, umbral o capacidad humana. | Cambiar el modelo cuando el fallo está en la decisión. |
| Drift por canal, idioma o fuente | Monitorizacion | Alerta por slice y comparación con validación. | Mirar solo metrica global en producción. |
| LLM con respuestas distintas por formulacion | Dataset de prueba | Pares mínimos, rubrica, trazas y revisión humana. | Confundir una demo correcta con estabilidad real. |

Mitigar no significa maquillar una metrica. Significa reducir una consecuencia concreta sin romper otra parte importante del sistema.

## 6. Preguntas para comprar o adoptar herramientas

1. Puede ejecutarse con mis datos de validación sin mandar información innecesaria?
2. Exporta CSV, JSON o artefactos que puedan revisarse en una pull request?
3. Permite definir slices propios e intersecciones?
4. Distingue referencia, validación, test y producción?
5. Tiene API para CI/CD o solo interfaz manual?
6. Guarda versión de modelo, dataset, política, umbral y configuracion?
7. Permite delayed ground truth cuando la etiqueta llega días después?
8. Integra permisos para atributos de auditoria?
9. Genera alertas con owner y severidad?
10. Ayuda a diagnosticar causa o solo señala diferencias?
11. Permite comparar dos modelos bajo el mismo contrato?
12. Documenta limitaciones de sus métricas?

## 7. Antes/después de una mitigación

Una mitigación debe compararse contra una política base. No basta con decir que mejora.

| Campo | Politica base | Politica candidata | Lectura obligatoria |
|---|---|---|---|
| `release_status` | `block` | `review` o `pass` | Que decision cambia y por que. |
| `safety_capture` | Valor base | Valor candidato | Si menos casos importantes pasan a flujo normal. |
| `miss_rate` | Valor base | Valor candidato | Si baja la perdida operativa. |
| `review_rate` | Valor base | Valor candidato | Si el equipo puede asumir la carga humana. |
| `cost_per_case` | Valor base | Valor candidato | Si el coste total baja o solo cambia de sitio. |
| Slices críticos | Falla aquí | Mejora o no mejora aquí | Si la solución resuelve el problema real. |

Comando del kit:

```bash
python3 ops/compare_mitigation.py --write
cat output/mitigation_before_after.md
```

## 8. Produccion: convertir slices en SLI y SLO

| SLI por slice | SLO posible | Runbook si falla |
|---|---|---|
| `miss_rate` con etiqueta retrasada | Menor o igual que el gate acordado. | Revisar política y bloquear más automatización. |
| `review_rate` | Dentro de capacidad diaria del equipo. | Ajustar colas, capacidad o banda de revisión. |
| `safety_capture` | Por encima del mínimo del contrato. | Recolectar datos, revisar umbral o reentrenar. |
| Drift de distribución | Distancia respecto a validación bajo limite. | Comparar fuentes, canales e idioma. |
| Tasa de corrección humana | Estable por slice. | Revisar guía de etiquetado y feedback. |

Un SLI es una medida. Un SLO es el objetivo de esa medida. Un runbook dice que se hace cuando no se cumple.

## 9. Buenas practicas

1. Define slices críticos antes de mirar test.
2. Separa campos de modelo y campos de auditoria.
3. Congela umbrales desde validation.
4. Guarda hashes de dataset y política.
5. Mide intersecciones cuando el riesgo pueda concentrarse.
6. Escribe una decisión `pass`, `review` o `block`.
7. Conecta los mismos slices con monitorizacion en producción.
8. Elige herramienta después de definir metrica, coste y gate.
9. Documenta por que una mitigación concreta reduce una consecuencia concreta.
10. Compara siempre política base y política candidata con el mismo dataset y contrato.

## 10. Cosas que evitar

1. Borrar una columna y asumir que desaparece el proxy.
2. Publicar solo slices que apoyan la conclusion.
3. Ajustar umbrales mirando test.
4. Comparar modelos solo por media global.
5. Usar una herramienta como sustituto del criterio de dominio.
6. Ignorar slices con poca muestra.
7. Confundir score alto con decision automáticamente aceptable.
8. Comprar un panel sin API, versionado ni exportacion.
9. Aplicar mitigación sin diagnostico de causa.
10. Llamar justo a un sistema solo porque una metrica salio verde.
11. Presentar una mitigación sin coste de revisión, owner y limite operativo.

## 11. Entregable esperado

Una auditoria mínima debe dejar:

```text
output/slice_audit_report.json
output/slice_metrics.csv
output/slice_decision.md
output/slice_audit_card.md
output/mitigation_before_after.md
output/mitigation_critical_slices.csv
```

Y una respuesta humana:

```text
Que automatizamos?
Que dejamos en revisión?
Que slice impide publicar?
Que datos faltan?
Que se monitoriza después?
```
