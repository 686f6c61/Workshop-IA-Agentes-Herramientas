# Kit F7 C05: calibración e incertidumbre

Este kit acompaña al capítulo 05 del facsímil 7. La práctica no intenta simular todo un sistema de soporte real; intenta dejar un artefacto pequeño que un alumno pueda ejecutar, leer, modificar y defender.

## Qué construyes

Archivos principales:

| Archivo | Papel |
|---|---|
| `evals/calibration_cases.csv` | Casos revisados con split, score bruto, etiqueta, slice, canal y semana. |
| `policies/calibration_policy.json` | Contrato operativo: costes, umbrales máximos, versiones y triggers. |
| `ops/ai/calibrate_policy.py` | Script ejecutable sin dependencias externas. |
| `output/calibration_report.json` | Métricas, reliability tables, intervalos, riesgo-cobertura y política recomendada. |
| `output/calibration_manifest.json` | Manifest versionado para revisar la política en producción. |
| `output/calibration_decision.md` | Decisión técnica lista para revisar con el equipo. |

## Cómo lo ejecutas

Desde esta carpeta:

```bash
python3 ops/ai/calibrate_policy.py --write
cat output/calibration_decision.md
```

También puedes pasar rutas explícitas:

```bash
python3 ops/ai/calibrate_policy.py \
  --cases evals/calibration_cases.csv \
  --policy policies/calibration_policy.json \
  --write
```

## Qué deberías mirar

1. `raw_metrics` frente a `calibrated_metrics`.
2. `reliability`: cada banda tiene confianza media, accuracy real e intervalo Wilson.
3. `bootstrap`: rango aproximado de Brier y ECE por remuestreo.
4. `slice_report`: si una media global esconde slices poco fiables.
5. `risk_coverage_curve`: qué error queda al automatizar más o menos.
6. `operational_checks`: si la política pasa los criterios mínimos.
7. `calibration_manifest.json`: versiones, hashes, slices y triggers.

## Cómo lo adaptas a un proyecto propio

Cambia primero `evals/calibration_cases.csv`. Manteniendo las columnas obligatorias, puedes añadir más columnas sin romper el script.

Columnas obligatorias:

| Columna | Significado |
|---|---|
| `case_id` | Identificador estable del caso. |
| `split` | `calibration` o `evaluation`. |
| `raw_score` | Score bruto que quieres calibrar. |
| `label` | Resultado real: 1 para positivo, 0 para negativo. |
| `slice` | Segmento operativo que quieres vigilar. |

Después ajusta `policies/calibration_policy.json`: costes, bins, cobertura objetivo, límites de revisión y slices válidos.

## Qué entregaría un alumno

Un entregable defendible tendría:

1. El CSV de casos revisados.
2. La política JSON.
3. El reporte JSON generado.
4. El manifest.
5. Una decisión Markdown que diga si publicaría, limitaría o pediría más datos.
6. Dos cambios propuestos: uno de datos y otro de política.

La parte importante no es acertar el umbral perfecto. Es poder explicar por qué ese umbral existe, qué coste acepta, en qué datos se apoya y cuándo caduca.

## Qué te llevas

Te llevas una práctica ejecutable sobre calibración e incertidumbre, con sets de evaluación y rúbricas, políticas de decisión, plantillas de entrega, código ejecutable y tests reproducibles. Trabajas con `evals/calibration_cases.csv`, contrastas la decisión contra `policies/calibration_policy.json` y ejecutas `ops/ai/calibrate_policy.py` para generar `output/calibration_decision.md`. La idea no es mirar una solución cerrada: es cambiar una entrada, volver a ejecutar, comparar la salida y poder defender qué harías en una revisión técnica, una asignatura o un piloto real.

## Variantes para hacerlo tuyo

- Ejecuta `make run` sin tocar nada y usa `output/calibration_decision.md` como línea base.
- Cambia o añade un caso en `evals/calibration_cases.csv` para representar un problema de tu trabajo, clase o producto.
- Endurece una regla, umbral o campo obligatorio en `policies/calibration_policy.json` y explica por qué el resultado debería cambiar o bloquearse.
- Compara antes/después en `output/calibration_decision.md` y `output/calibration_manifest.json` y escribe una decisión de una página: seguir, bloquear, medir más o cambiar el diseño.
- Completa `templates/entrega.md` con contexto, cambio, evidencia, decisión y límite; no la dejes como checklist vacía.

## Rúbrica rápida

| Nivel | Qué demuestra |
|---|---|
| Mínimo | Ejecuta `make run` y `make test`, localiza `ops/ai/calibrate_policy.py`, abre `output/calibration_decision.md` y explica qué decisión o señal produce. |
| Bueno | Cambia `evals/calibration_cases.csv`, compara antes/después y justifica la diferencia con una evidencia concreta del output. |
| Excelente | Convierte el kit en un mini caso profesional: añade un caso propio, ajusta una regla o test, documenta el límite principal y deja una recomendación accionable para un equipo. |

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `Kit F7 C05: calibración e incertidumbre`, no escondido en una ruta del repositorio.

### Qué contiene

- `README.md`: esta guía y la explicación del ejercicio.
- `Makefile`: entrada única para ejecutar y validar el kit con `make run` y `make test`.
- `requirements.txt`: dependencias declaradas; muchos kits solo usan la biblioteca estándar de Python.
- `policies/`: umbrales, reglas de decisión o políticas operativas. Ejemplos dentro del ZIP: `policies/calibration_policy.json`.
- `templates/`: plantillas editables para la entrega. Ejemplos dentro del ZIP: `templates/entrega.md`.
- `evals/`: datasets, rúbricas o configuraciones de evaluación. Ejemplos dentro del ZIP: `evals/calibration_cases.csv`.
- `ops/`: código ejecutable del laboratorio. Ejemplos dentro del ZIP: `ops/ai/calibrate_policy.py`.
- `tests/`: tests que comprueban que el ejercicio sigue siendo reproducible. Ejemplos dentro del ZIP: `tests/test_lab_contract.py`.
- `output/`: salidas generadas o esperadas que debes revisar. Ejemplos dentro del ZIP: `output/calibration_decision.md`, `output/calibration_manifest.json`, `output/calibration_report.json`.

### Ejecutar desde cero

Desde la carpeta extraída del ZIP:

```bash
make run
make test
```

`make run` construye las evidencias del ejercicio. `make test` comprueba que el kit sigue siendo ejecutable después de descargarlo, extraerlo y tocarlo.

### Qué mirar antes de entregar

- `output/calibration_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/calibration_manifest.json`: evidencia estructurada para validar o automatizar.
- `output/calibration_report.json`: evidencia estructurada para validar o automatizar.

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
3. Revisa `policies/` para adaptar límites de riesgo, criterios de bloqueo o reglas de negocio.
4. Usa `templates/` como base documental; no entregues una plantilla sin completar.
5. Guarda los outputs finales y una nota breve con la decisión técnica que tomarías en un proyecto real.

### Criterio de validación

El kit está completo cuando se puede descargar, extraer, ejecutar con `make run`, validar con `make test` y explicar sin depender de ninguna carpeta externa. Si una práctica menciona código, datos, contrato, CSV, SQL, política o plantilla, ese contenido debe venir dentro del ZIP.
<!-- zip-quality-audit:end -->
