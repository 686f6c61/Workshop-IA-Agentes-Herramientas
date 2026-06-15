# Kit F8 C03: splits, muestreo y leakage

Este kit acompaña el capítulo 03 del facsímil 8. Compara varias estrategias de partición sobre un dataset sintético de soporte académico con grupos, fechas, textos parecidos y fuentes compartidas.

El objetivo no es obtener el porcentaje perfecto de train/validation/test. El objetivo es aprender a elegir una partición que responda a la pregunta de evaluación sin contaminarla.

## Ejecutar

Desde está carpeta:

```bash
python3 ops/split_audit.py --write
cat output/split_decision.md
python3 ops/preprocessing_fit_audit.py --write
cat output/preprocessing_fit_decision.md
python3 ops/evaluate_test_slices.py --write
cat output/evaluation_slice_decision.md
```

## Archivos

| Archivo | Papel |
|---|---|
| `data/support_split_cases.csv` | Dataset sintético con estudiantes, fechas, fuentes y etiquetas. |
| `data/model_predictions.csv` | Predicciones de ejemplo para evaluar solo los casos asignados a test. |
| `contracts/split_policy.json` | Politica de partición, umbrales y checks de leakage. |
| `contracts/evaluation_use_policy.md` | Reglas de uso de train, validation, test y holdout. |
| `contracts/preprocessing_policy.json` | Contrato para evitar leakage de transformaciones. |
| `contracts/rag_llm_eval_policy.json` | Contrato para RAG, LLM eval, prompts, chunks y trazas. |
| `ops/split_audit.py` | Compara estrategias de split sin dependencias externas. |
| `ops/preprocessing_fit_audit.py` | Comprueba que un vectorizador no aprenda vocabulario desde validation o test. |
| `ops/evaluate_test_slices.py` | Evalúa predicciones de test con accuracy, intervalo aproximado, slices y latencia. |
| `output/split_report.json` | Reporte completo por estrategia. |
| `output/split_manifest.json` | Manifiesto reproducible con hashes, estrategia y asignaciones. |
| `output/strategy_comparison.csv` | Tabla compacta para comparar estrategias. |
| `output/leakage_findings.csv` | Hallazgos de leakage exacto, cercano, grupo, fuente y tiempo. |
| `output/split_assignments.csv` | Asignacion de cada caso por estrategia. |
| `output/split_decision.md` | Decisión técnica recomendada. |
| `output/preprocessing_fit_report.json` | Vocabulario aprendido con train frente a todo el dataset. |
| `output/preprocessing_fit_decision.md` | Decisión sobre si el preprocesado contamina la evaluación. |
| `output/evaluation_slice_report.json` | Métricas de test por producto, canal y etiqueta. |
| `output/evaluation_slice_decision.md` | Lectura operativa de la evaluación final. |

## Qué deberías mirar

1. `random_row`: suele parecer razonable, pero mezcla estudiantes entre splits.
2. `stratified_label`: conserva etiquetas, pero puede filtrar grupos o fuentes.
3. `group_holdout`: evita que el mismo estudiante aparezca en train y test.
4. `time_cutoff`: simula mejor una decisión futura, pero puede cambiar la distribución.
5. `time_group_holdout`: combina orden temporal y grupos no compartidos.
6. `leakage_findings.csv`: explica por que una estrategia queda bloqueada o en revisión.
7. `split_manifest.json`: deja rastro de dataset, política, estrategia y permisos de uso.
8. `preprocessing_policy.json`: recuerda que las transformaciones con `fit` aprenden solo desde train.
9. `rag_llm_eval_policy.json`: evita que documentos, chunks, ejemplos de prompt o respuestas esperadas crucen donde no deben.
10. `preprocessing_fit_report.json`: ensena que ajustar vocabulario con todo el dataset aprende terminos reservados.
11. `evaluation_slice_report.json`: muestra por que una accuracy global no basta si el test es pequeño.

## Qué entregaría un alumno

1. Reporte JSON generado.
2. Comparación de estrategias.
3. Decisión de split justificada.
4. Manifiesto de split con hashes y asignaciones.
5. Un cambio en `split_policy.json` para su propio caso.
6. Reporte de preprocesado con `fit` solo con train.
7. Reporte de evaluación por slices.
8. Una explicación de que leakage evita su estrategia y que leakage no evita.

## Qué te llevas

Te llevas una práctica ejecutable sobre splits, muestreo y leakage, con datos editables, contratos y umbrales, plantillas de entrega, código ejecutable y tests reproducibles. Trabajas con `data/model_predictions.csv` y `data/support_split_cases.csv`, contrastas la decisión contra `contracts/evaluation_use_policy.md` y `contracts/preprocessing_policy.json` y ejecutas `ops/evaluate_test_slices.py` para generar `output/evaluation_slice_decision.md`. La idea no es mirar una solución cerrada: es cambiar una entrada, volver a ejecutar, comparar la salida y poder defender qué harías en una revisión técnica, una asignatura o un piloto real.

## Variantes para hacerlo tuyo

- Ejecuta `make run` sin tocar nada y usa `output/evaluation_slice_decision.md` como línea base.
- Cambia o añade un caso en `data/model_predictions.csv` y `data/support_split_cases.csv` para representar un problema de tu trabajo, clase o producto.
- Endurece una regla, umbral o campo obligatorio en `contracts/evaluation_use_policy.md` y `contracts/preprocessing_policy.json` y explica por qué el resultado debería cambiar o bloquearse.
- Compara antes/después en `output/evaluation_slice_decision.md` y `output/preprocessing_fit_decision.md` y escribe una decisión de una página: seguir, bloquear, medir más o cambiar el diseño.
- Completa `templates/entrega.md` con contexto, cambio, evidencia, decisión y límite; no la dejes como checklist vacía.

## Rúbrica rápida

| Nivel | Qué demuestra |
|---|---|
| Mínimo | Ejecuta `make run` y `make test`, localiza `ops/evaluate_test_slices.py`, abre `output/evaluation_slice_decision.md` y explica qué decisión o señal produce. |
| Bueno | Cambia `data/model_predictions.csv`, compara antes/después y justifica la diferencia con una evidencia concreta del output. |
| Excelente | Convierte el kit en un mini caso profesional: añade un caso propio, ajusta una regla o test, documenta el límite principal y deja una recomendación accionable para un equipo. |

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `Kit F8 C03: splits, muestreo y leakage`, no escondido en una ruta del repositorio.

### Qué contiene

- `README.md`: esta guía y la explicación del ejercicio.
- `Makefile`: entrada única para ejecutar y validar el kit con `make run` y `make test`.
- `requirements.txt`: dependencias declaradas; muchos kits solo usan la biblioteca estándar de Python.
- `data/`: datos de entrada o casos de prueba realistas. Ejemplos dentro del ZIP: `data/model_predictions.csv`, `data/support_split_cases.csv`.
- `contracts/`: contratos de datos, salida, política o validación. Ejemplos dentro del ZIP: `contracts/evaluation_use_policy.md`, `contracts/preprocessing_policy.json`, `contracts/rag_llm_eval_policy.json`, `contracts/split_policy.json`.
- `templates/`: plantillas editables para la entrega. Ejemplos dentro del ZIP: `templates/entrega.md`.
- `ops/`: código ejecutable del laboratorio. Ejemplos dentro del ZIP: `ops/evaluate_test_slices.py`, `ops/preprocessing_fit_audit.py`, `ops/split_audit.py`.
- `tests/`: tests que comprueban que el ejercicio sigue siendo reproducible. Ejemplos dentro del ZIP: `tests/test_lab_contract.py`.
- `output/`: salidas generadas o esperadas que debes revisar. Ejemplos dentro del ZIP: `output/evaluation_slice_decision.md`, `output/preprocessing_fit_decision.md`, `output/split_decision.md`, `output/evaluation_slice_report.json`, ....

### Ejecutar desde cero

Desde la carpeta extraída del ZIP:

```bash
make run
make test
```

`make run` construye las evidencias del ejercicio. `make test` comprueba que el kit sigue siendo ejecutable después de descargarlo, extraerlo y tocarlo.

### Qué mirar antes de entregar

- `output/evaluation_slice_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/preprocessing_fit_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/split_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/evaluation_slice_report.json`: evidencia estructurada para validar o automatizar.
- `output/preprocessing_fit_report.json`: evidencia estructurada para validar o automatizar.
- `output/split_manifest.json`: evidencia estructurada para validar o automatizar.
- `output/split_report.json`: evidencia estructurada para validar o automatizar.
- `output/leakage_findings.csv`: tabla que puedes inspeccionar o cargar en un notebook.
- `output/split_assignments.csv`: tabla que puedes inspeccionar o cargar en un notebook.
- `output/strategy_comparison.csv`: tabla que puedes inspeccionar o cargar en un notebook.

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
