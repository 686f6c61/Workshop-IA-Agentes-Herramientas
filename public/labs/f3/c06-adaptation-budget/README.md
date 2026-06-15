# Kit F3 C06: presupuesto de adaptación y destilación

Este kit acompaña el capítulo 06 del facsímil 3. Calcula parámetros entrenables de LoRA/adapters, gradientes de logits, memoria por bits y una pérdida KL de destilación.

## Ejecutar

```bash
python3 ops/estimate_adaptation_budget.py --write
cat output/adaptation_budget_decision.md
```

Como gate:

```bash
python3 ops/estimate_adaptation_budget.py --write --fail-on-invalid
```

## Archivos

| Archivo | Papel |
|---|---|
| `data/adaptation_case.json` | Dimensiones, logits, objetivo y tamaños de modelo. |
| `contracts/adaptation_policy.json` | Umbrales de LoRA, memoria y KL. |
| `ops/estimate_adaptation_budget.py` | Cálculos de parámetros, gradientes, memoria y KL. |
| `output/adaptation_budget_report.json` | Resultados estructurados. |
| `output/adaptation_budget_decision.md` | Informe legible. |

## Qué deberías mirar

1. `lora_trainable_parameters`: cuántos parámetros entrenas de verdad frente al modelo base.
2. `memory_by_precision`: cuánto cambia la memoria al variar bits; no lo confundas con calidad.
3. `logit_gradients`: qué dirección empuja la pérdida.
4. `kl_distillation`: distancia entre profesor y estudiante.
5. `decision`: si el problema pide adaptar estilo, comprimir, destilar o no tocar pesos.

## Cómo lo adaptas a tu caso

Cambia rango LoRA, dimensión, precisión y logits en `data/adaptation_case.json`. Una entrega fuerte no elige LoRA por moda: explica si quiere cambiar formato estable, reducir coste, copiar comportamiento de un profesor o mantener conocimiento vivo fuera de los pesos.

## Qué entregaría un alumno

El Markdown generado, otro rango LoRA, otra precisión y una decisión: LoRA, adapter, cuantización, destilación o no adaptar.

## Qué te llevas

Te llevas una práctica ejecutable sobre presupuesto de adaptación y destilación, con datos editables, contratos y umbrales, plantillas de entrega, código ejecutable y tests reproducibles. Trabajas con `data/adaptation_case.json`, contrastas la decisión contra `contracts/adaptation_policy.json` y ejecutas `ops/estimate_adaptation_budget.py` para generar `output/adaptation_budget_decision.md`. La idea no es mirar una solución cerrada: es cambiar una entrada, volver a ejecutar, comparar la salida y poder defender qué harías en una revisión técnica, una asignatura o un piloto real.

## Variantes para hacerlo tuyo

- Ejecuta `make run` sin tocar nada y usa `output/adaptation_budget_decision.md` como línea base.
- Cambia o añade un caso en `data/adaptation_case.json` para representar un problema de tu trabajo, clase o producto.
- Endurece una regla, umbral o campo obligatorio en `contracts/adaptation_policy.json` y explica por qué el resultado debería cambiar o bloquearse.
- Compara antes/después en `output/adaptation_budget_decision.md` y `output/adaptation_budget_report.json` y escribe una decisión de una página: seguir, bloquear, medir más o cambiar el diseño.
- Completa `templates/entrega.md` con contexto, cambio, evidencia, decisión y límite; no la dejes como checklist vacía.

## Rúbrica rápida

| Nivel | Qué demuestra |
|---|---|
| Mínimo | Ejecuta `make run` y `make test`, localiza `ops/estimate_adaptation_budget.py`, abre `output/adaptation_budget_decision.md` y explica qué decisión o señal produce. |
| Bueno | Cambia `data/adaptation_case.json`, compara antes/después y justifica la diferencia con una evidencia concreta del output. |
| Excelente | Convierte el kit en un mini caso profesional: añade un caso propio, ajusta una regla o test, documenta el límite principal y deja una recomendación accionable para un equipo. |

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `Kit F3 C06: presupuesto de adaptación y destilación`, no escondido en una ruta del repositorio.

### Qué contiene

- `README.md`: esta guía y la explicación del ejercicio.
- `Makefile`: entrada única para ejecutar y validar el kit con `make run` y `make test`.
- `requirements.txt`: dependencias declaradas; muchos kits solo usan la biblioteca estándar de Python.
- `data/`: datos de entrada o casos de prueba realistas. Ejemplos dentro del ZIP: `data/adaptation_case.json`.
- `contracts/`: contratos de datos, salida, política o validación. Ejemplos dentro del ZIP: `contracts/adaptation_policy.json`.
- `templates/`: plantillas editables para la entrega. Ejemplos dentro del ZIP: `templates/entrega.md`.
- `ops/`: código ejecutable del laboratorio. Ejemplos dentro del ZIP: `ops/estimate_adaptation_budget.py`.
- `tests/`: tests que comprueban que el ejercicio sigue siendo reproducible. Ejemplos dentro del ZIP: `tests/test_lab_contract.py`.
- `output/`: salidas generadas o esperadas que debes revisar. Ejemplos dentro del ZIP: `output/adaptation_budget_decision.md`, `output/adaptation_budget_report.json`.

### Ejecutar desde cero

Desde la carpeta extraída del ZIP:

```bash
make run
make test
```

`make run` construye las evidencias del ejercicio. `make test` comprueba que el kit sigue siendo ejecutable después de descargarlo, extraerlo y tocarlo.

### Qué mirar antes de entregar

- `output/adaptation_budget_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/adaptation_budget_report.json`: evidencia estructurada para validar o automatizar.

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
