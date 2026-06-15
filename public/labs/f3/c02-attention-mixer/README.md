# Kit F3 C02: mezcla de atención

Este kit acompaña el capítulo 02 del facsímil 3. Calcula una fila de atención en Python puro y muestra cómo un token mezcla vectores de valor.

## Ejecutar

```bash
python3 ops/run_attention_mixer.py --write
cat output/attention_mixer_decision.md
```

Como gate:

```bash
python3 ops/run_attention_mixer.py --write --fail-on-invalid
```

## Archivos

| Archivo | Papel |
|---|---|
| `data/attention_case.json` | Tokens, puntuaciones y vectores de valor. |
| `contracts/attention_policy.json` | Token observado y umbrales de suma de pesos. |
| `ops/run_attention_mixer.py` | Softmax estable y mezcla ponderada. |
| `output/attention_mixer_report.json` | Pesos y vector contextual. |
| `output/attention_mixer_decision.md` | Lectura técnica. |

## Qué deberías mirar

1. `attention_scores`: puntuaciones antes de softmax; todavía no son probabilidades.
2. `attention_weights`: pesos normalizados; deben sumar 1.
3. `context_vector`: mezcla final de valores ponderada por atención.
4. Qué token domina la mezcla y si eso coincide con la intuición lingüística del caso.
5. Qué cambia si subes o bajas una puntuación: la atención redistribuye masa, no elige una sola palabra mágicamente.

## Cómo lo adaptas a tu caso

Añade un token nuevo y cambia sus puntuaciones en `data/attention_case.json`. Una buena entrega compara el vector contextual antes y después, y explica qué información entró más fuerte en la representación. No basta con decir “atiende más”: hay que enseñar el peso y el efecto en el vector.

## Qué entregaría un alumno

El Markdown generado, una variante de puntuaciones y una explicación de qué token domina el vector contextual y por qué.

## Qué te llevas

Te llevas una práctica ejecutable sobre mezcla de atención, con datos editables, contratos y umbrales, plantillas de entrega, código ejecutable y tests reproducibles. Trabajas con `data/attention_case.json`, contrastas la decisión contra `contracts/attention_policy.json` y ejecutas `ops/run_attention_mixer.py` para generar `output/attention_mixer_decision.md`. La idea no es mirar una solución cerrada: es cambiar una entrada, volver a ejecutar, comparar la salida y poder defender qué harías en una revisión técnica, una asignatura o un piloto real.

## Variantes para hacerlo tuyo

- Ejecuta `make run` sin tocar nada y usa `output/attention_mixer_decision.md` como línea base.
- Cambia o añade un caso en `data/attention_case.json` para representar un problema de tu trabajo, clase o producto.
- Endurece una regla, umbral o campo obligatorio en `contracts/attention_policy.json` y explica por qué el resultado debería cambiar o bloquearse.
- Compara antes/después en `output/attention_mixer_decision.md` y `output/attention_mixer_report.json` y escribe una decisión de una página: seguir, bloquear, medir más o cambiar el diseño.
- Completa `templates/entrega.md` con contexto, cambio, evidencia, decisión y límite; no la dejes como checklist vacía.

## Rúbrica rápida

| Nivel | Qué demuestra |
|---|---|
| Mínimo | Ejecuta `make run` y `make test`, localiza `ops/run_attention_mixer.py`, abre `output/attention_mixer_decision.md` y explica qué decisión o señal produce. |
| Bueno | Cambia `data/attention_case.json`, compara antes/después y justifica la diferencia con una evidencia concreta del output. |
| Excelente | Convierte el kit en un mini caso profesional: añade un caso propio, ajusta una regla o test, documenta el límite principal y deja una recomendación accionable para un equipo. |

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `Kit F3 C02: mezcla de atención`, no escondido en una ruta del repositorio.

### Qué contiene

- `README.md`: esta guía y la explicación del ejercicio.
- `Makefile`: entrada única para ejecutar y validar el kit con `make run` y `make test`.
- `requirements.txt`: dependencias declaradas; muchos kits solo usan la biblioteca estándar de Python.
- `data/`: datos de entrada o casos de prueba realistas. Ejemplos dentro del ZIP: `data/attention_case.json`.
- `contracts/`: contratos de datos, salida, política o validación. Ejemplos dentro del ZIP: `contracts/attention_policy.json`.
- `templates/`: plantillas editables para la entrega. Ejemplos dentro del ZIP: `templates/entrega.md`.
- `ops/`: código ejecutable del laboratorio. Ejemplos dentro del ZIP: `ops/run_attention_mixer.py`.
- `tests/`: tests que comprueban que el ejercicio sigue siendo reproducible. Ejemplos dentro del ZIP: `tests/test_lab_contract.py`.
- `output/`: salidas generadas o esperadas que debes revisar. Ejemplos dentro del ZIP: `output/attention_mixer_decision.md`, `output/attention_mixer_report.json`.

### Ejecutar desde cero

Desde la carpeta extraída del ZIP:

```bash
make run
make test
```

`make run` construye las evidencias del ejercicio. `make test` comprueba que el kit sigue siendo ejecutable después de descargarlo, extraerlo y tocarlo.

### Qué mirar antes de entregar

- `output/attention_mixer_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/attention_mixer_report.json`: evidencia estructurada para validar o automatizar.

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
