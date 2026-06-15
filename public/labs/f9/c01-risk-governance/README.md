# Kit f9/c01: registro de riesgos, controles y evidencias

Este kit convierte el capítulo 01 del facsímil 09 en una práctica de ingeniería. La idea es sencilla: antes de publicar una capacidad de IA, el equipo debe poder explicar qué sistema está evaluando, qué escenarios le preocupan, qué controles existen, qué evidencia falta y qué decisión tomaría.

## Qué vas a crear

| Archivo | Para qué sirve |
|---|---|
| `contracts/ai_system_context.json` | Describe el sistema de IA, su finalidad, datos, integraciones, owners y fase de release. |
| `contracts/control_policy.json` | Define umbrales, controles mínimos y evidencias obligatorias. |
| `data/risk_scenarios.csv` | Lista escenarios de riesgo con probabilidad, impacto, exposición y hueco de detección. |
| `output/risk_register.json` | Registro completo calculado por el script. |
| `output/risk_register.md` | Versión legible para revisión técnica o clase. |
| `output/control_matrix.csv` | Matriz que cruza escenarios, controles, owners y evidencias. |
| `output/release_gate.md` | Decisión de salida con condiciones concretas. |
| `output/evidence_pack/release_manifest.json` | Manifest de versión para reconstruir modelo, prompt, índice, policy y decisión. |
| `output/evidence_pack/evidence_index.md` | Índice de evidencias que conecta marcos, artefactos y owners. |
| `output/evidence_pack/trace_sample.jsonl` | Traza mínima de ejemplo para discutir qué se conserva y qué se oculta. |
| `output/evidence_pack/privacy_review.md` | Primera revisión de privacidad para abrir el capítulo siguiente. |

## Cómo ejecutarlo

Desde está carpeta:

```bash
python3 ops/build_risk_register.py --write
```

No necesita dependencias externas. Usa solo la biblioteca estándar de Python.

## Qué deberías ver

El script imprimirá un resumen parecido a este:

```text
escenarios: 8
críticos: 1
altos: 4
decisión: revisar_antes_de_publicar
```

Y dejará los archivos en `output/`.

## Cómo adaptarlo a tu caso

Cambia primero `contracts/ai_system_context.json`: nombre del sistema, finalidad, datos tratados, integraciones y fase de release. Después modifica `data/risk_scenarios.csv` con tus escenarios reales. Mantén la escala 1-5 para que las decisiones sean comparables entre equipos.

La regla más importante: no añadas un riesgo si no puedes asignarle owner, control y evidencia. Si no hay evidencia, la decisión debe decirlo.

## Entregable de alumno

Un entregable serio incluye:

1. `risk_register.md` con lectura ejecutiva.
2. `control_matrix.csv` revisado.
3. `release_gate.md` con decisión y condiciones.
4. `evidence_pack/` revisado, especialmente `release_manifest.json` y `evidence_index.md`.
5. Un párrafo explicando qué cambiaría antes de publicar.
6. Un diff o comentario señalando qué campos adaptó a su proyecto.

## Qué te llevas

Te llevas una práctica ejecutable sobre registro de riesgos, controles y evidencias, con datos editables, contratos y umbrales, plantillas de entrega, código ejecutable y tests reproducibles. Trabajas con `data/risk_scenarios.csv`, contrastas la decisión contra `contracts/ai_system_context.json` y `contracts/control_policy.json` y ejecutas `ops/build_risk_register.py` para generar `output/evidence_pack/evidence_index.md`. La idea no es mirar una solución cerrada: es cambiar una entrada, volver a ejecutar, comparar la salida y poder defender qué harías en una revisión técnica, una asignatura o un piloto real.

## Variantes para hacerlo tuyo

- Ejecuta `make run` sin tocar nada y usa `output/evidence_pack/evidence_index.md` como línea base.
- Cambia o añade un caso en `data/risk_scenarios.csv` para representar un problema de tu trabajo, clase o producto.
- Endurece una regla, umbral o campo obligatorio en `contracts/ai_system_context.json` y `contracts/control_policy.json` y explica por qué el resultado debería cambiar o bloquearse.
- Compara antes/después en `output/evidence_pack/evidence_index.md` y `output/evidence_pack/privacy_review.md` y escribe una decisión de una página: seguir, bloquear, medir más o cambiar el diseño.
- Completa `templates/entrega.md` con contexto, cambio, evidencia, decisión y límite; no la dejes como checklist vacía.

## Rúbrica rápida

| Nivel | Qué demuestra |
|---|---|
| Mínimo | Ejecuta `make run` y `make test`, localiza `ops/build_risk_register.py`, abre `output/evidence_pack/evidence_index.md` y explica qué decisión o señal produce. |
| Bueno | Cambia `data/risk_scenarios.csv`, compara antes/después y justifica la diferencia con una evidencia concreta del output. |
| Excelente | Convierte el kit en un mini caso profesional: añade un caso propio, ajusta una regla o test, documenta el límite principal y deja una recomendación accionable para un equipo. |

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `Kit f9/c01: registro de riesgos, controles y evidencias`, no escondido en una ruta del repositorio.

### Qué contiene

- `README.md`: esta guía y la explicación del ejercicio.
- `Makefile`: entrada única para ejecutar y validar el kit con `make run` y `make test`.
- `requirements.txt`: dependencias declaradas; muchos kits solo usan la biblioteca estándar de Python.
- `data/`: datos de entrada o casos de prueba realistas. Ejemplos dentro del ZIP: `data/risk_scenarios.csv`.
- `contracts/`: contratos de datos, salida, política o validación. Ejemplos dentro del ZIP: `contracts/ai_system_context.json`, `contracts/control_policy.json`.
- `templates/`: plantillas editables para la entrega. Ejemplos dentro del ZIP: `templates/entrega.md`.
- `ops/`: código ejecutable del laboratorio. Ejemplos dentro del ZIP: `ops/build_risk_register.py`.
- `tests/`: tests que comprueban que el ejercicio sigue siendo reproducible. Ejemplos dentro del ZIP: `tests/test_lab_contract.py`.
- `output/`: salidas generadas o esperadas que debes revisar. Ejemplos dentro del ZIP: `output/evidence_pack/evidence_index.md`, `output/evidence_pack/privacy_review.md`, `output/release_gate.md`, `output/risk_register.md`, ....

### Ejecutar desde cero

Desde la carpeta extraída del ZIP:

```bash
make run
make test
```

`make run` construye las evidencias del ejercicio. `make test` comprueba que el kit sigue siendo ejecutable después de descargarlo, extraerlo y tocarlo.

### Qué mirar antes de entregar

- `output/evidence_pack/evidence_index.md`: lectura humana de la decisión, informe o runbook.
- `output/evidence_pack/privacy_review.md`: lectura humana de la decisión, informe o runbook.
- `output/release_gate.md`: lectura humana de la decisión, informe o runbook.
- `output/risk_register.md`: lectura humana de la decisión, informe o runbook.
- `output/evidence_pack/release_manifest.json`: evidencia estructurada para validar o automatizar.
- `output/risk_register.json`: evidencia estructurada para validar o automatizar.
- `output/evidence_pack/trace_sample.jsonl`: eventos o registros línea a línea.
- `output/control_matrix.csv`: tabla que puedes inspeccionar o cargar en un notebook.

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
