# Kit F10 C07: serving de políticas, drift y rollback

Este kit acompaña el capítulo 07 del facsímil 10. Audita si una política candidata puede avanzar en un rollout controlado.

La práctica junta cuatro piezas: ventana de referencia, ventana actual, plan de rollout y contrato operativo. El objetivo no es tener un dashboard bonito, sino decidir si una política vive, se queda en shadow o vuelve a la política de reserva.

## Ejecutar

```bash
python3 ops/audit_policy_serving.py --write
cat output/serving_decision.md
cat output/serving_runbook.md
head -n 8 output/drift_scorecard.csv
cat output/rollout_scorecard.csv
```

Salida esperada:

```text
status=pass
blocked_slices=0
blocked_rollout_stages=0
```

Escenario que debe bloquear:

```bash
python3 ops/audit_policy_serving.py \
  --current data/current_window_bad.json \
  --plan data/release_plan_bad.json \
  --output output_bad \
  --write
cat output_bad/serving_decision.md
cat output_bad/serving_runbook.md
```

Salida esperada:

```text
status=block
```

## Archivos

| Archivo | Papel |
|---|---|
| `contracts/policy_serving_contract.json` | SLOs, campos de traza y outputs obligatorios. |
| `data/reference_window.json` | Ventana estable contra la que se compara. |
| `data/current_window_ok.json` | Ventana actual que puede avanzar. |
| `data/current_window_bad.json` | Ventana actual con drift, latencia y calidad insuficiente. |
| `data/release_plan.json` | Rollout con shadow, pilotos, política de reserva y rollback. |
| `data/release_plan_bad.json` | Rollout roto: sin shadow, rollback débil y trazas incompletas. |
| `ops/audit_policy_serving.py` | Auditor reproducible sin dependencias externas. |
| `output/serving_audit_report.json` | Reporte completo. |
| `output/serving_decision.md` | Decisión técnica. |
| `output/drift_scorecard.csv` | Estado por slice. |
| `output/rollout_scorecard.csv` | Estado por etapa de rollout. |
| `output/serving_runbook.md` | Runbook de operación y rollback. |

## Qué debería mirar el alumno

1. Si cada slice cumple reward, evidencia, latencia, errores de herramienta y fallback.
2. Si el PSI de población y de acciones sigue por debajo del límite.
3. Si el plan incluye `shadow`, `pilot_5` y `pilot_25`.
4. Si la política de reserva está declarada.
5. Si el rollback está listo y tiene condiciones concretas.
6. Si la traza de ejemplo contiene política estable, política candidata, reward card y probabilidad de acción.
7. Si el runbook dice qué hacer antes de aumentar tráfico y qué hacer si el gate bloquea.

## Adaptarlo a tu proyecto

Cambia primero los SLOs del contrato: `max_p95_latency_ms`, `min_reward_mean`, `max_fallback_rate` y `max_population_stability_index`. Después ajusta los slices para que representen tu producto: `rag`, `sql`, `herramientas`, `privacidad` son ejemplos, no categorías universales.

El entregable profesional sería un PR con:

- contrato actualizado,
- ventana de referencia,
- ventana actual,
- plan de rollout,
- decisión generada,
- runbook generado,
- explicación de los slices bloqueados o de por qué se permite avanzar.

## Qué te llevas

Te llevas una práctica ejecutable sobre serving de políticas, drift y rollback, con datos editables, contratos y umbrales, plantillas de entrega, código ejecutable y tests reproducibles. Trabajas con `data/current_window_bad.json` y `data/current_window_ok.json`, contrastas la decisión contra `contracts/policy_serving_contract.json` y ejecutas `ops/audit_policy_serving.py` para generar `output/serving_decision.md`. La idea no es mirar una solución cerrada: es cambiar una entrada, volver a ejecutar, comparar la salida y poder defender qué harías en una revisión técnica, una asignatura o un piloto real.

## Variantes para hacerlo tuyo

- Ejecuta `make run` sin tocar nada y usa `output/serving_decision.md` como línea base.
- Cambia o añade un caso en `data/current_window_bad.json` y `data/current_window_ok.json` para representar un problema de tu trabajo, clase o producto.
- Endurece una regla, umbral o campo obligatorio en `contracts/policy_serving_contract.json` y explica por qué el resultado debería cambiar o bloquearse.
- Compara el caso que pasa con el caso roto o arriesgado y escribe qué señal lo bloquea.
- Compara antes/después en `output/serving_decision.md` y `output/serving_runbook.md` y escribe una decisión de una página: seguir, bloquear, medir más o cambiar el diseño.
- Completa `templates/entrega.md` con contexto, cambio, evidencia, decisión y límite; no la dejes como checklist vacía.

## Rúbrica rápida

| Nivel | Qué demuestra |
|---|---|
| Mínimo | Ejecuta `make run` y `make test`, localiza `ops/audit_policy_serving.py`, abre `output/serving_decision.md` y explica qué decisión o señal produce. |
| Bueno | Cambia `data/current_window_bad.json`, compara antes/después y justifica la diferencia con una evidencia concreta del output. |
| Excelente | Convierte el kit en un mini caso profesional: añade un caso propio, ajusta una regla o test, documenta el límite principal y deja una recomendación accionable para un equipo. |

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `Kit F10 C07: serving de políticas, drift y rollback`, no escondido en una ruta del repositorio.

### Qué contiene

- `README.md`: esta guía y la explicación del ejercicio.
- `Makefile`: entrada única para ejecutar y validar el kit con `make run` y `make test`.
- `requirements.txt`: dependencias declaradas; muchos kits solo usan la biblioteca estándar de Python.
- `data/`: datos de entrada o casos de prueba realistas. Ejemplos dentro del ZIP: `data/current_window_bad.json`, `data/current_window_ok.json`, `data/reference_window.json`, `data/release_plan.json`, ....
- `contracts/`: contratos de datos, salida, política o validación. Ejemplos dentro del ZIP: `contracts/policy_serving_contract.json`.
- `templates/`: plantillas editables para la entrega. Ejemplos dentro del ZIP: `templates/entrega.md`.
- `ops/`: código ejecutable del laboratorio. Ejemplos dentro del ZIP: `ops/audit_policy_serving.py`.
- `tests/`: tests que comprueban que el ejercicio sigue siendo reproducible. Ejemplos dentro del ZIP: `tests/test_lab_contract.py`.
- `output/`: salidas generadas o esperadas que debes revisar. Ejemplos dentro del ZIP: `output/serving_decision.md`, `output/serving_runbook.md`, `output/serving_audit_report.json`, `output/drift_scorecard.csv`, ....
- `output_bad/`: salidas de fallo para aprender qué debe bloquearse. Ejemplos dentro del ZIP: `output_bad/serving_decision.md`, `output_bad/serving_runbook.md`, `output_bad/serving_audit_report.json`, `output_bad/drift_scorecard.csv`, ....

### Ejecutar desde cero

Desde la carpeta extraída del ZIP:

```bash
make run
make test
```

`make run` construye las evidencias del ejercicio. `make test` comprueba que el kit sigue siendo ejecutable después de descargarlo, extraerlo y tocarlo.

### Qué mirar antes de entregar

- `output/serving_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/serving_runbook.md`: lectura humana de la decisión, informe o runbook.
- `output_bad/serving_decision.md`: lectura humana de la decisión, informe o runbook.
- `output_bad/serving_runbook.md`: lectura humana de la decisión, informe o runbook.
- `output/serving_audit_report.json`: evidencia estructurada para validar o automatizar.
- `output_bad/serving_audit_report.json`: evidencia estructurada para validar o automatizar.
- `output/drift_scorecard.csv`: tabla que puedes inspeccionar o cargar en un notebook.
- `output/rollout_scorecard.csv`: tabla que puedes inspeccionar o cargar en un notebook.
- `output_bad/drift_scorecard.csv`: tabla que puedes inspeccionar o cargar en un notebook.
- `output_bad/rollout_scorecard.csv`: tabla que puedes inspeccionar o cargar en un notebook.

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
