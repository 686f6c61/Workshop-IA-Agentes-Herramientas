# Kit F1 C04: neurona artificial con contrato de dimensiones

Este kit acompaña el capítulo 04 del facsímil 1. Implementa una neurona artificial sin dependencias externas, valida el contrato de entrada y genera un pequeño informe técnico.

El objetivo no es usar una librería de deep learning. El objetivo es que puedas defender, con números, que una neurona es producto escalar, sesgo y activación.

## Ejecutar

Desde esta carpeta:

```bash
python3 ops/run_neuron_contract.py --write
cat output/neuron_decision.md
```

Como gate:

```bash
python3 ops/run_neuron_contract.py --write --fail-on-invalid
```

## Archivos

| Archivo | Papel |
|---|---|
| `data/neuron_cases.json` | Casos de neurona con entradas, pesos, sesgo y activación esperada. |
| `contracts/neuron_policy.json` | Tolerancia numérica, activaciones permitidas y barrido de sensibilidad. |
| `ops/run_neuron_contract.py` | Implementación ejecutable sin dependencias externas. |
| `output/neuron_report.json` | Resultado calculado, validaciones y sensibilidad. |
| `output/neuron_decision.md` | Informe legible para clase o revisión técnica. |

## Qué deberías mirar

1. `z`: suma ponderada antes de activar.
2. `output`: salida después de aplicar ReLU o sigmoide.
3. `valid`: si entradas y pesos tienen la misma dimensión.
4. `sensitivity`: cuánto cambia la salida al mover un peso o el sesgo.
5. `invalid_cases`: casos que un sistema serio debe rechazar antes de calcular.

## Qué entregaría un alumno

1. El Markdown generado.
2. Un caso nuevo con cuatro entradas.
3. Un caso inválido explicado: dimensión incorrecta, activación no permitida o valor no numérico.
4. Una frase técnica explicando qué parámetro mueve más la salida y por qué.

## Qué te llevas

Te llevas una práctica ejecutable sobre neurona artificial con contrato de dimensiones, con datos editables, contratos y umbrales, plantillas de entrega, código ejecutable y tests reproducibles. Trabajas con `data/neuron_cases.json`, contrastas la decisión contra `contracts/neuron_policy.json` y ejecutas `ops/run_neuron_contract.py` para generar `output/neuron_decision.md`. La idea no es mirar una solución cerrada: es cambiar una entrada, volver a ejecutar, comparar la salida y poder defender qué harías en una revisión técnica, una asignatura o un piloto real.

## Variantes para hacerlo tuyo

- Ejecuta `make run` sin tocar nada y usa `output/neuron_decision.md` como línea base.
- Cambia o añade un caso en `data/neuron_cases.json` para representar un problema de tu trabajo, clase o producto.
- Endurece una regla, umbral o campo obligatorio en `contracts/neuron_policy.json` y explica por qué el resultado debería cambiar o bloquearse.
- Compara antes/después en `output/neuron_decision.md` y `output/neuron_report.json` y escribe una decisión de una página: seguir, bloquear, medir más o cambiar el diseño.
- Completa `templates/entrega.md` con contexto, cambio, evidencia, decisión y límite; no la dejes como checklist vacía.

## Rúbrica rápida

| Nivel | Qué demuestra |
|---|---|
| Mínimo | Ejecuta `make run` y `make test`, localiza `ops/run_neuron_contract.py`, abre `output/neuron_decision.md` y explica qué decisión o señal produce. |
| Bueno | Cambia `data/neuron_cases.json`, compara antes/después y justifica la diferencia con una evidencia concreta del output. |
| Excelente | Convierte el kit en un mini caso profesional: añade un caso propio, ajusta una regla o test, documenta el límite principal y deja una recomendación accionable para un equipo. |

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `Kit F1 C04: neurona artificial con contrato de dimensiones`, no escondido en una ruta del repositorio.

### Qué contiene

- `README.md`: esta guía y la explicación del ejercicio.
- `Makefile`: entrada única para ejecutar y validar el kit con `make run` y `make test`.
- `requirements.txt`: dependencias declaradas; muchos kits solo usan la biblioteca estándar de Python.
- `data/`: datos de entrada o casos de prueba realistas. Ejemplos dentro del ZIP: `data/neuron_cases.json`.
- `contracts/`: contratos de datos, salida, política o validación. Ejemplos dentro del ZIP: `contracts/neuron_policy.json`.
- `templates/`: plantillas editables para la entrega. Ejemplos dentro del ZIP: `templates/entrega.md`.
- `ops/`: código ejecutable del laboratorio. Ejemplos dentro del ZIP: `ops/run_neuron_contract.py`.
- `tests/`: tests que comprueban que el ejercicio sigue siendo reproducible. Ejemplos dentro del ZIP: `tests/test_neuron_contract.py`.
- `output/`: salidas generadas o esperadas que debes revisar. Ejemplos dentro del ZIP: `output/neuron_decision.md`, `output/neuron_report.json`.

### Ejecutar desde cero

Desde la carpeta extraída del ZIP:

```bash
make run
make test
```

`make run` construye las evidencias del ejercicio. `make test` comprueba que el kit sigue siendo ejecutable después de descargarlo, extraerlo y tocarlo.

### Qué mirar antes de entregar

- `output/neuron_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/neuron_report.json`: evidencia estructurada para validar o automatizar.

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
