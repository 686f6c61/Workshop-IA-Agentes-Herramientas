# Kit F8 C06: DataOps, drift y monitorización

Este kit acompaña el capítulo 06 del facsímil 8. Simula dos ventanas de producción de un sistema de decisión: una ventana sana y otra con cambio de distribución, latencia alta, trazas incompletas y pérdida en slices críticos.

La práctica no entrena un modelo. Audita si una ventana de producción es suficientemente trazable y estable para sostener decisiones.

## Ejecutar

Desde esta carpeta:

```bash
python3 ops/monitor_dataops.py --write
cat output/operational_decision.md
cat output/alerts.md
python3 -m json.tool output/monitoring_report.json
```

Para revisar trazas, idempotencia, spans obligatorios y generar postmortem:

```bash
python3 ops/inspect_pipeline_engineering.py --write
cat output/incident_postmortem.md
python3 -m json.tool output/trace_correlation_report.json
```

## Archivos

| Archivo | Papel |
|---|---|
| `data/reference_events.csv` | Ventana de referencia usada como baseline operativo. |
| `data/production_events.csv` | Ventanas de producción a monitorizar. |
| `data/trace_spans.csv` | Spans de trazas para eventos concretos. |
| `contracts/monitoring_contract.json` | Columnas, valores permitidos, slices críticos y SLOs. |
| `contracts/pipeline_engineering_contract.json` | Idempotencia, spans obligatorios, SLOs de trazas y política de evolución. |
| `contracts/runbook.md` | Plantilla de respuesta cuando el gate queda en `review` o `block`. |
| `ops/monitor_dataops.py` | Calcula drift, SLIs, scorecard, alertas y evento de linaje. |
| `ops/inspect_pipeline_engineering.py` | Revisa trazas, orden de spans, duraciones, idempotencia y genera postmortem. |
| `output/monitoring_report.json` | Reporte completo para máquina o CI. |
| `output/slo_scorecard.csv` | Tabla por ventana con estado y SLIs principales. |
| `output/alerts.md` | Alertas humanas ordenadas por ventana. |
| `output/operational_decision.md` | Decisión operativa explicada. |
| `output/lineage_event.json` | Evento de linaje estilo OpenLineage simplificado. |
| `output/trace_correlation_report.json` | Reporte de trazas, spans faltantes, duraciones y flags. |
| `output/trace_scorecard.csv` | Tabla por evento con salud de la traza. |
| `output/incident_postmortem.md` | Postmortem reproducible a partir de alertas y trazas. |

## Qué deberías mirar

1. `2026-06-07` queda en `pass`: la ventana parece estable.
2. `2026-06-08` queda en `block`: hay trace faltante, latencia alta, drift y perdida.
3. `language=en`, `access_need=si` y `product=practicas` explican por qué no basta la media.
4. `lineage_event.json` deja rastro de inputs, outputs, hashes, job y run.
5. `runbook.md` convierte una alerta en acción revisable.
6. `trace_correlation_report.json` muestra eventos sin traza, spans lentos y spans obligatorios que faltan.
7. `incident_postmortem.md` convierte el fallo en timeline, impacto, causa probable y acciones.

## Tests que deberías poder diseñar

| Test | Condición esperada |
|---|---|
| Contrato de datos | Todas las columnas obligatorias de `monitoring_contract.json` existen y respetan catálogos. |
| Contrato de trazas | Los eventos críticos tienen spans `ingest`, `validate`, `score`, `decide` y `emit`. |
| Idempotencia | No hay claves duplicadas con `window + event_id`. |
| Replay | Reprocesar una ventana conocida mantiene la misma decisión operativa. |
| Slices críticos | `language=en`, `access_need=si` y `product=practicas` no quedan escondidos por la media. |
| Backfill seguro | La versión de pipeline, contrato y datos queda fijada antes de recalcular histórico. |

## Cómo lo llevarías a un proyecto real

1. Cambia `production_events.csv` por una muestra de tus eventos reales.
2. Reescribe `monitoring_contract.json` con tus columnas, catalogos, slices y SLOs.
3. Reescribe `pipeline_engineering_contract.json` con tus spans obligatorios y política de retries.
4. Ejecuta los dos scripts en CI antes de aceptar una nueva ventana.
5. Guarda los outputs como evidencia de la run.
6. Convierte cada fallo repetido en un test nuevo o en una regla de gate.

## Qué te llevas

Te llevas una práctica ejecutable sobre DataOps, drift y monitorización, con datos editables, contratos y umbrales, plantillas de entrega, código ejecutable y tests reproducibles. Trabajas con `data/production_events.csv` y `data/reference_events.csv`, contrastas la decisión contra `contracts/runbook.md` y `contracts/monitoring_contract.json` y ejecutas `ops/inspect_pipeline_engineering.py` para generar `output/alerts.md`. La idea no es mirar una solución cerrada: es cambiar una entrada, volver a ejecutar, comparar la salida y poder defender qué harías en una revisión técnica, una asignatura o un piloto real.

## Qué entregaría un alumno

1. `operational_decision.md` generado.
2. `slo_scorecard.csv` interpretado con sus palabras.
3. Un cambio razonado en `monitoring_contract.json`.
4. Un nuevo SLI por slice para su proyecto.
5. Una adaptación de `runbook.md` con owner, acción y criterio de salida.
6. Una explicación de por qué no se debe usar la ventana `2026-06-08` para aumentar automatización.
7. Un postmortem con acción correctiva y test nuevo que habría evitado repetir el problema.
8. Una propuesta de contrato de spans para su propio pipeline.

## Variantes para hacerlo tuyo

- Ejecuta `make run` sin tocar nada y usa `output/alerts.md` como línea base.
- Cambia o añade un caso en `data/production_events.csv` y `data/reference_events.csv` para representar un problema de tu trabajo, clase o producto.
- Endurece una regla, umbral o campo obligatorio en `contracts/runbook.md` y `contracts/monitoring_contract.json` y explica por qué el resultado debería cambiar o bloquearse.
- Compara antes/después en `output/alerts.md` y `output/incident_postmortem.md` y escribe una decisión de una página: seguir, bloquear, medir más o cambiar el diseño.
- Completa `templates/entrega.md` con contexto, cambio, evidencia, decisión y límite; no la dejes como checklist vacía.

## Rúbrica rápida

| Nivel | Qué demuestra |
|---|---|
| Mínimo | Ejecuta `make run` y `make test`, localiza `ops/inspect_pipeline_engineering.py`, abre `output/alerts.md` y explica qué decisión o señal produce. |
| Bueno | Cambia `data/production_events.csv`, compara antes/después y justifica la diferencia con una evidencia concreta del output. |
| Excelente | Convierte el kit en un mini caso profesional: añade un caso propio, ajusta una regla o test, documenta el límite principal y deja una recomendación accionable para un equipo. |

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `Kit F8 C06: DataOps, drift y monitorización`, no escondido en una ruta del repositorio.

### Qué contiene

- `README.md`: esta guía y la explicación del ejercicio.
- `Makefile`: entrada única para ejecutar y validar el kit con `make run` y `make test`.
- `requirements.txt`: dependencias declaradas; muchos kits solo usan la biblioteca estándar de Python.
- `data/`: datos de entrada o casos de prueba realistas. Ejemplos dentro del ZIP: `data/production_events.csv`, `data/reference_events.csv`, `data/trace_spans.csv`.
- `contracts/`: contratos de datos, salida, política o validación. Ejemplos dentro del ZIP: `contracts/runbook.md`, `contracts/monitoring_contract.json`, `contracts/pipeline_engineering_contract.json`.
- `templates/`: plantillas editables para la entrega. Ejemplos dentro del ZIP: `templates/entrega.md`.
- `ops/`: código ejecutable del laboratorio. Ejemplos dentro del ZIP: `ops/inspect_pipeline_engineering.py`, `ops/monitor_dataops.py`.
- `tests/`: tests que comprueban que el ejercicio sigue siendo reproducible. Ejemplos dentro del ZIP: `tests/test_lab_contract.py`.
- `output/`: salidas generadas o esperadas que debes revisar. Ejemplos dentro del ZIP: `output/alerts.md`, `output/incident_postmortem.md`, `output/operational_decision.md`, `output/lineage_event.json`, ....

### Ejecutar desde cero

Desde la carpeta extraída del ZIP:

```bash
make run
make test
```

`make run` construye las evidencias del ejercicio. `make test` comprueba que el kit sigue siendo ejecutable después de descargarlo, extraerlo y tocarlo.

### Qué mirar antes de entregar

- `output/alerts.md`: lectura humana de la decisión, informe o runbook.
- `output/incident_postmortem.md`: lectura humana de la decisión, informe o runbook.
- `output/operational_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/lineage_event.json`: evidencia estructurada para validar o automatizar.
- `output/monitoring_report.json`: evidencia estructurada para validar o automatizar.
- `output/trace_correlation_report.json`: evidencia estructurada para validar o automatizar.
- `output/slo_scorecard.csv`: tabla que puedes inspeccionar o cargar en un notebook.
- `output/trace_scorecard.csv`: tabla que puedes inspeccionar o cargar en un notebook.

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
