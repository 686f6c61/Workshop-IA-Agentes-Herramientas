# Kit F2 C07: traza de backtracking CSP

Este kit acompaña el capítulo 07 del facsímil 2. Resuelve un horario pequeño con propagación unaria, MRV, forward checking y backtracking, dejando una traza evento a evento.

El objetivo es que el solver no sea una caja negra: queremos ver qué variable se eligió, qué valor se probó, qué dominios se redujeron y dónde se cortaron ramas.

## Ejecutar

Desde esta carpeta:

```bash
python3 ops/trace_backtracking.py --write
cat output/backtracking_decision.md
```

Como gate:

```bash
python3 ops/trace_backtracking.py --write --fail-on-invalid
```

## Archivos

| Archivo | Papel |
|---|---|
| `data/backtracking_problem.json` | Variables, dominios y restricciones del horario. |
| `contracts/backtracking_policy.json` | Expectativas mínimas del ejercicio. |
| `ops/trace_backtracking.py` | Backtracking con MRV y forward checking sin dependencias externas. |
| `output/backtracking_report.json` | Métricas estructuradas. |
| `output/backtracking_trace.jsonl` | Traza línea a línea para depurar. |
| `output/backtracking_decision.md` | Informe legible para entregar. |

## Qué deberías mirar

1. Cuántos candidatos habría sin poda.
2. Cuánto reducen las restricciones unarias.
3. Qué variable elige MRV en cada paso.
4. Qué valores elimina forward checking.
5. Cuántos nodos visita el backtracking.

## Qué entregaría un alumno

1. El Markdown generado.
2. Tres líneas comentadas de la traza `jsonl`.
3. Una explicación de por qué MRV eligió una variable.
4. Una modificación del problema que aumente o reduzca las soluciones.

## Qué te llevas

Te llevas una práctica ejecutable sobre traza de backtracking CSP, con datos editables, contratos y umbrales, plantillas de entrega, código ejecutable y tests reproducibles. Trabajas con `data/backtracking_problem.json`, contrastas la decisión contra `contracts/backtracking_policy.json` y ejecutas `ops/trace_backtracking.py` para generar `output/backtracking_decision.md`. La idea no es mirar una solución cerrada: es cambiar una entrada, volver a ejecutar, comparar la salida y poder defender qué harías en una revisión técnica, una asignatura o un piloto real.

## Variantes para hacerlo tuyo

- Ejecuta `make run` sin tocar nada y usa `output/backtracking_decision.md` como línea base.
- Cambia o añade un caso en `data/backtracking_problem.json` para representar un problema de tu trabajo, clase o producto.
- Endurece una regla, umbral o campo obligatorio en `contracts/backtracking_policy.json` y explica por qué el resultado debería cambiar o bloquearse.
- Compara antes/después en `output/backtracking_decision.md` y `output/backtracking_report.json` y escribe una decisión de una página: seguir, bloquear, medir más o cambiar el diseño.
- Completa `templates/entrega.md` con contexto, cambio, evidencia, decisión y límite; no la dejes como checklist vacía.

## Rúbrica rápida

| Nivel | Qué demuestra |
|---|---|
| Mínimo | Ejecuta `make run` y `make test`, localiza `ops/trace_backtracking.py`, abre `output/backtracking_decision.md` y explica qué decisión o señal produce. |
| Bueno | Cambia `data/backtracking_problem.json`, compara antes/después y justifica la diferencia con una evidencia concreta del output. |
| Excelente | Convierte el kit en un mini caso profesional: añade un caso propio, ajusta una regla o test, documenta el límite principal y deja una recomendación accionable para un equipo. |

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `Kit F2 C07: traza de backtracking CSP`, no escondido en una ruta del repositorio.

### Qué contiene

- `README.md`: esta guía y la explicación del ejercicio.
- `Makefile`: entrada única para ejecutar y validar el kit con `make run` y `make test`.
- `requirements.txt`: dependencias declaradas; muchos kits solo usan la biblioteca estándar de Python.
- `data/`: datos de entrada o casos de prueba realistas. Ejemplos dentro del ZIP: `data/backtracking_problem.json`.
- `contracts/`: contratos de datos, salida, política o validación. Ejemplos dentro del ZIP: `contracts/backtracking_policy.json`.
- `templates/`: plantillas editables para la entrega. Ejemplos dentro del ZIP: `templates/entrega.md`.
- `ops/`: código ejecutable del laboratorio. Ejemplos dentro del ZIP: `ops/trace_backtracking.py`.
- `tests/`: tests que comprueban que el ejercicio sigue siendo reproducible. Ejemplos dentro del ZIP: `tests/test_lab_contract.py`.
- `output/`: salidas generadas o esperadas que debes revisar. Ejemplos dentro del ZIP: `output/backtracking_decision.md`, `output/backtracking_report.json`, `output/backtracking_trace.jsonl`.

### Ejecutar desde cero

Desde la carpeta extraída del ZIP:

```bash
make run
make test
```

`make run` construye las evidencias del ejercicio. `make test` comprueba que el kit sigue siendo ejecutable después de descargarlo, extraerlo y tocarlo.

### Qué mirar antes de entregar

- `output/backtracking_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/backtracking_report.json`: evidencia estructurada para validar o automatizar.
- `output/backtracking_trace.jsonl`: eventos o registros línea a línea.

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
