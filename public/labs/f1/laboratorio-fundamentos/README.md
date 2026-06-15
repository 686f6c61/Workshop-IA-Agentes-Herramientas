# F1 · Laboratorio de fundamentos

Este kit convierte el laboratorio del facsímil 1 en una práctica ejecutable. Trabaja dos ideas base: decidir con métricas y entender un buscador semántico pequeño antes de esconderlo detrás de una API.

## Ejecutar

```bash
make run
make test
```

`make run` genera las salidas del clasificador, las salidas del buscador semántico, una solución de referencia y el informe del checker. `make test` ejecuta pruebas de regresión sobre las métricas, las trazas y la entrega de referencia. Si prefieres ejecutar las piezas por separado:

```bash
python3 ops/evaluate_classifier.py --write --fail-on-review
python3 ops/run_semantic_search.py --write --fail-on-review
```

Generar una solución de referencia:

```bash
python3 ops/evaluate_classifier.py --output-dir solutions/reference --write
python3 ops/run_semantic_search.py --output-dir solutions/reference --write
python3 ops/check_student_submission.py --submission-dir solutions/reference --write --fail-on-missing
```

## Entradas

| Archivo | Uso |
|---|---|
| `contracts/fundamentos_lab_contract.json` | Gate de clasificador, capacidad diaria y métricas del buscador. |
| `data/classifier_cases.json` | Matrices de confusión de los dos modelos candidatos. |
| `data/semantic_documents.json` | Documentos, consultas, dimensiones y vectores didácticos. |

## Salidas

| Archivo | Qué demuestra |
|---|---|
| `classifier_metrics.json` | Precision, recall, F1 y cola prioritaria por modelo. |
| `classifier_decision.md` | Decisión explicada para operar con capacidad limitada. |
| `semantic_search_report.json` | Hit@1, MRR y resultados por consulta. |
| `semantic_search_decision.md` | Lectura técnica del buscador. |
| `semantic_search_traces.jsonl` | Trazas mínimas de tokenización, embedding, scoring y ranking. |

## Entrega esperada

La carpeta de entrega debe contener los cinco archivos anteriores. Una entrega buena no dice solo que el modelo B gana: explica por qué el límite de 60 tickets cambia la decisión y por qué Hit@1/MRR no bastarían con dos consultas en un proyecto real.

## Criterios de aceptación

- El alumno puede ejecutar `make run` sin servicios externos ni claves.
- El alumno puede ejecutar `make test` y ver qué parte del laboratorio protege cada prueba.
- La decisión del clasificador no se basa solo en F1: incorpora capacidad operativa diaria.
- La práctica de embeddings incluye trazas mínimas para no esconder el ranking detrás de una puntuación final.

## Qué te llevas

Te llevas una práctica ejecutable sobre F1 · Laboratorio de fundamentos, con datos editables, contratos y umbrales, plantillas de entrega, código ejecutable y tests reproducibles. Trabajas con `data/classifier_cases.json` y `data/semantic_documents.json`, contrastas la decisión contra `contracts/fundamentos_lab_contract.json` y ejecutas `ops/check_student_submission.py` para generar `output/classifier_decision.md`. La idea no es mirar una solución cerrada: es cambiar una entrada, volver a ejecutar, comparar la salida y poder defender qué harías en una revisión técnica, una asignatura o un piloto real.

## Variantes para hacerlo tuyo

- Ejecuta `make run` sin tocar nada y usa `output/classifier_decision.md` como línea base.
- Cambia o añade un caso en `data/classifier_cases.json` y `data/semantic_documents.json` para representar un problema de tu trabajo, clase o producto.
- Endurece una regla, umbral o campo obligatorio en `contracts/fundamentos_lab_contract.json` y explica por qué el resultado debería cambiar o bloquearse.
- Compara antes/después en `output/classifier_decision.md` y `output/semantic_search_decision.md` y escribe una decisión de una página: seguir, bloquear, medir más o cambiar el diseño.
- Completa `templates/entrega.md` con contexto, cambio, evidencia, decisión y límite; no la dejes como checklist vacía.

## Rúbrica rápida

| Nivel | Qué demuestra |
|---|---|
| Mínimo | Ejecuta `make run` y `make test`, localiza `ops/check_student_submission.py`, abre `output/classifier_decision.md` y explica qué decisión o señal produce. |
| Bueno | Cambia `data/classifier_cases.json`, compara antes/después y justifica la diferencia con una evidencia concreta del output. |
| Excelente | Convierte el kit en un mini caso profesional: añade un caso propio, ajusta una regla o test, documenta el límite principal y deja una recomendación accionable para un equipo. |

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `F1 · Laboratorio de fundamentos`, no escondido en una ruta del repositorio.

### Qué contiene

- `README.md`: esta guía y la explicación del ejercicio.
- `Makefile`: entrada única para ejecutar y validar el kit con `make run` y `make test`.
- `requirements.txt`: dependencias declaradas; muchos kits solo usan la biblioteca estándar de Python.
- `data/`: datos de entrada o casos de prueba realistas. Ejemplos dentro del ZIP: `data/classifier_cases.json`, `data/semantic_documents.json`.
- `contracts/`: contratos de datos, salida, política o validación. Ejemplos dentro del ZIP: `contracts/fundamentos_lab_contract.json`.
- `templates/`: plantillas editables para la entrega. Ejemplos dentro del ZIP: `templates/entrega.md`.
- `ops/`: código ejecutable del laboratorio. Ejemplos dentro del ZIP: `ops/check_student_submission.py`, `ops/evaluate_classifier.py`, `ops/run_semantic_search.py`.
- `tests/`: tests que comprueban que el ejercicio sigue siendo reproducible. Ejemplos dentro del ZIP: `tests/test_laboratorio_fundamentos.py`.
- `output/`: salidas generadas o esperadas que debes revisar. Ejemplos dentro del ZIP: `output/classifier_decision.md`, `output/semantic_search_decision.md`, `output/student_submission_report.md`, `output/classifier_metrics.json`, ....
- `solutions/`: soluciones de referencia o carpeta para la entrega del alumno. Ejemplos dentro del ZIP: `solutions/reference/classifier_decision.md`, `solutions/reference/semantic_search_decision.md`, `solutions/reference/classifier_metrics.json`, `solutions/reference/semantic_search_report.json`, ....

### Ejecutar desde cero

Desde la carpeta extraída del ZIP:

```bash
make run
make test
```

`make run` construye las evidencias del ejercicio. `make test` comprueba que el kit sigue siendo ejecutable después de descargarlo, extraerlo y tocarlo.

### Qué mirar antes de entregar

- `output/classifier_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/semantic_search_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/student_submission_report.md`: lectura humana de la decisión, informe o runbook.
- `solutions/reference/classifier_decision.md`: lectura humana de la decisión, informe o runbook.
- `solutions/reference/semantic_search_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/classifier_metrics.json`: evidencia estructurada para validar o automatizar.
- `output/semantic_search_report.json`: evidencia estructurada para validar o automatizar.
- `solutions/reference/classifier_metrics.json`: evidencia estructurada para validar o automatizar.
- `solutions/reference/semantic_search_report.json`: evidencia estructurada para validar o automatizar.
- `output/semantic_search_traces.jsonl`: eventos o registros línea a línea.
- `solutions/reference/semantic_search_traces.jsonl`: eventos o registros línea a línea.

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
