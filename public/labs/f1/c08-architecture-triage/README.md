# Kit F1 C08: elegir arquitectura antes de entrenar

Este kit acompaña el capítulo 08 del facsímil 1. Convierte la comparación entre CNN, RNN/LSTM y Transformer en una decisión reproducible: dado un conjunto de casos, calcula señales de coste, memoria, estructura de datos y riesgo antes de escoger arquitectura.

La idea no es demostrar que una familia sea siempre mejor. La idea es entrenar el hábito de ingeniería: mirar la forma de los datos, la longitud de la secuencia, el hardware, la latencia y el tipo de salida antes de elegir modelo.

## Ejecutar

Desde esta carpeta:

```bash
python3 ops/audit_architecture_triage.py --write
cat output/architecture_triage_decision.md
```

Como gate:

```bash
python3 ops/audit_architecture_triage.py --write --fail-on-invalid
```

## Archivos

| Archivo | Papel |
|---|---|
| `data/problem_cases.json` | Casos de visión, series temporales, texto corto y texto largo. |
| `contracts/architecture_policy.json` | Umbrales de latencia, memoria, tamaño de secuencia y mínimos de justificación. |
| `ops/audit_architecture_triage.py` | Selector de arquitectura con cálculos aproximados de parámetros y coste de atención. |
| `output/architecture_triage_report.json` | Informe estructurado con candidatos, recomendación y riesgos. |
| `output/architecture_triage_decision.md` | Lectura técnica para entregar o discutir en clase. |

## Qué deberías mirar

1. Qué cambia cuando la entrada es una imagen, una serie temporal o un texto largo.
2. Por qué una CNN aprovecha la estructura local de una rejilla.
3. Por qué una LSTM sigue siendo razonable en secuencias cortas con poco hardware.
4. Por qué el coste de atención crece cómo `O(n²)` con la longitud de contexto.
5. Qué señales obligan a no entrenar todavía: pocos ejemplos, latencia imposible o memoria insuficiente.

## Qué entregaría un alumno

1. El Markdown generado.
2. Un caso nuevo añadido a `data/problem_cases.json`.
3. Una justificación de arquitectura con forma de datos, coste y restricción de despliegue.
4. Una decisión escrita: entrenar, simplificar, cambiar de familia o recoger más datos.

## Qué te llevas

Te llevas una práctica ejecutable sobre elegir arquitectura antes de entrenar, con datos editables, contratos y umbrales, plantillas de entrega, código ejecutable y tests reproducibles. Trabajas con `data/problem_cases.json`, contrastas la decisión contra `contracts/architecture_policy.json` y ejecutas `ops/audit_architecture_triage.py` para generar `output/architecture_triage_decision.md`. La idea no es mirar una solución cerrada: es cambiar una entrada, volver a ejecutar, comparar la salida y poder defender qué harías en una revisión técnica, una asignatura o un piloto real.

## Variantes para hacerlo tuyo

- Ejecuta `make run` sin tocar nada y usa `output/architecture_triage_decision.md` como línea base.
- Cambia o añade un caso en `data/problem_cases.json` para representar un problema de tu trabajo, clase o producto.
- Endurece una regla, umbral o campo obligatorio en `contracts/architecture_policy.json` y explica por qué el resultado debería cambiar o bloquearse.
- Compara antes/después en `output/architecture_triage_decision.md` y `output/architecture_triage_report.json` y escribe una decisión de una página: seguir, bloquear, medir más o cambiar el diseño.
- Completa `templates/entrega.md` con contexto, cambio, evidencia, decisión y límite; no la dejes como checklist vacía.

## Rúbrica rápida

| Nivel | Qué demuestra |
|---|---|
| Mínimo | Ejecuta `make run` y `make test`, localiza `ops/audit_architecture_triage.py`, abre `output/architecture_triage_decision.md` y explica qué decisión o señal produce. |
| Bueno | Cambia `data/problem_cases.json`, compara antes/después y justifica la diferencia con una evidencia concreta del output. |
| Excelente | Convierte el kit en un mini caso profesional: añade un caso propio, ajusta una regla o test, documenta el límite principal y deja una recomendación accionable para un equipo. |

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `Kit F1 C08: elegir arquitectura antes de entrenar`, no escondido en una ruta del repositorio.

### Qué contiene

- `README.md`: esta guía y la explicación del ejercicio.
- `Makefile`: entrada única para ejecutar y validar el kit con `make run` y `make test`.
- `requirements.txt`: dependencias declaradas; muchos kits solo usan la biblioteca estándar de Python.
- `data/`: datos de entrada o casos de prueba realistas. Ejemplos dentro del ZIP: `data/problem_cases.json`.
- `contracts/`: contratos de datos, salida, política o validación. Ejemplos dentro del ZIP: `contracts/architecture_policy.json`.
- `templates/`: plantillas editables para la entrega. Ejemplos dentro del ZIP: `templates/entrega.md`.
- `ops/`: código ejecutable del laboratorio. Ejemplos dentro del ZIP: `ops/audit_architecture_triage.py`.
- `tests/`: tests que comprueban que el ejercicio sigue siendo reproducible. Ejemplos dentro del ZIP: `tests/test_architecture_triage.py`.
- `output/`: salidas generadas o esperadas que debes revisar. Ejemplos dentro del ZIP: `output/architecture_triage_decision.md`, `output/architecture_triage_report.json`.

### Ejecutar desde cero

Desde la carpeta extraída del ZIP:

```bash
make run
make test
```

`make run` construye las evidencias del ejercicio. `make test` comprueba que el kit sigue siendo ejecutable después de descargarlo, extraerlo y tocarlo.

### Qué mirar antes de entregar

- `output/architecture_triage_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/architecture_triage_report.json`: evidencia estructurada para validar o automatizar.

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
