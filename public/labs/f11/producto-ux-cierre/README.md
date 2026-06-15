# F11 · Laboratorio de producto y UX

Este laboratorio cierra el volumen. El objetivo es decidir si una función de IA merece piloto y si su experiencia permite control, evidencia y recuperación.

## Ejecutar

```bash
python3 ops/score_product_readiness.py --write
python3 ops/review_ux_flows.py --write
cp templates/ai_product_decision.md output/nota_de_decision.md
cp templates/ux_contract.md output/ux_contract.md
python3 ops/check_student_submission.py --submission-dir solutions/reference --write --fail-on-missing
```

## Entradas

| Archivo | Uso |
|---|---|
| `contracts/product_ai_release_policy.json` | Umbrales, pesos y evidencias obligatorias. |
| `data/feature_candidates.csv` | Funciones candidatas con métrica, coste, operación y UX. |
| `data/eval_snapshot.json` | Contexto de evaluación y slices. |
| `data/ux_review_sessions.csv` | Sesiones de revisión UX por escenario. |
| `templates/ai_product_decision.md` | Plantilla PRD/ADR para escribir una decisión propia. |
| `templates/ux_contract.md` | Plantilla de contrato UX con estados, aprobación, recuperación y medición. |

## Salidas

| Archivo | Qué demuestra |
|---|---|
| `output/product_readiness_report.json` | Score y bloqueos por función candidata. |
| `output/product_release_decision.md` | Decisión de producto con condiciones de piloto. |
| `output/metric_tree.md` | Árbol de métricas de valor, calidad, UX, coste y operación. |
| `output/unit_economics.csv` | Coste por tarea útil y margen esperado. |
| `output/ux_review_report.json` | Revisión de estados, evidencia, recuperación y accesibilidad. |
| `output/ux_release_gate.json` | Gate máquina de UX. |
| `output/ux_decision.md` | Cambios obligatorios de experiencia. |
| `output/final_product_packet.md` | Resumen integrador del paquete final. |
| `output/student_submission_report.md` | Resultado del checker de una entrega. |
| `output/nota_de_decision.md` | Plantilla copiada para que el alumno la rellene con su criterio. |
| `output/ux_contract.md` | Plantilla copiada para que el alumno escriba un contrato UX defendible. |

## Retos oficiales

### Reto 1: decidir si una función de IA merece piloto

Genera el score de producto, revisa la unidad económica y escribe una decisión defendible: piloto limitado, piloto condicionado o no piloto.

Usa `templates/ai_product_decision.md` para convertir el resultado del script en una decisión propia. No basta con repetir el JSON: hay que explicar problema, baseline, métrica norte, guardrails, unidad económica, análisis de sensibilidad, slices, plan de piloto y criterios de no construir.

### Reto 2: diseñar la experiencia de control y recuperación

Revisa los escenarios UX, identifica huecos y produce un gate que impida publicar una experiencia sin estados, evidencia o recuperación.

## Entrega esperada

```text
entrega-f11/
  product_release_decision.md
  metric_tree.md
  unit_economics.csv
  nota_de_decision.md
  ux_contract.md
  ux_decision.md
  ux_release_gate.json
  final_product_packet.md
```

Una entrega buena no promete "IA" en abstracto. Explica qué tarea se mejora, qué alternativa sin IA existe, qué coste tiene, qué variable rompe la decisión, qué límites se muestran, qué recuperación se ofrece, quién revisa cada guardrail y qué condiciones obligan a parar o repetir el piloto.

## Qué te llevas

Te llevas una práctica ejecutable sobre F11 · Laboratorio de producto y UX, con datos editables, contratos y umbrales, plantillas de entrega, código ejecutable y tests reproducibles. Trabajas con `data/feature_candidates.csv` y `data/ux_review_sessions.csv`, contrastas la decisión contra `contracts/product_ai_release_policy.json` y ejecutas `ops/check_student_submission.py` para generar `output/final_product_packet.md`. La idea no es mirar una solución cerrada: es cambiar una entrada, volver a ejecutar, comparar la salida y poder defender qué harías en una revisión técnica, una asignatura o un piloto real.

## Variantes para hacerlo tuyo

- Ejecuta `make run` sin tocar nada y usa `output/final_product_packet.md` como línea base.
- Cambia o añade un caso en `data/feature_candidates.csv` y `data/ux_review_sessions.csv` para representar un problema de tu trabajo, clase o producto.
- Endurece una regla, umbral o campo obligatorio en `contracts/product_ai_release_policy.json` y explica por qué el resultado debería cambiar o bloquearse.
- Compara antes/después en `output/final_product_packet.md` y `output/metric_tree.md` y escribe una decisión de una página: seguir, bloquear, medir más o cambiar el diseño.
- Completa `templates/entrega.md` con contexto, cambio, evidencia, decisión y límite; no la dejes como checklist vacía.

## Rúbrica rápida

| Nivel | Qué demuestra |
|---|---|
| Mínimo | Ejecuta `make run` y `make test`, localiza `ops/check_student_submission.py`, abre `output/final_product_packet.md` y explica qué decisión o señal produce. |
| Bueno | Cambia `data/feature_candidates.csv`, compara antes/después y justifica la diferencia con una evidencia concreta del output. |
| Excelente | Convierte el kit en un mini caso profesional: añade un caso propio, ajusta una regla o test, documenta el límite principal y deja una recomendación accionable para un equipo. |

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `F11 · Laboratorio de producto y UX`, no escondido en una ruta del repositorio.

### Qué contiene

- `README.md`: esta guía y la explicación del ejercicio.
- `Makefile`: entrada única para ejecutar y validar el kit con `make run` y `make test`.
- `requirements.txt`: dependencias declaradas; muchos kits solo usan la biblioteca estándar de Python.
- `data/`: datos de entrada o casos de prueba realistas. Ejemplos dentro del ZIP: `data/eval_snapshot.json`, `data/feature_candidates.csv`, `data/ux_review_sessions.csv`.
- `contracts/`: contratos de datos, salida, política o validación. Ejemplos dentro del ZIP: `contracts/product_ai_release_policy.json`.
- `templates/`: plantillas editables para la entrega. Ejemplos dentro del ZIP: `templates/ai_product_decision.md`, `templates/entrega.md`, `templates/ux_contract.md`.
- `ops/`: código ejecutable del laboratorio. Ejemplos dentro del ZIP: `ops/check_student_submission.py`, `ops/review_ux_flows.py`, `ops/score_product_readiness.py`.
- `tests/`: tests que comprueban que el ejercicio sigue siendo reproducible. Ejemplos dentro del ZIP: `tests/test_lab_contract.py`.
- `output/`: salidas generadas o esperadas que debes revisar. Ejemplos dentro del ZIP: `output/final_product_packet.md`, `output/metric_tree.md`, `output/nota_de_decision.md`, `output/product_release_decision.md`, ....
- `solutions/`: soluciones de referencia o carpeta para la entrega del alumno. Ejemplos dentro del ZIP: `solutions/reference/final_product_packet.md`, `solutions/reference/metric_tree.md`, `solutions/reference/nota_de_decision.md`, `solutions/reference/product_release_decision.md`, ....

### Ejecutar desde cero

Desde la carpeta extraída del ZIP:

```bash
make run
make test
```

`make run` construye las evidencias del ejercicio. `make test` comprueba que el kit sigue siendo ejecutable después de descargarlo, extraerlo y tocarlo.

### Qué mirar antes de entregar

- `output/final_product_packet.md`: lectura humana de la decisión, informe o runbook.
- `output/metric_tree.md`: lectura humana de la decisión, informe o runbook.
- `output/nota_de_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/product_release_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/student_submission_report.md`: lectura humana de la decisión, informe o runbook.
- `output/ux_contract.md`: lectura humana de la decisión, informe o runbook.
- `output/ux_decision.md`: lectura humana de la decisión, informe o runbook.
- `solutions/reference/final_product_packet.md`: lectura humana de la decisión, informe o runbook.
- `solutions/reference/metric_tree.md`: lectura humana de la decisión, informe o runbook.
- `solutions/reference/nota_de_decision.md`: lectura humana de la decisión, informe o runbook.
- `solutions/reference/product_release_decision.md`: lectura humana de la decisión, informe o runbook.
- `solutions/reference/ux_contract.md`: lectura humana de la decisión, informe o runbook.

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
6. Usa `solutions/` como contraste de calidad, no como sustituto de tu razonamiento.
7. Guarda los outputs finales y una nota breve con la decisión técnica que tomarías en un proyecto real.

### Criterio de validación

El kit está completo cuando se puede descargar, extraer, ejecutar con `make run`, validar con `make test` y explicar sin depender de ninguna carpeta externa. Si una práctica menciona código, datos, contrato, CSV, SQL, política o plantilla, ese contenido debe venir dentro del ZIP.
<!-- zip-quality-audit:end -->
