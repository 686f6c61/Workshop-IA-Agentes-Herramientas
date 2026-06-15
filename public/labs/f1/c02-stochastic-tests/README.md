# Kit F1 C02: tests para salidas probabilísticas

Este kit acompaña el capítulo 02 del facsímil 1. Simula un LLM pequeño con varias respuestas posibles para que puedas ver por qué un assert exacto falla y cómo se reemplaza por una evaluación de propiedades.

No llama a ningún proveedor. Usa solo Python estándar y una distribución de logits definida en JSON.

## Ejecutar

Desde esta carpeta:

```bash
python3 ops/run_stochastic_eval.py --write
cat output/stochastic_eval_decision.md
```

Como mini proyecto reproducible:

```bash
make run
make test
```

Como gate:

```bash
python3 ops/run_stochastic_eval.py --write --fail-on-gate
```

## Requisitos

No necesitas credenciales ni proveedor de IA. `requirements.txt` deja explícito que el kit usa solo biblioteca estándar de Python. Python 3.10 o superior es suficiente.

## Archivos

| Archivo | Papel |
|---|---|
| `Makefile` | Atajos reproducibles para ejecutar, probar y limpiar salidas. |
| `requirements.txt` | Declara que no hay paquetes externos. |
| `data/sampling_cases.json` | Casos con prompt, respuestas candidatas, logits y propiedades esperadas. |
| `contracts/eval_policy.json` | Número de ejecuciones, temperaturas, umbrales y política de gate. |
| `ops/run_stochastic_eval.py` | Simulador y evaluador sin dependencias externas. |
| `tests/test_stochastic_eval.py` | Tests sobre softmax, temperatura cero, evaluación por propiedades y gate. |
| `output/stochastic_eval_report.json` | Resultados por caso y temperatura. |
| `output/stochastic_eval_decision.md` | Decisión técnica lista para revisar. |

## Qué deberías mirar

1. `exact_pass_rate`: porcentaje de ejecuciones que coinciden literalmente con el texto esperado.
2. `property_pass_rate`: porcentaje de ejecuciones que cumplen las propiedades importantes.
3. `unique_outputs`: cuántas salidas distintas aparecieron en las muestras.
4. `temperature`: cómo cambia la variabilidad al modificar el muestreo.
5. `gate`: si la evaluación pasaría o bloquearía una release.

## Criterios de aceptación

El ejercicio está bien resuelto cuando:

1. `make test` termina sin errores.
2. En `rust_definition`, `property_pass_rate` es mayor que `exact_pass_rate` cuando hay muestreo.
3. En `json_priority`, la temperatura alta bloquea o exige revisión si rompe demasiadas propiedades.
4. Puedes explicar por qué `temperature=0` se comporta como argmax en este simulador, pero no debe venderse como determinismo absoluto en una integración real.
5. Puedes justificar qué umbral de `property_pass_min` usarías en una tarea de soporte, documentación o salida JSON.

## Cómo adaptarlo a un proyecto real

1. Añade un caso propio a `data/sampling_cases.json`.
2. Define propiedades observables: campos obligatorios, palabras clave, longitud máxima, idioma, citas o formato.
3. Ajusta `contracts/eval_policy.json` con el número de ejecuciones y el umbral mínimo.
4. Ejecuta `make run` y revisa `output/stochastic_eval_decision.md`.
5. Entrega el diff del caso y una nota explicando por qué una igualdad literal no mide la calidad que te importa.

## Qué entregaría un alumno

1. El Markdown generado.
2. Un caso nuevo en `sampling_cases.json` para una salida JSON o Markdown.
3. Un ajuste razonado de `property_pass_min` o `max_unique_outputs`.
4. El resultado de `make test`.
5. Un párrafo explicando por qué el assert exacto no sirve para esa tarea.

## Qué te llevas

Te llevas una práctica ejecutable sobre tests para salidas probabilísticas, con datos editables, contratos y umbrales, plantillas de entrega, código ejecutable y tests reproducibles. Trabajas con `data/sampling_cases.json`, contrastas la decisión contra `contracts/eval_policy.json` y ejecutas `ops/run_stochastic_eval.py` para generar `output/stochastic_eval_decision.md`. La idea no es mirar una solución cerrada: es cambiar una entrada, volver a ejecutar, comparar la salida y poder defender qué harías en una revisión técnica, una asignatura o un piloto real.

## Variantes para hacerlo tuyo

- Ejecuta `make run` sin tocar nada y usa `output/stochastic_eval_decision.md` como línea base.
- Cambia o añade un caso en `data/sampling_cases.json` para representar un problema de tu trabajo, clase o producto.
- Endurece una regla, umbral o campo obligatorio en `contracts/eval_policy.json` y explica por qué el resultado debería cambiar o bloquearse.
- Compara antes/después en `output/stochastic_eval_decision.md` y `output/stochastic_eval_report.json` y escribe una decisión de una página: seguir, bloquear, medir más o cambiar el diseño.
- Completa `templates/entrega.md` con contexto, cambio, evidencia, decisión y límite; no la dejes como checklist vacía.

## Rúbrica rápida

| Nivel | Qué demuestra |
|---|---|
| Mínimo | Ejecuta `make run` y `make test`, localiza `ops/run_stochastic_eval.py`, abre `output/stochastic_eval_decision.md` y explica qué decisión o señal produce. |
| Bueno | Cambia `data/sampling_cases.json`, compara antes/después y justifica la diferencia con una evidencia concreta del output. |
| Excelente | Convierte el kit en un mini caso profesional: añade un caso propio, ajusta una regla o test, documenta el límite principal y deja una recomendación accionable para un equipo. |

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `Kit F1 C02: tests para salidas probabilísticas`, no escondido en una ruta del repositorio.

### Qué contiene

- `README.md`: esta guía y la explicación del ejercicio.
- `Makefile`: entrada única para ejecutar y validar el kit con `make run` y `make test`.
- `requirements.txt`: dependencias declaradas; muchos kits solo usan la biblioteca estándar de Python.
- `data/`: datos de entrada o casos de prueba realistas. Ejemplos dentro del ZIP: `data/sampling_cases.json`.
- `contracts/`: contratos de datos, salida, política o validación. Ejemplos dentro del ZIP: `contracts/eval_policy.json`.
- `templates/`: plantillas editables para la entrega. Ejemplos dentro del ZIP: `templates/entrega.md`.
- `ops/`: código ejecutable del laboratorio. Ejemplos dentro del ZIP: `ops/run_stochastic_eval.py`.
- `tests/`: tests que comprueban que el ejercicio sigue siendo reproducible. Ejemplos dentro del ZIP: `tests/test_stochastic_eval.py`.
- `output/`: salidas generadas o esperadas que debes revisar. Ejemplos dentro del ZIP: `output/stochastic_eval_decision.md`, `output/stochastic_eval_report.json`.

### Ejecutar desde cero

Desde la carpeta extraída del ZIP:

```bash
make run
make test
```

`make run` construye las evidencias del ejercicio. `make test` comprueba que el kit sigue siendo ejecutable después de descargarlo, extraerlo y tocarlo.

### Qué mirar antes de entregar

- `output/stochastic_eval_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/stochastic_eval_report.json`: evidencia estructurada para validar o automatizar.

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
