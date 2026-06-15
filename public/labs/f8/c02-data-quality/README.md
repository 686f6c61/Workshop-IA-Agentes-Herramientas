# Kit F8 C02: calidad de datos, leakage y etiquetas

Este kit acompaña el capítulo 02 del facsímil 8. Trabaja con un dataset sintético de soporte académico que incluye problemas deliberados: columnas incompletas, valores fuera de contrato, duplicados, leakage entre splits y etiquetas que conviene revisar.

El objetivo no es limpiar por intuicion. El objetivo es convertir calidad de datos en una decisión reproducible: que se bloquea, que se revisa y que evidencia queda para el equipo.

## Ejecutar

Desde está carpeta:

```bash
python3 ops/data_quality_gate.py --write
python3 ops/ci_assert_gate.py
cat output/clean_actions.md
```

## Archivos

| Archivo | Papel |
|---|---|
| `data/quality_cases_dirty.csv` | Dataset sintético con problemas intencionados. |
| `contracts/quality_contract.json` | Reglas de schema, catalogos, splits, etiquetas y umbrales. |
| `contracts/quality_slos.json` | SLI/SLO de calidad y política de presupuesto de error. |
| `contracts/annotation_policy.md` | Politica de anotación con etiquetas, casos frontera y desempate. |
| `ops/data_quality_gate.py` | Gate sin dependencias externas. |
| `ops/ci_assert_gate.py` | Script para fallar en CI si el gate queda en `block`. |
| `output/quality_report.json` | Reporte completo de checks, métricas y resultado. |
| `output/release_gate.json` | Resumen para CI o revisión técnica. |
| `output/duplicate_candidates.csv` | Pares exactos o cercanos que cruzan splits. |
| `output/label_review_queue.csv` | Casos candidatos a revisión de etiqueta. |
| `output/clean_actions.md` | Plan de limpieza priorizado. |

## Qué deberías mirar

1. `gate`: si el dataset queda en `pass`, `review` o `block`.
2. `blocking_failures`: fallos que impiden usar el dataset.
3. `label_review_queue.csv`: casos que no se deberían borrar a ciegas.
4. `duplicate_candidates.csv`: duplicados exactos o cercanos entre splits.
5. `kappa`: acuerdo entre dos anotadores.
6. `stratification_drift`: diferencia de distribución de etiquetas entre splits.
7. `contracts/annotation_policy.md`: si la cola de revisión apunta a una política incompleta.
8. `contracts/quality_slos.json`: que indicadores se convierten en objetivos.

## Qué entregaría un alumno

1. Reporte JSON generado.
2. Cola de revisión de etiquetas.
3. Lista de duplicados candidatos.
4. Plan de limpieza con decisiones justificadas.
5. Una propuesta de nuevo contrato para un dataset propio.
6. Una propuesta de SLI/SLO de calidad para ese dataset.

## Qué te llevas

Te llevas una práctica ejecutable sobre calidad de datos, leakage y etiquetas, con datos editables, contratos y umbrales, plantillas de entrega, código ejecutable y tests reproducibles. Trabajas con `data/quality_cases_dirty.csv`, contrastas la decisión contra `contracts/annotation_policy.md` y `contracts/quality_contract.json` y ejecutas `ops/ci_assert_gate.py` para generar `output/clean_actions.md`. La idea no es mirar una solución cerrada: es cambiar una entrada, volver a ejecutar, comparar la salida y poder defender qué harías en una revisión técnica, una asignatura o un piloto real.

## Variantes para hacerlo tuyo

- Ejecuta `make run` sin tocar nada y usa `output/clean_actions.md` como línea base.
- Cambia o añade un caso en `data/quality_cases_dirty.csv` para representar un problema de tu trabajo, clase o producto.
- Endurece una regla, umbral o campo obligatorio en `contracts/annotation_policy.md` y `contracts/quality_contract.json` y explica por qué el resultado debería cambiar o bloquearse.
- Compara antes/después en `output/clean_actions.md` y `output/quality_report.json` y escribe una decisión de una página: seguir, bloquear, medir más o cambiar el diseño.
- Completa `templates/entrega.md` con contexto, cambio, evidencia, decisión y límite; no la dejes como checklist vacía.

## Rúbrica rápida

| Nivel | Qué demuestra |
|---|---|
| Mínimo | Ejecuta `make run` y `make test`, localiza `ops/ci_assert_gate.py`, abre `output/clean_actions.md` y explica qué decisión o señal produce. |
| Bueno | Cambia `data/quality_cases_dirty.csv`, compara antes/después y justifica la diferencia con una evidencia concreta del output. |
| Excelente | Convierte el kit en un mini caso profesional: añade un caso propio, ajusta una regla o test, documenta el límite principal y deja una recomendación accionable para un equipo. |

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `Kit F8 C02: calidad de datos, leakage y etiquetas`, no escondido en una ruta del repositorio.

### Qué contiene

- `README.md`: esta guía y la explicación del ejercicio.
- `Makefile`: entrada única para ejecutar y validar el kit con `make run` y `make test`.
- `requirements.txt`: dependencias declaradas; muchos kits solo usan la biblioteca estándar de Python.
- `data/`: datos de entrada o casos de prueba realistas. Ejemplos dentro del ZIP: `data/quality_cases_dirty.csv`.
- `contracts/`: contratos de datos, salida, política o validación. Ejemplos dentro del ZIP: `contracts/annotation_policy.md`, `contracts/quality_contract.json`, `contracts/quality_slos.json`.
- `templates/`: plantillas editables para la entrega. Ejemplos dentro del ZIP: `templates/entrega.md`.
- `ops/`: código ejecutable del laboratorio. Ejemplos dentro del ZIP: `ops/ci_assert_gate.py`, `ops/data_quality_gate.py`.
- `tests/`: tests que comprueban que el ejercicio sigue siendo reproducible. Ejemplos dentro del ZIP: `tests/test_lab_contract.py`.
- `output/`: salidas generadas o esperadas que debes revisar. Ejemplos dentro del ZIP: `output/clean_actions.md`, `output/quality_report.json`, `output/release_gate.json`, `output/duplicate_candidates.csv`, ....

### Ejecutar desde cero

Desde la carpeta extraída del ZIP:

```bash
make run
make test
```

`make run` construye las evidencias del ejercicio. `make test` comprueba que el kit sigue siendo ejecutable después de descargarlo, extraerlo y tocarlo.

### Qué mirar antes de entregar

- `output/clean_actions.md`: lectura humana de la decisión, informe o runbook.
- `output/quality_report.json`: evidencia estructurada para validar o automatizar.
- `output/release_gate.json`: evidencia estructurada para validar o automatizar.
- `output/duplicate_candidates.csv`: tabla que puedes inspeccionar o cargar en un notebook.
- `output/label_review_queue.csv`: tabla que puedes inspeccionar o cargar en un notebook.

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
