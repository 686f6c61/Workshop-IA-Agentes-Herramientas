# Kit f9/c02: privacidad, minimización, EIPD/DPIA y memoria

Este kit convierte el capítulo 02 del facsímil 09 en una práctica de ingeniería. La pregunta no es "tenemos privacidad", sino: qué dato entra, con qué finalidad, dónde se guarda, cuánto tiempo vive, qué memoria toca y qué evidencia existe.

## Qué vas a crear

| Archivo | Para qué sirve |
|---|---|
| `contracts/privacy_policy.json` | Define umbrales, allowlists por finalidad, retenciones esperadas y señales de EIPD/DPIA. |
| `data/data_flows.csv` | Inventario de flujos entre prompt, RAG, memoria, observabilidad, proveedor y entrenamiento. |
| `data/sample_traces.jsonl` | Trazas de ejemplo con datos ficticios para practicar redacción. |
| `output/data_flow_inventory.json` | Inventario enriquecido con puntuación de privacidad y señales de revisión. |
| `output/data_flow_map.md` | Mapa legible de flujos, finalidades, memoria, retención y owner. |
| `output/minimization_report.md` | Campos permitidos, campos a transformar y criterio de minimización. |
| `output/dpia_precheck.md` | Prechequeo EIPD/DPIA con señales técnicas. |
| `output/retention_plan.csv` | Plan de retención por tipo de memoria y acción recomendada. |
| `output/redacted_trace_sample.jsonl` | Trazas redactadas para revisar observabilidad sin conservar más de lo necesario. |
| `output/presidio_style_findings.json` | Hallazgos de PII con entidad, span, score, reconocedor, hash y operador recomendado. |
| `output/presidio_detection_report.md` | Informe técnico inspirado en Presidio para revisar detección, contexto y operadores. |
| `output/privacy_release_gate.md` | Decisión de salida con bloqueos y evidencias obligatorias. |
| `output/ci_privacy_gate.json` | Resultado máquina para pipeline de CI. |
| `output/ci_privacy_gate.md` | Resultado legible con hallazgos bloqueantes. |

## Cómo ejecutarlo

Desde está carpeta:

```bash
python3 ops/build_privacy_pack.py --write
python3 ops/privacy_ci_gate.py --write
```

No necesita dependencias externas. Usa solo la biblioteca estándar de Python.

Para usarlo como gate de CI real:

```bash
python3 ops/privacy_ci_gate.py --write --fail-on-blocker
```

## Qué deberías ver

El script imprimirá algo parecido a:

```text
flujos: 6
altos: 3
prechequeo_dpia: 5
decisión: revisar_antes_de_publicar
```

Después, el gate CI imprimirá:

```text
estado: fail
hallazgos: 5
```

La decisión esperada en este dataset es conservadora porque hay trazas con texto bruto retenidas demasiado tiempo y un intento de usar tickets con datos personales para entrenamiento.

## Cómo adaptarlo a tu caso

1. Cambia `contracts/privacy_policy.json` para ajustar retenciones, finalidades y campos permitidos.
2. Sustituye `data/data_flows.csv` por los flujos de tu sistema: prompt, RAG, memoria, tools, logs, proveedor, backups, datasets y entrenamiento.
3. Añade trazas reales solo después de redactarlas o con datos de prueba. El kit incluye datos ficticios para practicar.
4. Ejecuta el script y revisa `output/privacy_release_gate.md`.
5. Revisa `output/presidio_detection_report.md` y decide si faltan reconocedores de dominio: DNI/NIE, expediente, matrícula, teléfono local o identificadores internos.
6. Ejecuta `ops/privacy_ci_gate.py` y decide qué hallazgo convertirías en tarea de ingeniería.

## Entregable de alumno

Un entregable serio incluye:

1. `data_flow_map.md` explicado con tus palabras.
2. `minimization_report.md` con al menos tres decisiones de eliminación, redacción o justificación.
3. `dpia_precheck.md` indicando qué señales justifican revisión formal.
4. `retention_plan.csv` ajustado a tu caso.
5. `redacted_trace_sample.jsonl` sin correos, teléfonos ni identificadores directos.
6. `presidio_detection_report.md` explicando entidades detectadas, operador elegido y qué falso negativo buscarías en una evaluación real.
7. `ci_privacy_gate.md` explicando por qué el sistema pasa o falla.
8. Una decisión final: publicar, publicar con condiciones o revisar antes.

## Qué te llevas

Te llevas una práctica ejecutable sobre privacidad, minimización, EIPD/DPIA y memoria, con datos editables, contratos y umbrales, plantillas de entrega, código ejecutable y tests reproducibles. Trabajas con `data/data_flows.csv` y `data/sample_traces.jsonl`, contrastas la decisión contra `contracts/privacy_policy.json` y ejecutas `ops/build_privacy_pack.py` para generar `output/ci_privacy_gate.md`. La idea no es mirar una solución cerrada: es cambiar una entrada, volver a ejecutar, comparar la salida y poder defender qué harías en una revisión técnica, una asignatura o un piloto real.

## Variantes para hacerlo tuyo

- Ejecuta `make run` sin tocar nada y usa `output/ci_privacy_gate.md` como línea base.
- Cambia o añade un caso en `data/data_flows.csv` y `data/sample_traces.jsonl` para representar un problema de tu trabajo, clase o producto.
- Endurece una regla, umbral o campo obligatorio en `contracts/privacy_policy.json` y explica por qué el resultado debería cambiar o bloquearse.
- Compara antes/después en `output/ci_privacy_gate.md` y `output/data_flow_map.md` y escribe una decisión de una página: seguir, bloquear, medir más o cambiar el diseño.
- Completa `templates/entrega.md` con contexto, cambio, evidencia, decisión y límite; no la dejes como checklist vacía.

## Rúbrica rápida

| Nivel | Qué demuestra |
|---|---|
| Mínimo | Ejecuta `make run` y `make test`, localiza `ops/build_privacy_pack.py`, abre `output/ci_privacy_gate.md` y explica qué decisión o señal produce. |
| Bueno | Cambia `data/data_flows.csv`, compara antes/después y justifica la diferencia con una evidencia concreta del output. |
| Excelente | Convierte el kit en un mini caso profesional: añade un caso propio, ajusta una regla o test, documenta el límite principal y deja una recomendación accionable para un equipo. |

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `Kit f9/c02: privacidad, minimización, EIPD/DPIA y memoria`, no escondido en una ruta del repositorio.

### Qué contiene

- `README.md`: esta guía y la explicación del ejercicio.
- `Makefile`: entrada única para ejecutar y validar el kit con `make run` y `make test`.
- `requirements.txt`: dependencias declaradas; muchos kits solo usan la biblioteca estándar de Python.
- `data/`: datos de entrada o casos de prueba realistas. Ejemplos dentro del ZIP: `data/sample_traces.jsonl`, `data/data_flows.csv`.
- `contracts/`: contratos de datos, salida, política o validación. Ejemplos dentro del ZIP: `contracts/privacy_policy.json`.
- `templates/`: plantillas editables para la entrega. Ejemplos dentro del ZIP: `templates/entrega.md`.
- `ops/`: código ejecutable del laboratorio. Ejemplos dentro del ZIP: `ops/build_privacy_pack.py`, `ops/privacy_ci_gate.py`.
- `tests/`: tests que comprueban que el ejercicio sigue siendo reproducible. Ejemplos dentro del ZIP: `tests/test_lab_contract.py`.
- `output/`: salidas generadas o esperadas que debes revisar. Ejemplos dentro del ZIP: `output/ci_privacy_gate.md`, `output/data_flow_map.md`, `output/dpia_precheck.md`, `output/minimization_report.md`, ....

### Ejecutar desde cero

Desde la carpeta extraída del ZIP:

```bash
make run
make test
```

`make run` construye las evidencias del ejercicio. `make test` comprueba que el kit sigue siendo ejecutable después de descargarlo, extraerlo y tocarlo.

### Qué mirar antes de entregar

- `output/ci_privacy_gate.md`: lectura humana de la decisión, informe o runbook.
- `output/data_flow_map.md`: lectura humana de la decisión, informe o runbook.
- `output/dpia_precheck.md`: lectura humana de la decisión, informe o runbook.
- `output/minimization_report.md`: lectura humana de la decisión, informe o runbook.
- `output/presidio_detection_report.md`: lectura humana de la decisión, informe o runbook.
- `output/privacy_release_gate.md`: lectura humana de la decisión, informe o runbook.
- `output/ci_privacy_gate.json`: evidencia estructurada para validar o automatizar.
- `output/data_flow_inventory.json`: evidencia estructurada para validar o automatizar.
- `output/presidio_style_findings.json`: evidencia estructurada para validar o automatizar.
- `output/redacted_trace_sample.jsonl`: eventos o registros línea a línea.
- `output/retention_plan.csv`: tabla que puedes inspeccionar o cargar en un notebook.

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
