# Kit F3 C01: pérdida y memoria de un LLM

Este kit acompaña el capítulo 01 del facsímil 3. Convierte dos ideas básicas en cálculos reproducibles: la pérdida token a token y la memoria mínima de pesos de un modelo.

El objetivo es que el alumno no hable de “un 7B” en abstracto. Un modelo tiene parámetros, precisión, memoria de pesos y una pérdida que baja cuando asigna más probabilidad a los tokens correctos.

## Ejecutar

```bash
python3 ops/estimate_loss_memory.py --write
cat output/loss_memory_decision.md
```

Como gate:

```bash
python3 ops/estimate_loss_memory.py --write --fail-on-invalid
```

## Archivos

| Archivo | Papel |
|---|---|
| `data/loss_memory_case.json` | Probabilidades antes/después y tamaños de modelo. |
| `contracts/loss_memory_policy.json` | Umbrales mínimos: la pérdida debe bajar y la memoria debe cuadrar. |
| `ops/estimate_loss_memory.py` | Calcula pérdida, perplexity y memoria por precisión. |
| `output/loss_memory_report.json` | Resultados estructurados. |
| `output/loss_memory_decision.md` | Informe legible para entregar. |

## Qué deberías mirar

1. `token_losses`: qué token queda peor explicado y cuánto aporta a la pérdida total.
2. `perplexity_before` y `perplexity_after`: si la mejora de probabilidad se traduce en una señal interpretable.
3. `model_memory`: memoria mínima de pesos por precisión; no incluye KV cache, runtime ni batch.
4. `fits_declared_budget`: si el cálculo contradice la intuición de “cabe porque es un 7B”.
5. `missing_operational_costs`: qué piezas faltan antes de prometer una integración real.

## Cómo lo adaptas a tu caso

Sustituye las probabilidades de `data/loss_memory_case.json` por una secuencia de tokens de tu propio ejemplo. Después añade un tamaño de modelo y precisión que estés considerando. La decisión correcta debe separar tres cosas: pérdida/token, memoria de pesos y memoria operativa total. Si el alumno mezcla esas tres, todavía no ha entendido el capítulo.

## Qué entregaría un alumno

El Markdown generado, una secuencia nueva de probabilidades, una precisión nueva y una decisión: qué falta todavía para saber si un modelo cabe de verdad en una máquina.

## Qué te llevas

Te llevas una práctica ejecutable sobre pérdida y memoria de un LLM, con datos editables, contratos y umbrales, plantillas de entrega, código ejecutable y tests reproducibles. Trabajas con `data/loss_memory_case.json`, contrastas la decisión contra `contracts/loss_memory_policy.json` y ejecutas `ops/estimate_loss_memory.py` para generar `output/loss_memory_decision.md`. La idea no es mirar una solución cerrada: es cambiar una entrada, volver a ejecutar, comparar la salida y poder defender qué harías en una revisión técnica, una asignatura o un piloto real.

## Variantes para hacerlo tuyo

- Ejecuta `make run` sin tocar nada y usa `output/loss_memory_decision.md` como línea base.
- Cambia o añade un caso en `data/loss_memory_case.json` para representar un problema de tu trabajo, clase o producto.
- Endurece una regla, umbral o campo obligatorio en `contracts/loss_memory_policy.json` y explica por qué el resultado debería cambiar o bloquearse.
- Compara antes/después en `output/loss_memory_decision.md` y `output/loss_memory_report.json` y escribe una decisión de una página: seguir, bloquear, medir más o cambiar el diseño.
- Completa `templates/entrega.md` con contexto, cambio, evidencia, decisión y límite; no la dejes como checklist vacía.

## Rúbrica rápida

| Nivel | Qué demuestra |
|---|---|
| Mínimo | Ejecuta `make run` y `make test`, localiza `ops/estimate_loss_memory.py`, abre `output/loss_memory_decision.md` y explica qué decisión o señal produce. |
| Bueno | Cambia `data/loss_memory_case.json`, compara antes/después y justifica la diferencia con una evidencia concreta del output. |
| Excelente | Convierte el kit en un mini caso profesional: añade un caso propio, ajusta una regla o test, documenta el límite principal y deja una recomendación accionable para un equipo. |

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `Kit F3 C01: pérdida y memoria de un LLM`, no escondido en una ruta del repositorio.

### Qué contiene

- `README.md`: esta guía y la explicación del ejercicio.
- `Makefile`: entrada única para ejecutar y validar el kit con `make run` y `make test`.
- `requirements.txt`: dependencias declaradas; muchos kits solo usan la biblioteca estándar de Python.
- `data/`: datos de entrada o casos de prueba realistas. Ejemplos dentro del ZIP: `data/loss_memory_case.json`.
- `contracts/`: contratos de datos, salida, política o validación. Ejemplos dentro del ZIP: `contracts/loss_memory_policy.json`.
- `templates/`: plantillas editables para la entrega. Ejemplos dentro del ZIP: `templates/entrega.md`.
- `ops/`: código ejecutable del laboratorio. Ejemplos dentro del ZIP: `ops/estimate_loss_memory.py`.
- `tests/`: tests que comprueban que el ejercicio sigue siendo reproducible. Ejemplos dentro del ZIP: `tests/test_lab_contract.py`.
- `output/`: salidas generadas o esperadas que debes revisar. Ejemplos dentro del ZIP: `output/loss_memory_decision.md`, `output/loss_memory_report.json`.

### Ejecutar desde cero

Desde la carpeta extraída del ZIP:

```bash
make run
make test
```

`make run` construye las evidencias del ejercicio. `make test` comprueba que el kit sigue siendo ejecutable después de descargarlo, extraerlo y tocarlo.

### Qué mirar antes de entregar

- `output/loss_memory_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/loss_memory_report.json`: evidencia estructurada para validar o automatizar.

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
