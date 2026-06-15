# Kit F7: laboratorio de cierre de evaluación

Este kit une los capítulos del facsímil 7 en un expediente de release. No sustituye los kits de calibración e interpretabilidad: los usa como evidencias.

## Qué construyes

El resultado es una carpeta de entrega con:

```text
release-eval/
  eval_contract.json
  rag_eval_report.json
  evaluator_metaeval.json
  calibration_manifest.json
  interpretability_report.json
  explanation_contract.json
  ci_explanation_gate.json
  model_card_fragment.md
  release_eval_report.json
  source_evidence_matrix.csv
  ci_release_gate.json
  decision.md
```

## Ejecutar desde cero

Este kit ya incluye en `evidence/` las evidencias mínimas necesarias para que funcione descargado de forma independiente. En el repositorio completo esas evidencias se relacionan con los kits de calibración e interpretabilidad, pero aquí no necesitas rutas hermanas para practicar el cierre.

```bash
make run
make test
```

Si quieres ejecutar solo el empaquetador:

```bash
python3 ops/build_release_eval_pack.py --write
python3 -m json.tool output/ci_release_gate.json
cat output/decision.md
```

La salida esperada de referencia es `publicar_con_condiciones`. No es un fallo: el paquete no tiene bloqueos, pero conserva puntos de revisión como cola larga de RAG, intervalo Wilson amplio y concentración de feature principal.

## Variante para practicar

Ejecuta una variante con evidencias más débiles:

```bash
python3 ops/build_release_eval_pack.py \
  --rag-report evidence/rag_eval_report_student.json \
  --evaluator-report evidence/evaluator_metaeval_student.json \
  --output-dir output/student \
  --write
python3 -m json.tool output/student/ci_release_gate.json
cat output/student/decision.md
```

Esta variante debe quedar bloqueada. Sirve para practicar una decisión incómoda: explicar por qué una release no puede avanzar aunque algunas métricas parezcan cercanas.

## Validar una entrega

El checker espera una carpeta con los artefactos finales:

```bash
python3 ops/check_student_submission.py --submission-dir solutions/reference --write
```

Para una entrega propia:

```bash
python3 ops/check_student_submission.py --submission-dir solutions/mi-equipo --write --fail-on-missing
```

## Cómo leer el resultado

| Archivo | Lectura |
|---|---|
| `source_evidence_matrix.csv` | Qué capítulo sostiene cada check y qué evidencia usa. |
| `release_eval_report.json` | Resultado estructurado del gate. |
| `ci_release_gate.json` | Salida pequeña para CI. |
| `decision.md` | Decisión profesional explicada. |
| `release_eval_package_manifest.json` | Inventario del paquete entregado. |

## Qué entregaría un alumno

1. Carpeta `release-eval/` completa.
2. Una decisión técnica: publicar, publicar con condiciones o bloquear.
3. Una explicación de cada check fuera de umbral.
4. Una tarea de mejora por cada bloqueo o revisión.
5. Una nota breve de qué cambiaría en el dataset de evaluación.

El objetivo no es conseguir todos los números perfectos. El objetivo es aprender a defender una decisión con evidencias conectadas al temario: RAG, evaluador, calibración e interpretabilidad.

## Qué te llevas

Te llevas una práctica ejecutable sobre laboratorio de cierre de evaluación, con contratos y umbrales, evidencias fuente, plantillas de entrega, código ejecutable y tests reproducibles. Trabajas con `evidence/calibration_manifest.json` y `evidence/calibration_report.json`, contrastas la decisión contra `contracts/release_eval_contract.json` y ejecutas `ops/build_release_eval_pack.py` para generar `output/decision.md`. La idea no es mirar una solución cerrada: es cambiar una entrada, volver a ejecutar, comparar la salida y poder defender qué harías en una revisión técnica, una asignatura o un piloto real.

## Variantes para hacerlo tuyo

- Ejecuta `make run` sin tocar nada y usa `output/decision.md` como línea base.
- Cambia o añade un caso en `evidence/calibration_manifest.json` y `evidence/calibration_report.json` para representar un problema de tu trabajo, clase o producto.
- Endurece una regla, umbral o campo obligatorio en `contracts/release_eval_contract.json` y explica por qué el resultado debería cambiar o bloquearse.
- Compara antes/después en `output/decision.md` y `output/model_card_fragment.md` y escribe una decisión de una página: seguir, bloquear, medir más o cambiar el diseño.
- Completa `templates/entrega.md` con contexto, cambio, evidencia, decisión y límite; no la dejes como checklist vacía.

## Rúbrica rápida

| Nivel | Qué demuestra |
|---|---|
| Mínimo | Ejecuta `make run` y `make test`, localiza `ops/build_release_eval_pack.py`, abre `output/decision.md` y explica qué decisión o señal produce. |
| Bueno | Cambia `evidence/calibration_manifest.json`, compara antes/después y justifica la diferencia con una evidencia concreta del output. |
| Excelente | Convierte el kit en un mini caso profesional: añade un caso propio, ajusta una regla o test, documenta el límite principal y deja una recomendación accionable para un equipo. |

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `Kit F7: laboratorio de cierre de evaluación`, no escondido en una ruta del repositorio.

### Qué contiene

- `README.md`: esta guía y la explicación del ejercicio.
- `Makefile`: entrada única para ejecutar y validar el kit con `make run` y `make test`.
- `requirements.txt`: dependencias declaradas; muchos kits solo usan la biblioteca estándar de Python.
- `contracts/`: contratos de datos, salida, política o validación. Ejemplos dentro del ZIP: `contracts/release_eval_contract.json`.
- `templates/`: plantillas editables para la entrega. Ejemplos dentro del ZIP: `templates/entrega.md`.
- `evidence/`: evidencias preconstruidas que el kit usa como entrada o referencia. Ejemplos dentro del ZIP: `evidence/model_card_interpretability.md`, `evidence/calibration_manifest.json`, `evidence/calibration_report.json`, `evidence/ci_explanation_gate.json`, ....
- `ops/`: código ejecutable del laboratorio. Ejemplos dentro del ZIP: `ops/build_release_eval_pack.py`, `ops/check_student_submission.py`.
- `tests/`: tests que comprueban que el ejercicio sigue siendo reproducible. Ejemplos dentro del ZIP: `tests/test_lab_contract.py`.
- `output/`: salidas generadas o esperadas que debes revisar. Ejemplos dentro del ZIP: `output/decision.md`, `output/model_card_fragment.md`, `output/student/decision.md`, `output/student/model_card_fragment.md`, ....
- `solutions/`: soluciones de referencia o carpeta para la entrega del alumno. Ejemplos dentro del ZIP: `solutions/mi-equipo/README.md`, `solutions/reference/decision.md`, `solutions/reference/model_card_fragment.md`, `solutions/reference/calibration_manifest.json`, ....

### Ejecutar desde cero

Desde la carpeta extraída del ZIP:

```bash
make run
make test
```

`make run` construye las evidencias del ejercicio. `make test` comprueba que el kit sigue siendo ejecutable después de descargarlo, extraerlo y tocarlo.

### Qué mirar antes de entregar

- `output/decision.md`: lectura humana de la decisión, informe o runbook.
- `output/model_card_fragment.md`: lectura humana de la decisión, informe o runbook.
- `output/student/decision.md`: lectura humana de la decisión, informe o runbook.
- `output/student/model_card_fragment.md`: lectura humana de la decisión, informe o runbook.
- `output/student_submission_report.md`: lectura humana de la decisión, informe o runbook.
- `solutions/reference/decision.md`: lectura humana de la decisión, informe o runbook.
- `solutions/reference/model_card_fragment.md`: lectura humana de la decisión, informe o runbook.
- `output/calibration_manifest.json`: evidencia estructurada para validar o automatizar.
- `output/calibration_report.json`: evidencia estructurada para validar o automatizar.
- `output/ci_explanation_gate.json`: evidencia estructurada para validar o automatizar.
- `output/ci_release_gate.json`: evidencia estructurada para validar o automatizar.
- `output/eval_contract.json`: evidencia estructurada para validar o automatizar.

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
3. Ajusta `contracts/` cuando cambien tipos, campos obligatorios, umbrales o catálogos permitidos.
4. Usa `templates/` como base documental; no entregues una plantilla sin completar.
5. Coloca tu versión en `solutions/mi-equipo/` y compárala contra la referencia o contra los tests.
6. Guarda los outputs finales y una nota breve con la decisión técnica que tomarías en un proyecto real.

### Criterio de validación

El kit está completo cuando se puede descargar, extraer, ejecutar con `make run`, validar con `make test` y explicar sin depender de ninguna carpeta externa. Si una práctica menciona código, datos, contrato, CSV, SQL, política o plantilla, ese contenido debe venir dentro del ZIP.
<!-- zip-quality-audit:end -->
