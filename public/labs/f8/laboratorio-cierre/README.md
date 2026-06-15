# F8 · Laboratorio de cierre de datos

Este kit acompaña el laboratorio final del facsímil 8. Integra datos, contrato, split, slices, trazabilidad, calidad documental y decisión operativa.

## Ejecutar

```bash
python3 ops/run_final_review.py --write
cat output/final_decision.md
cat output/technical_decision_memo.md
cat output/source_evidence_review.md
python3 -m json.tool output/final_review_report.json
cat output/final_split_summary.csv
cat output/final_slice_summary.csv
```

Escenario corregido por el alumno:

```bash
python3 ops/run_final_review.py \
  --data data/final_project_events_student.csv \
  --output-dir output/student \
  --write

cat output/student/final_decision.md
cat output/student/correction_plan.md
cat output/student/next_experiment_plan.md
python3 -m json.tool output/student/data_release_ci_gate.json
```

Cómo gate:

```bash
python3 ops/run_final_review.py --write --fail-on-blocker
```

Validar una entrega:

```bash
python3 ops/check_student_submission.py --submission-dir solutions/reference --write
cat output/student_submission_report.md
```

La ejecución no busca "aprobar" el sistema. Busca producir una decisión defendible. Lee los artefactos en este orden:

1. `final_decision.md`: estado, lectura ejecutiva, checks y siguiente iteración.
2. `technical_decision_memo.md`: memo defendible para una revisión técnica.
3. `final_review_report.json`: datos estructurados para reproducir la decisión.
4. `final_split_summary.csv`: comportamiento por split.
5. `final_slice_summary.csv`: comportamiento en slices críticos.
6. `source_evidence_review.md`: evidencias fuente que sostienen la decisión.
7. `contracts/final_review_contract.json`: SLOs y umbrales que no se deben cambiar después de ver el resultado.

## Archivos

| Archivo | Papel |
|---|---|
| `data/final_project_events.csv` | Eventos de un mini proyecto de IA con splits, slices, trazas y experimento. |
| `data/final_project_events_student.csv` | Variante corregida parcialmente para que el alumno vea como cambia el gate. |
| `contracts/final_review_contract.json` | SLOs y slices críticos del cierre. |
| `evidence/` | Evidencias fuente: trazabilidad, calidad, slices, exposición experimental y alcance. |
| `ops/run_final_review.py` | Audita contrato, trazabilidad, test, slices y calidad documental. |
| `ops/check_student_submission.py` | Valida una entrega profesional del laboratorio. |
| `output/final_review_report.json` | Reporte completo. |
| `output/final_split_summary.csv` | Resumen por split. |
| `output/final_slice_summary.csv` | Resumen por slice crítico. |
| `output/final_decision.md` | Decisión final defendible. |
| `output/technical_decision_memo.md` | Memo técnico de decisión. |
| `output/source_evidence_review.md` | Revisión de evidencias fuente. |
| `output/correction_plan.md` | Plan de corrección por check abierto. |
| `output/next_experiment_plan.md` | Plan experimental conectado con el slice más debil. |
| `output/data_release_ci_gate.json` | Salida máquina para CI. |

## Qué deberías mirar

1. El estado queda en `block`.
2. Faltan trazas en al menos un evento.
3. Hay campos obligatorios incompletos.
4. Los slices críticos concentran fallos.
5. La decisión final no publica el sistema: pide corregir antes de automatizar.

## Cómo leer el resultado

| Señal | Valor del kit | Lectura |
|---|---:|---|
| `missing_trace_rate` | `0.083333` | Hay una decisión que no se puede reconstruir. Bloquea. |
| `missing_required_fields_rate` | `0.083333` | La ingesta permite filas incompletas. Bloquea. |
| `latency_p95_ms` | `730` | Supera el SLO de `720`. Requiere revisión. |
| `test_accuracy` | `0.6` | No alcanza `0.75`. Requiere revisar split, umbral y errores. |
| `citation_valid_rate` | `0.916667` | Pasa el mínimo documental. No compensa los bloqueos. |
| `language=en` | `0.8` miss rate | Slice crítico con fallo concentrado. |
| `segment=practicas` | `0.75` miss rate | Segmento donde no deberías automatizar aún. |
| `source=form` | `0.666667` miss rate | Fuente con calidad o distribución distinta. |

## Qué te llevas

Te llevas una práctica ejecutable sobre F8 · Laboratorio de cierre de datos, con datos editables, contratos y umbrales, evidencias fuente, plantillas de entrega, código ejecutable y tests reproducibles. Trabajas con `data/final_project_events.csv` y `data/final_project_events_student.csv`, contrastas la decisión contra `contracts/final_review_contract.json` y ejecutas `ops/check_student_submission.py` para generar `output/correction_plan.md`. La idea no es mirar una solución cerrada: es cambiar una entrada, volver a ejecutar, comparar la salida y poder defender qué harías en una revisión técnica, una asignatura o un piloto real.

## Entrega esperada

La entrega buena cabe en una carpeta `final-data-release-review/` con:

```text
final-data-release-review/
  final_decision.md
  technical_decision_memo.md
  final_review_report.json
  final_split_summary.csv
  final_slice_summary.csv
  source_evidence_review.md
  correction_plan.md
  next_experiment_plan.md
  data_release_ci_gate.json
```

`correction_plan.md` debe explicar qué corregirías antes de publicar. `next_experiment_plan.md` debe proponer una intervención medible para el slice más importante, usando el kit del capítulo 07.

Una entrega completa puede validarse con `ops/check_student_submission.py`. La validación no premia que marques todo como correcto: premia que expliques qué se cerró, qué sigue condicionado, qué evidencia lo sostiene y qué experimento vendría después.

## Variantes para hacerlo tuyo

- Ejecuta `make run` sin tocar nada y usa `output/correction_plan.md` como línea base.
- Cambia o añade un caso en `data/final_project_events.csv` y `data/final_project_events_student.csv` para representar un problema de tu trabajo, clase o producto.
- Endurece una regla, umbral o campo obligatorio en `contracts/final_review_contract.json` y explica por qué el resultado debería cambiar o bloquearse.
- Compara antes/después en `output/correction_plan.md` y `output/final_decision.md` y escribe una decisión de una página: seguir, bloquear, medir más o cambiar el diseño.
- Completa `templates/entrega.md` con contexto, cambio, evidencia, decisión y límite; no la dejes como checklist vacía.

## Rúbrica rápida

| Nivel | Qué demuestra |
|---|---|
| Mínimo | Ejecuta `make run` y `make test`, localiza `ops/check_student_submission.py`, abre `output/correction_plan.md` y explica qué decisión o señal produce. |
| Bueno | Cambia `data/final_project_events.csv`, compara antes/después y justifica la diferencia con una evidencia concreta del output. |
| Excelente | Convierte el kit en un mini caso profesional: añade un caso propio, ajusta una regla o test, documenta el límite principal y deja una recomendación accionable para un equipo. |

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `F8 · Laboratorio de cierre de datos`, no escondido en una ruta del repositorio.

### Qué contiene

- `README.md`: esta guía y la explicación del ejercicio.
- `Makefile`: entrada única para ejecutar y validar el kit con `make run` y `make test`.
- `requirements.txt`: dependencias declaradas; muchos kits solo usan la biblioteca estándar de Python.
- `data/`: datos de entrada o casos de prueba realistas. Ejemplos dentro del ZIP: `data/final_project_events.csv`, `data/final_project_events_student.csv`.
- `contracts/`: contratos de datos, salida, política o validación. Ejemplos dentro del ZIP: `contracts/final_review_contract.json`.
- `templates/`: plantillas editables para la entrega. Ejemplos dentro del ZIP: `templates/entrega.md`.
- `evidence/`: evidencias preconstruidas que el kit usa como entrada o referencia. Ejemplos dentro del ZIP: `evidence/data_release_scope.md`, `evidence/slice_remediation_plan.md`, `evidence/traceability_policy.md`, `evidence/data_quality_contract.json`, ....
- `ops/`: código ejecutable del laboratorio. Ejemplos dentro del ZIP: `ops/check_student_submission.py`, `ops/run_final_review.py`.
- `tests/`: tests que comprueban que el ejercicio sigue siendo reproducible. Ejemplos dentro del ZIP: `tests/test_lab_contract.py`.
- `output/`: salidas generadas o esperadas que debes revisar. Ejemplos dentro del ZIP: `output/correction_plan.md`, `output/final_decision.md`, `output/next_experiment_plan.md`, `output/source_evidence_review.md`, ....
- `solutions/`: soluciones de referencia o carpeta para la entrega del alumno. Ejemplos dentro del ZIP: `solutions/mi-equipo/README.md`, `solutions/reference/correction_plan.md`, `solutions/reference/decision_memo.md`, `solutions/reference/final_decision.md`, ....

### Ejecutar desde cero

Desde la carpeta extraída del ZIP:

```bash
make run
make test
```

`make run` construye las evidencias del ejercicio. `make test` comprueba que el kit sigue siendo ejecutable después de descargarlo, extraerlo y tocarlo.

### Qué mirar antes de entregar

- `output/correction_plan.md`: lectura humana de la decisión, informe o runbook.
- `output/final_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/next_experiment_plan.md`: lectura humana de la decisión, informe o runbook.
- `output/source_evidence_review.md`: lectura humana de la decisión, informe o runbook.
- `output/student/correction_plan.md`: lectura humana de la decisión, informe o runbook.
- `output/student/final_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/student/next_experiment_plan.md`: lectura humana de la decisión, informe o runbook.
- `output/student/source_evidence_review.md`: lectura humana de la decisión, informe o runbook.
- `output/student/technical_decision_memo.md`: lectura humana de la decisión, informe o runbook.
- `output/student_submission_report.md`: lectura humana de la decisión, informe o runbook.
- `output/technical_decision_memo.md`: lectura humana de la decisión, informe o runbook.
- `solutions/reference/correction_plan.md`: lectura humana de la decisión, informe o runbook.

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
6. Coloca tu versión en `solutions/mi-equipo/` y compárala contra la referencia o contra los tests.
7. Guarda los outputs finales y una nota breve con la decisión técnica que tomarías en un proyecto real.

### Criterio de validación

El kit está completo cuando se puede descargar, extraer, ejecutar con `make run`, validar con `make test` y explicar sin depender de ninguna carpeta externa. Si una práctica menciona código, datos, contrato, CSV, SQL, política o plantilla, ese contenido debe venir dentro del ZIP.
<!-- zip-quality-audit:end -->
