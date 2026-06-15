# F4 · Prácticas ejecutables por capítulo

Este kit acompaña los `Manos a la obra` del facsímil 4. No sustituye al laboratorio largo del capítulo 13; sirve para que cada capítulo tenga una práctica descargable, reproducible y verificable sin depender de claves de API.

La idea es que puedas trabajar capítulo a capítulo. Cada práctica toma una decisión pequeña, genera un informe Markdown y deja un JSON con datos que puedes auditar, cambiar y comparar.

Los casos ya no viven escondidos dentro del script: están en `data/practice_cases.json`. Los criterios mínimos, umbrales y la frase de utilidad de cada práctica están en `contracts/practice_policy.json`. Ese es el material que debes tocar cuando quieras adaptar el ejercicio a tu día a día.

## Ejecutar todo

```bash
python3 ops/run_f4_practices.py --all --write --fail-on-invalid
```

## Ejecutar un capítulo

```bash
python3 ops/run_f4_practices.py --chapter c01 --write --fail-on-invalid
python3 ops/run_f4_practices.py --chapter c09 --write --fail-on-invalid
python3 ops/run_f4_practices.py --chapter c14 --write --fail-on-invalid
```

Capítulos disponibles:

| Capítulo | Qué prueba |
|---|---|
| `c01` | Elegir intervención: prompt/schema, RAG, tool, ajuste o local. |
| `c02` | Revisar un payload de API con schema, tools, metadata y multimodalidad. |
| `c03` | Estimar tokens, ventana, caché y coste. |
| `c04` | Elegir modelo comparando calidad, coste, licencia, apertura, control de datos, reproducibilidad y encaje operativo. |
| `c05` | Preparar un contrato de modelo local. |
| `c06` | Comparar cloud, local, híbrido y GPU alquilada. |
| `c07` | Evaluar embeddings con dimensión, similitud y ranking. |
| `c08` | Probar búsqueda vectorial, léxica e híbrida con filtros. |
| `c09` | Evaluar un mini RAG con citas y abstención. |
| `c10` | Medir retrieval, groundedness y decisión de release. |
| `c11` | Simular una ruta de Agentic RAG/GraphRAG. |
| `c12` | Validar y ejecutar Text-to-SQL sobre SQLite local. |
| `c14` | Revisar una arquitectura completa con una rúbrica ejecutable. |

## Cómo trabajarlo como alumno

1. Ejecuta el capítulo que acabas de leer.
2. Abre `output/cXX_decision.md` y comprueba si entiendes la decisión sin mirar el código.
3. Cambia un dato de entrada en `data/practice_cases.json`.
4. Si quieres cambiar el criterio de aceptación, toca `contracts/practice_policy.json`.
5. Vuelve a ejecutar y escribe qué cambió: métrica, riesgo, coste, ruta o decisión final.

Esto no pretende simular una API comercial completa. Pretende entrenar el músculo útil: transformar una idea de herramienta en una decisión con contrato, métricas y límites.

## Qué te llevas

Te llevas una práctica ejecutable sobre F4 · Prácticas ejecutables por capítulo, con datos editables, contratos y umbrales, plantillas de entrega, código ejecutable y tests reproducibles. Trabajas con `data/practice_cases.json`, contrastas la decisión contra `contracts/practice_policy.json` y ejecutas `ops/run_f4_practices.py` para generar `output/c01_decision.md`. La idea no es mirar una solución cerrada: es cambiar una entrada, volver a ejecutar, comparar la salida y poder defender qué harías en una revisión técnica, una asignatura o un piloto real.

## Salidas

El script escribe:

```text
output/
  cXX_report.json
  cXX_decision.md
  all_summary.json
```

| Salida | Qué deberías poder defender |
|---|---|
| `cXX_decision.md` | La decisión técnica en lenguaje humano. |
| `cXX_report.json` | Los datos que sostienen esa decisión. |
| `all_summary.json` | Qué prácticas pasaron y cuáles requieren revisión. |

Una práctica válida no busca un número bonito. Debe dejar una traza mínima: entrada, decisión, métricas, límites y siguiente acción.

## Entrega mínima

Para cerrar una práctica, entrega:

- el Markdown generado;
- una captura o copia del JSON relevante;
- una variante del caso original;
- una explicación breve de por qué la decisión cambió o no cambió.

## Variantes para hacerlo tuyo

- Ejecuta `make run` sin tocar nada y usa `output/c01_decision.md` como línea base.
- Cambia o añade un caso en `data/practice_cases.json` para representar un problema de tu trabajo, clase o producto.
- Endurece una regla, umbral o campo obligatorio en `contracts/practice_policy.json` y explica por qué el resultado debería cambiar o bloquearse.
- Compara antes/después en `output/c01_decision.md` y `output/c02_decision.md` y escribe una decisión de una página: seguir, bloquear, medir más o cambiar el diseño.
- Completa `templates/entrega.md` con contexto, cambio, evidencia, decisión y límite; no la dejes como checklist vacía.

## Rúbrica rápida

| Nivel | Qué demuestra |
|---|---|
| Mínimo | Ejecuta `make run` y `make test`, localiza `ops/run_f4_practices.py`, abre `output/c01_decision.md` y explica qué decisión o señal produce. |
| Bueno | Cambia `data/practice_cases.json`, compara antes/después y justifica la diferencia con una evidencia concreta del output. |
| Excelente | Convierte el kit en un mini caso profesional: añade un caso propio, ajusta una regla o test, documenta el límite principal y deja una recomendación accionable para un equipo. |

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `F4 · Prácticas ejecutables por capítulo`, no escondido en una ruta del repositorio.

### Qué contiene

- `README.md`: esta guía y la explicación del ejercicio.
- `Makefile`: entrada única para ejecutar y validar el kit con `make run` y `make test`.
- `requirements.txt`: dependencias declaradas; muchos kits solo usan la biblioteca estándar de Python.
- `data/`: datos de entrada o casos de prueba realistas. Ejemplos dentro del ZIP: `data/practice_cases.json`.
- `contracts/`: contratos de datos, salida, política o validación. Ejemplos dentro del ZIP: `contracts/practice_policy.json`.
- `templates/`: plantillas editables para la entrega. Ejemplos dentro del ZIP: `templates/entrega.md`.
- `ops/`: código ejecutable del laboratorio. Ejemplos dentro del ZIP: `ops/run_f4_practices.py`.
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
- `output/c10_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/c11_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/c12_decision.md`: lectura humana de la decisión, informe o runbook.

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
