# Kit F8 C05: slices, sesgos y decisión algorítmica

Este kit acompaña el capítulo 05 del facsímil 8. Parte de predicciones ya congeladas y audita una política de decisión por slices. No entrena un modelo ni ajusta umbrales con test: mide si la decisión se sostiene por segmentos relevantes.

La práctica produce tres salidas que un equipo podría revisar en una pull request: un reporte JSON, una tabla CSV de slices y una decisión Markdown.

## Ejecutar

Desde esta carpeta:

```bash
python3 ops/audit_decision_slices.py --write
cat output/slice_decision.md
python3 -m json.tool output/slice_audit_report.json
```

Para comparar una mitigación concreta:

```bash
python3 ops/compare_mitigation.py --write
cat output/mitigation_before_after.md
```

La ruta opcional con Fairlearn puede ejecutarse de dos formas. Sin dependencias externas genera un fallback con librería estándar para que siempre exista una lectura por grupo:

```bash
python3 ops/audit_with_fairlearn.py --field access_need --write
python3 -m json.tool output/fairlearn_metricframe.json
```

Si quieres repetir la misma lectura con `MetricFrame` real de Fairlearn, instala dependencias en un entorno virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install pandas fairlearn
python3 ops/audit_with_fairlearn.py --field access_need --write
python3 -m json.tool output/fairlearn_metricframe.json
```

## Archivos

| Archivo | Papel |
|---|---|
| `data/decision_predictions.csv` | Predicciones congeladas con score, etiqueta real, split y metadatos de auditoría. |
| `contracts/slice_decision_policy.json` | Umbrales, campos auditables, costes, mínimos de muestra y gates. |
| `contracts/slice_decision_policy_review_band.json` | Política candidata que amplía banda de revisión para estudiar mitigación. |
| `contracts/bias_audit_playbook.md` | Guía de trabajo: fuentes de sesgo, señales detectables, herramientas por fase, mitigaciones, buenas prácticas y cosas que evitar. |
| `ops/audit_decision_slices.py` | Calcula decisiones, matriz por slice, intervalos, disparidades y veredicto. |
| `ops/compare_mitigation.py` | Compara política base frente a política candidata y genera un antes/después. |
| `ops/audit_with_fairlearn.py` | Ruta opcional para repetir parte de la lectura con Fairlearn `MetricFrame` o fallback estándar. |
| `output/slice_audit_report.json` | Reporte completo para CI, revisión técnica o expediente de release. |
| `output/slice_metrics.csv` | Tabla plana con métricas por slice. |
| `output/slice_decision.md` | Lectura humana: qué se puede hacer y qué no se debe automatizar. |
| `output/slice_audit_card.md` | Ficha corta para adjuntar a model card o data card. |
| `output/mitigation_before_after.md` | Comparación humana entre política base y banda de revisión. |
| `output/mitigation_before_after.csv` | Comparación tabular de estado, captura, pérdida, revisión y coste. |
| `output/mitigation_critical_slices.csv` | Lectura específica de slices críticos antes y después. |

## Qué deberías mirar

1. `overall`: la métrica global puede parecer razonable.
2. `slice_metrics.csv`: algunos slices cuentan otra historia.
3. `disparities`: compara máximos y mínimos entre slices válidos.
4. `flags`: separa problemas de muestra, métrica y coste.
5. `critical_slices`: recuerda que no todos los segmentos pesan igual para la decisión.
6. `fields_not_for_model`: algunos campos se usan para auditar, no para decidir.
7. `bias_audit_playbook.md`: convierte la auditoría en una checklist que puedes adaptar a tu equipo.
8. Matriz de herramientas: decide si tu caso pide Fairlearn, Aequitas, AI Fairness 360, Clarify, Azure Responsible AI, Evidently, Giskard, Fiddler, Arize, WhyLabs u otra pieza equivalente.
9. `mitigation_before_after.md`: muestra que una mitigación puede reducir pérdida, pero aumentar revisión y coste operativo.
10. `fairlearn_metricframe.json`: si no instalas nada, ves un fallback explícito; si instalas Fairlearn, comparas la lectura del kit con una librería profesional.

## Qué te llevas

Te llevas una práctica ejecutable sobre slices, sesgos y decisión algorítmica, con datos editables, contratos y umbrales, plantillas de entrega, código ejecutable y tests reproducibles. Trabajas con `data/decision_predictions.csv`, contrastas la decisión contra `contracts/bias_audit_playbook.md` y `contracts/slice_decision_policy.json` y ejecutas `ops/audit_decision_slices.py` para generar `output/mitigation_before_after.md`. La idea no es mirar una solución cerrada: es cambiar una entrada, volver a ejecutar, comparar la salida y poder defender qué harías en una revisión técnica, una asignatura o un piloto real.

## Qué entregaría un alumno

1. Reporte JSON generado.
2. CSV de slices revisado.
3. Decisión Markdown explicada con sus propias palabras.
4. Cambio razonado en un umbral o gate, sin tocar test para optimizar a ciegas.
5. Dos slices nuevos que tendría sentido auditar en su proyecto.
6. Propuesta de datos adicionales si un slice queda con muestra insuficiente.
7. Playbook adaptado a su dominio con fuentes de sesgo, gates y acciones.
8. Justificación de herramienta: qué fase cubre, qué artefacto produce, qué no sustituye y qué mitigación permite o descarta.
9. Comparación antes/después de una mitigación, con trade-off escrito.
10. Una decisión operativa: publicar, revisar capacidad humana, ampliar datos o cambiar la política.

## Variantes para hacerlo tuyo

- Ejecuta `make run` sin tocar nada y usa `output/mitigation_before_after.md` como línea base.
- Cambia o añade un caso en `data/decision_predictions.csv` para representar un problema de tu trabajo, clase o producto.
- Endurece una regla, umbral o campo obligatorio en `contracts/bias_audit_playbook.md` y `contracts/slice_decision_policy.json` y explica por qué el resultado debería cambiar o bloquearse.
- Compara antes/después en `output/mitigation_before_after.md` y `output/slice_audit_card.md` y escribe una decisión de una página: seguir, bloquear, medir más o cambiar el diseño.
- Completa `templates/entrega.md` con contexto, cambio, evidencia, decisión y límite; no la dejes como checklist vacía.

## Rúbrica rápida

| Nivel | Qué demuestra |
|---|---|
| Mínimo | Ejecuta `make run` y `make test`, localiza `ops/audit_decision_slices.py`, abre `output/mitigation_before_after.md` y explica qué decisión o señal produce. |
| Bueno | Cambia `data/decision_predictions.csv`, compara antes/después y justifica la diferencia con una evidencia concreta del output. |
| Excelente | Convierte el kit en un mini caso profesional: añade un caso propio, ajusta una regla o test, documenta el límite principal y deja una recomendación accionable para un equipo. |

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `Kit F8 C05: slices, sesgos y decisión algorítmica`, no escondido en una ruta del repositorio.

### Qué contiene

- `README.md`: esta guía y la explicación del ejercicio.
- `Makefile`: entrada única para ejecutar y validar el kit con `make run` y `make test`.
- `requirements.txt`: dependencias declaradas; muchos kits solo usan la biblioteca estándar de Python.
- `data/`: datos de entrada o casos de prueba realistas. Ejemplos dentro del ZIP: `data/decision_predictions.csv`.
- `contracts/`: contratos de datos, salida, política o validación. Ejemplos dentro del ZIP: `contracts/bias_audit_playbook.md`, `contracts/slice_decision_policy.json`, `contracts/slice_decision_policy_review_band.json`.
- `templates/`: plantillas editables para la entrega. Ejemplos dentro del ZIP: `templates/entrega.md`.
- `ops/`: código ejecutable del laboratorio. Ejemplos dentro del ZIP: `ops/audit_decision_slices.py`, `ops/audit_with_fairlearn.py`, `ops/compare_mitigation.py`.
- `tests/`: tests que comprueban que el ejercicio sigue siendo reproducible. Ejemplos dentro del ZIP: `tests/test_lab_contract.py`.
- `output/`: salidas generadas o esperadas que debes revisar. Ejemplos dentro del ZIP: `output/mitigation_before_after.md`, `output/slice_audit_card.md`, `output/slice_decision.md`, `output/fairlearn_metricframe.json`, ....

### Ejecutar desde cero

Desde la carpeta extraída del ZIP:

```bash
make run
make test
```

`make run` construye las evidencias del ejercicio. `make test` comprueba que el kit sigue siendo ejecutable después de descargarlo, extraerlo y tocarlo.

### Qué mirar antes de entregar

- `output/mitigation_before_after.md`: lectura humana de la decisión, informe o runbook.
- `output/slice_audit_card.md`: lectura humana de la decisión, informe o runbook.
- `output/slice_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/fairlearn_metricframe.json`: evidencia estructurada para validar o automatizar.
- `output/mitigation_before_after.json`: evidencia estructurada para validar o automatizar.
- `output/slice_audit_report.json`: evidencia estructurada para validar o automatizar.
- `output/mitigation_before_after.csv`: tabla que puedes inspeccionar o cargar en un notebook.
- `output/mitigation_critical_slices.csv`: tabla que puedes inspeccionar o cargar en un notebook.
- `output/slice_metrics.csv`: tabla que puedes inspeccionar o cargar en un notebook.

### Qué entregar

Una entrega útil no es una captura de pantalla. Debe incluir los artefactos generados, la modificación razonada que hayas hecho y una decisión escrita que explique qué harías en un sistema real.

Como mínimo:

1. Resultado de `make test`.
2. Artefactos de `output/` que sostienen tu decisión.
3. Cambio propio en datos, contrato, política, plantilla o código, según el objetivo del kit.
4. Nota técnica breve: qué has probado, qué ha fallado o pasado, y qué decisión tomarías.

### Cómo adaptarlo a tu caso

1. Ejecuta primero `make run` sin tocar nada para obtener la línea base reproducible.
2. Ejecuta `make test` antes de cambiar el ejercicio; así sabes que el ZIP llegó completo.
3. Sustituye o amplía los archivos de `data/` con casos de tu dominio manteniendo el mismo contrato de campos.
4. Ajusta `contracts/` cuando cambien tipos, campos obligatorios, umbrales o catálogos permitidos.
5. Usa `templates/` como base documental; no entregues una plantilla sin completar.
6. Guarda los outputs finales y una nota breve con la decisión técnica que tomarías en un proyecto real.

### Criterio de validación

El kit está completo cuando se puede descargar, extraer, ejecutar con `make run`, validar con `make test` y explicar sin depender de ninguna carpeta externa. Si una práctica menciona código, datos, contrato, CSV, SQL, política o plantilla, ese contenido debe venir dentro del ZIP.
<!-- zip-quality-audit:end -->
