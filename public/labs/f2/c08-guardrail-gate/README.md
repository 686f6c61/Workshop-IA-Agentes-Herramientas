# Kit F2 C08: guardrail gate para tools

Este kit acompaña el capítulo 08 del facsímil 2. Evalúa llamadas candidatas a una tool de reembolso con controles ejecutables: schema, permisos, política de estado, riesgo e invariantes.

El objetivo es practicar el patrón: el LLM propone, la aplicación decide, el log permite auditar.

## Ejecutar

Desde esta carpeta:

```bash
python3 ops/evaluate_guardrails.py --write
cat output/guardrail_decision.md
```

Como gate:

```bash
python3 ops/evaluate_guardrails.py --write --fail-on-invalid
```

## Archivos

| Archivo | Papel |
|---|---|
| `data/refund_calls.json` | Tool calls candidatas con usuario, estado y riesgo. |
| `contracts/guardrail_policy.json` | Límites de rol, umbrales HITL y reglas del guardrail. |
| `ops/evaluate_guardrails.py` | Evaluador sin dependencias externas. |
| `output/guardrail_report.json` | Resultado estructurado por llamada. |
| `output/guardrail_audit_log.jsonl` | Log de auditoría línea a línea. |
| `output/guardrail_decision.md` | Informe legible para entregar. |

## Qué deberías mirar

1. Qué controles se evalúan en cada llamada.
2. Qué diferencia hay entre `DENY` y `HITL`.
3. Qué ocurre cuando el schema falla.
4. Por qué una llamada con forma correcta puede no estar autorizada.
5. Qué información queda en el log de auditoría.

## Qué entregaría un alumno

1. El Markdown generado.
2. Una tool nueva con su contrato.
3. Un caso `ALLOW`, uno `DENY` y uno `HITL`.
4. Una política de límites por rol.
5. Una explicación de qué haría *fail closed* si falta el estado del pedido.

## Qué te llevas

Te llevas una práctica ejecutable sobre guardrail gate para tools, con datos editables, contratos y umbrales, plantillas de entrega, código ejecutable y tests reproducibles. Trabajas con `data/refund_calls.json`, contrastas la decisión contra `contracts/guardrail_policy.json` y ejecutas `ops/evaluate_guardrails.py` para generar `output/guardrail_decision.md`. La idea no es mirar una solución cerrada: es cambiar una entrada, volver a ejecutar, comparar la salida y poder defender qué harías en una revisión técnica, una asignatura o un piloto real.

## Variantes para hacerlo tuyo

- Ejecuta `make run` sin tocar nada y usa `output/guardrail_decision.md` como línea base.
- Cambia o añade un caso en `data/refund_calls.json` para representar un problema de tu trabajo, clase o producto.
- Endurece una regla, umbral o campo obligatorio en `contracts/guardrail_policy.json` y explica por qué el resultado debería cambiar o bloquearse.
- Compara antes/después en `output/guardrail_decision.md` y `output/guardrail_report.json` y escribe una decisión de una página: seguir, bloquear, medir más o cambiar el diseño.
- Completa `templates/entrega.md` con contexto, cambio, evidencia, decisión y límite; no la dejes como checklist vacía.

## Rúbrica rápida

| Nivel | Qué demuestra |
|---|---|
| Mínimo | Ejecuta `make run` y `make test`, localiza `ops/evaluate_guardrails.py`, abre `output/guardrail_decision.md` y explica qué decisión o señal produce. |
| Bueno | Cambia `data/refund_calls.json`, compara antes/después y justifica la diferencia con una evidencia concreta del output. |
| Excelente | Convierte el kit en un mini caso profesional: añade un caso propio, ajusta una regla o test, documenta el límite principal y deja una recomendación accionable para un equipo. |

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `Kit F2 C08: guardrail gate para tools`, no escondido en una ruta del repositorio.

### Qué contiene

- `README.md`: esta guía y la explicación del ejercicio.
- `Makefile`: entrada única para ejecutar y validar el kit con `make run` y `make test`.
- `requirements.txt`: dependencias declaradas; muchos kits solo usan la biblioteca estándar de Python.
- `data/`: datos de entrada o casos de prueba realistas. Ejemplos dentro del ZIP: `data/refund_calls.json`.
- `contracts/`: contratos de datos, salida, política o validación. Ejemplos dentro del ZIP: `contracts/guardrail_policy.json`.
- `templates/`: plantillas editables para la entrega. Ejemplos dentro del ZIP: `templates/entrega.md`.
- `ops/`: código ejecutable del laboratorio. Ejemplos dentro del ZIP: `ops/evaluate_guardrails.py`.
- `tests/`: tests que comprueban que el ejercicio sigue siendo reproducible. Ejemplos dentro del ZIP: `tests/test_lab_contract.py`.
- `output/`: salidas generadas o esperadas que debes revisar. Ejemplos dentro del ZIP: `output/guardrail_decision.md`, `output/guardrail_report.json`, `output/guardrail_audit_log.jsonl`.

### Ejecutar desde cero

Desde la carpeta extraída del ZIP:

```bash
make run
make test
```

`make run` construye las evidencias del ejercicio. `make test` comprueba que el kit sigue siendo ejecutable después de descargarlo, extraerlo y tocarlo.

### Qué mirar antes de entregar

- `output/guardrail_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/guardrail_report.json`: evidencia estructurada para validar o automatizar.
- `output/guardrail_audit_log.jsonl`: eventos o registros línea a línea.

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
