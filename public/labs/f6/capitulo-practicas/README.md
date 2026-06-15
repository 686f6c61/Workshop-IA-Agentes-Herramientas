# Kit F6: prácticas por capítulo

Este kit acompaña los `Manos a la obra` del facsímil 6. Convierte operación de IA en artefactos ejecutables: manifests, contratos de runtime, capacidad, telemetría, routing, gates, rollout, revisión humana e incidencias.

Cada práctica intenta responder a una pregunta de ingeniería: ¿este sistema se puede operar mañana sin depender de memoria tribal? Por eso las salidas no son solo números: son decisiones, gates, acciones y evidencias.

## Ejecutar todo

```bash
python3 ops/run_f6_practices.py --all --write --fail-on-invalid
```

## Ejecutar un capítulo

```bash
python3 ops/run_f6_practices.py --chapter c04 --write --fail-on-invalid
```

Ejemplo de trabajo:

```bash
python3 ops/run_f6_practices.py --chapter c06 --write --fail-on-invalid
cat output/c06_decision.md
python3 -m json.tool output/c06_report.json
```

## Salidas

```text
output/cXX_report.json
output/cXX_decision.md
output/all_summary.json
```

| Capítulo | Entrega práctica |
|---|---|
| C01 | Kit operativo con `AGENTS.md`, `SHOULD.md`, manifest y gate. |
| C02 | Contrato de runtime con estados, colas e idempotencia. |
| C03 | Estimador inicial de capacidad de serving. |
| C04 | Contrato de telemetría con SLI, SLO y presupuesto de error. |
| C05 | Política de routing, fallback y presupuesto por tarea. |
| C06 | Gate de release con scorecard y bloqueo trazable. |
| C07 | Controlador de shadow, canary y rollback. |
| C08 | Cola mínima de revisión humana con SLO. |
| C09 | Analizador de incidencia con postmortem y caso de regresión. |

## Cómo trabajarlo como alumno

1. Ejecuta el capítulo que acabas de leer.
2. Lee el Markdown de decisión y localiza qué gate permite o bloquea.
3. Abre el JSON y revisa qué métrica sostiene esa decisión.
4. Cambia un límite operativo: latencia, coste, presupuesto, SLO, rollout o severidad.
5. Vuelve a ejecutar y explica qué cambió en la decisión.

## Entrega mínima

Para cerrar una práctica, entrega:

- `output/cXX_decision.md`;
- `output/cXX_report.json`;
- una variante del caso original;
- una explicación sobre qué harías antes de producción.

Una práctica buena no dice “todo correcto”. Dice qué falta, qué se bloquea, qué se degrada, quién decide y qué evidencia quedaría para una auditoría posterior.

## Qué te llevas

Te llevas una práctica ejecutable sobre prácticas por capítulo, con datos editables, runbooks, plantillas de entrega, código ejecutable y tests reproducibles. Trabajas con `data/handoff_examples.jsonl` y `data/incident_events.jsonl`, contrastas la decisión contra `ops/ai/routing_policy.yaml` y ejecutas `ops/ai/evalops_release_gate.py` para generar `output/c01_decision.md`. La idea no es mirar una solución cerrada: es cambiar una entrada, volver a ejecutar, comparar la salida y poder defender qué harías en una revisión técnica, una asignatura o un piloto real.

## Variantes para hacerlo tuyo

- Ejecuta `make run` sin tocar nada y usa `output/c01_decision.md` como línea base.
- Cambia o añade un caso en `data/handoff_examples.jsonl` y `data/incident_events.jsonl` para representar un problema de tu trabajo, clase o producto.
- Endurece una regla, umbral o campo obligatorio en `ops/ai/routing_policy.yaml` y explica por qué el resultado debería cambiar o bloquearse.
- Compara antes/después en `output/c01_decision.md` y `output/c02_decision.md` y escribe una decisión de una página: seguir, bloquear, medir más o cambiar el diseño.
- Completa `templates/entrega.md` con contexto, cambio, evidencia, decisión y límite; no la dejes como checklist vacía.

## Rúbrica rápida

| Nivel | Qué demuestra |
|---|---|
| Mínimo | Ejecuta `make run` y `make test`, localiza `ops/ai/evalops_release_gate.py`, abre `output/c01_decision.md` y explica qué decisión o señal produce. |
| Bueno | Cambia `data/handoff_examples.jsonl`, compara antes/después y justifica la diferencia con una evidencia concreta del output. |
| Excelente | Convierte el kit en un mini caso profesional: añade un caso propio, ajusta una regla o test, documenta el límite principal y deja una recomendación accionable para un equipo. |

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `Kit F6: prácticas por capítulo`, no escondido en una ruta del repositorio.

### Qué contiene

- `README.md`: esta guía y la explicación del ejercicio.
- `Makefile`: entrada única para ejecutar y validar el kit con `make run` y `make test`.
- `requirements.txt`: dependencias declaradas; muchos kits solo usan la biblioteca estándar de Python.
- `data/`: datos de entrada o casos de prueba realistas. Ejemplos dentro del ZIP: `data/handoff_examples.jsonl`, `data/incident_events.jsonl`.
- `templates/`: plantillas editables para la entrega. Ejemplos dentro del ZIP: `templates/entrega.md`.
- `runbooks/`: procedimientos de operación o respuesta. Ejemplos dentro del ZIP: `runbooks/ai/contract-failures.md`, `runbooks/ai/high-burn-rate.md`.
- `ops/`: código ejecutable del laboratorio. Ejemplos dentro del ZIP: `ops/ai/decision.md`, `ops/ai/should.md`, `ops/ai/evalops_release_gate.py`, `ops/ai/handoff_queue.py`, ....
- `tests/`: tests que comprueban que el ejercicio sigue siendo reproducible. Ejemplos dentro del ZIP: `tests/test_lab_contract.py`.
- `output/`: salidas generadas o esperadas que debes revisar. Ejemplos dentro del ZIP: `output/c01_decision.md`, `output/c02_decision.md`, `output/c03_decision.md`, `output/c04_decision.md`, ....

### Ejecutar desde cero

Desde la carpeta extraída del ZIP:

```bash
make run
make test
```

`make run` construye las evidencias del ejercicio. `make test` comprueba que el kit sigue siendo ejecutable después de descargarlo, extraerlo y tocarlo.

### Qué mirar antes de entregar

- `output/c01_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/c02_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/c03_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/c04_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/c05_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/c06_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/c07_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/c08_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/c09_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/all_summary.json`: evidencia estructurada para validar o automatizar.
- `output/c01_report.json`: evidencia estructurada para validar o automatizar.
- `output/c02_report.json`: evidencia estructurada para validar o automatizar.

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
4. Usa `templates/` como base documental; no entregues una plantilla sin completar.
5. Guarda los outputs finales y una nota breve con la decisión técnica que tomarías en un proyecto real.

### Criterio de validación

El kit está completo cuando se puede descargar, extraer, ejecutar con `make run`, validar con `make test` y explicar sin depender de ninguna carpeta externa. Si una práctica menciona código, datos, contrato, CSV, SQL, política o plantilla, ese contenido debe venir dentro del ZIP.
<!-- zip-quality-audit:end -->
