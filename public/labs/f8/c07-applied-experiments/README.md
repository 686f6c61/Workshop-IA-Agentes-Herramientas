# Kit F8 C07: experimentos, causalidad y decisión

Este kit acompaña el capítulo 07 del facsímil 8. Tiene cinco piezas:

1. Un A/B test pequeño para medir una intervención con contrato, SRM, balance, ATE, CUPED, guardrails y slices.
2. Una muestra observacional para ver por qué una asociación aparente no basta cuando hay contexto que influye en acción y resultado.
3. Un plan de análisis y un catálogo de métricas para validar el diseño antes de mirar resultados.
4. Una simulación de plataforma experimental con feature flag, exposición, RAG y métricas tardías.
5. Un ejemplo de interferencia por equipo para decidir si la unidad individual basta o hay que asignar por cluster.

## Ejecutar

Desde esta carpeta:

```bash
python3 ops/analyze_ab_experiment.py --write
cat output/experiment_decision.md
cat output/experiment_readiness.md
python3 -m json.tool output/experiment_report.json
```

Para simular asignación por feature flag y generar eventos de exposición:

```bash
python3 ops/validate_experiment_design.py --write
cat output/experiment_design_validation.md
python3 ops/simulate_feature_flag_assignment.py --write
cat output/flag_assignment_decision.md
```

Para un experimento RAG:

```bash
python3 ops/analyze_rag_experiment.py --write
cat output/rag_experiment_decision.md
```

Para ver métricas que maduran tarde:

```bash
python3 ops/summarize_metric_maturation.py --write
cat output/metric_maturation_decision.md
```

Para simular un gate de CI:

```bash
python3 ops/validate_experiment_design.py --write
python3 ops/ci_experiment_gate.py --write
cat output/ci_gate_decision.md
```

Para detectar interferencia por equipo, cola u operador:

```bash
python3 ops/analyze_cluster_interference.py --write
cat output/cluster_interference_decision.md
```

Para la lectura observacional:

```bash
python3 ops/audit_observational_effect.py --write
cat output/observational_decision.md
python3 -m json.tool output/observational_causal_report.json
```

## Archivos

| Archivo | Papel |
|---|---|
| `data/experiment_events.csv` | Eventos de un experimento controlado. |
| `data/observational_campaign.csv` | Muestra no aleatorizada para detectar confusión por contexto. |
| `data/rag_experiment_events.csv` | Experimento RAG con calidad, citas, latencia y coste. |
| `data/late_metric_events.csv` | Métricas medidas en ventanas `day_1` y `day_7`. |
| `data/cluster_interference_events.csv` | Ejemplo de mezcla entre control y treatment dentro del mismo equipo. |
| `contracts/experiment_contract.json` | Unidad, asignación esperada, columnas, métrica primaria, guardrails y gates. |
| `contracts/analysis_plan.json` | Hipótesis, población, métrica primaria, guardrails, ventanas y reglas de decisión. |
| `contracts/metric_catalog.json` | Catálogo de métricas primarias, guardrails y diagnósticas. |
| `contracts/causal_question.md` | Pregunta causal, intervención, resultado y supuestos. |
| `contracts/feature_flag_contract.json` | Flag, targeting key, contexto y campos de exposición. |
| `contracts/warehouse_schema.sql` | Schema mínimo para unidades, exposiciones, métricas y decisiones. |
| `contracts/ci_gate_policy.json` | Política para bloquear o dejar en revisión un experimento. |
| `ops/analyze_ab_experiment.py` | Audita experimento y genera decisión. |
| `ops/audit_observational_effect.py` | Compara efecto ingenuo y efecto estratificado. |
| `ops/validate_experiment_design.py` | Valida plan, catálogo de métricas y contrato de flag. |
| `ops/simulate_feature_flag_assignment.py` | Simula asignación por flag y genera exposiciones. |
| `ops/analyze_rag_experiment.py` | Analiza un experimento RAG con guardrails técnicos. |
| `ops/summarize_metric_maturation.py` | Muestra como cambian métricas segun ventana. |
| `ops/analyze_cluster_interference.py` | Detecta clusters mezclados con posible interferencia. |
| `ops/ci_experiment_gate.py` | Gate reproducible para CI. |
| `output/experiment_report.json` | Reporte completo del A/B test. |
| `output/experiment_scorecard.csv` | Tabla por variante. |
| `output/balance_report.csv` | Balance de covariables pretratamiento. |
| `output/slice_effects.csv` | Efectos por segmento. |
| `output/experiment_decision.md` | Decisión operativa del experimento. |
| `output/experiment_readiness.md` | MDE, potencia, A/A, exposure event, peeking y rollout. |
| `output/experiment_design_validation.json` | Validación del plan de análisis antes de medir. |
| `output/experiment_design_validation.md` | Lectura humana de la validación del diseño. |
| `output/exposure_events.csv` | Eventos de exposición generados por la simulación de flag. |
| `output/flag_assignment_manifest.json` | Resumen de reparto y discrepancias de asignación. |
| `output/rag_experiment_report.json` | Reporte del experimento RAG. |
| `output/metric_maturation_report.json` | Reporte de métricas por ventana de maduración. |
| `output/cluster_interference_report.json` | Reporte de mezcla de variantes dentro de clusters. |
| `output/cluster_interference_summary.csv` | Tabla por cluster para revisar mezcla y resultado. |
| `output/cluster_interference_decision.md` | Lectura humana sobre si conviene asignar por cluster. |
| `output/ci_gate_report.json` | Resultado del gate de CI. |
| `output/observational_causal_report.json` | Reporte de lectura observacional. |
| `output/observational_strata.csv` | Comparación por estratos. |
| `output/observational_decision.md` | Decisión sobre si la muestra permite concluir. |

## Qué deberías mirar

1. El experimento queda en `review`, no porque sea malo, sino porque el efecto es prometedor y aún impreciso.
2. La asignación 50/50 pasa el control de SRM.
3. Los guardrails no bloquean: latencia, coste y feedback negativo quedan dentro de contrato.
4. Los slices muestran que el efecto no se reparte igual por segmento.
5. La muestra observacional parece mucho más optimista si miras solo la diferencia ingenua.
6. Al estratificar por prioridad aparece falta de solapamiento: hay contextos donde no puedes comparar bien.
7. `experiment_readiness.md` explica por qué el experimento sirve para aprender, pero no para publicar globalmente con MDE 0.05.
8. El contrato exige `experiment_exposure`, asignación persistente, política de peeking y rollout progresivo.
9. `experiment_design_validation.md` comprueba que existe una métrica primaria, guardrails, plan y contexto de flag.
10. `cluster_interference_decision.md` muestra por qué una asignación por unidad puede ser pobre si el equipo comparte aprendizaje.

## Cómo llevarlo a un sistema real

1. Implementa la variante detrás de una feature flag.
2. Usa una unidad estable como `user_id`, `ticket_id` o `account_id`.
3. Registra asignación y exposición como eventos separados.
4. Versiona prompt, modelo, parámetros y política de decisión como parte del tratamiento.
5. Define una métrica primaria y guardrails antes de iniciar.
6. Calcula MDE, alpha, potencia y muestra esperada antes de mirar resultados.
7. Ejecuta A/A si la instrumentación es nueva.
8. Publica con ramp progresivo y rollback si un guardrail bloquea.
9. Define si hay clusters naturales: equipo, empresa, cola, operador o aula.
10. Deja un plan de análisis versionado antes de mirar resultados.

## Qué te llevas

Te llevas una práctica ejecutable sobre experimentos, causalidad y decisión, con datos editables, contratos y umbrales, plantillas de entrega, código ejecutable y tests reproducibles. Trabajas con `data/cluster_interference_events.csv` y `data/experiment_events.csv`, contrastas la decisión contra `contracts/causal_question.md` y `contracts/analysis_plan.json` y ejecutas `ops/analyze_ab_experiment.py` para generar `output/ci_gate_decision.md`. La idea no es mirar una solución cerrada: es cambiar una entrada, volver a ejecutar, comparar la salida y poder defender qué harías en una revisión técnica, una asignatura o un piloto real.

## Qué entregaría un alumno

1. `experiment_decision.md` generado e interpretado.
2. Un cambio razonado en `experiment_contract.json`.
3. Una nueva métrica guardrail para su proyecto.
4. Una lectura de `slice_effects.csv` indicando donde el efecto parece concentrarse.
5. Una explicación de por qué `observational_campaign.csv` no permite cerrar una conclusión causal final.
6. Un diseño de próximo experimento: unidad, tratamiento, métrica primaria, guardrails y criterio de parada.
7. Un readiness escrito: A/A, exposure event, MDE, potencia, peeking y rollout.
8. Un plan de análisis validado con `validate_experiment_design.py`.
9. Una decisión sobre unidad individual o asignación por cluster.

## Variantes para hacerlo tuyo

- Ejecuta `make run` sin tocar nada y usa `output/ci_gate_decision.md` como línea base.
- Cambia o añade un caso en `data/cluster_interference_events.csv` y `data/experiment_events.csv` para representar un problema de tu trabajo, clase o producto.
- Endurece una regla, umbral o campo obligatorio en `contracts/causal_question.md` y `contracts/analysis_plan.json` y explica por qué el resultado debería cambiar o bloquearse.
- Compara antes/después en `output/ci_gate_decision.md` y `output/cluster_interference_decision.md` y escribe una decisión de una página: seguir, bloquear, medir más o cambiar el diseño.
- Completa `templates/entrega.md` con contexto, cambio, evidencia, decisión y límite; no la dejes como checklist vacía.

## Rúbrica rápida

| Nivel | Qué demuestra |
|---|---|
| Mínimo | Ejecuta `make run` y `make test`, localiza `ops/analyze_ab_experiment.py`, abre `output/ci_gate_decision.md` y explica qué decisión o señal produce. |
| Bueno | Cambia `data/cluster_interference_events.csv`, compara antes/después y justifica la diferencia con una evidencia concreta del output. |
| Excelente | Convierte el kit en un mini caso profesional: añade un caso propio, ajusta una regla o test, documenta el límite principal y deja una recomendación accionable para un equipo. |

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `Kit F8 C07: experimentos, causalidad y decisión`, no escondido en una ruta del repositorio.

### Qué contiene

- `README.md`: esta guía y la explicación del ejercicio.
- `Makefile`: entrada única para ejecutar y validar el kit con `make run` y `make test`.
- `requirements.txt`: dependencias declaradas; muchos kits solo usan la biblioteca estándar de Python.
- `data/`: datos de entrada o casos de prueba realistas. Ejemplos dentro del ZIP: `data/cluster_interference_events.csv`, `data/experiment_events.csv`, `data/late_metric_events.csv`, `data/observational_campaign.csv`, ....
- `contracts/`: contratos de datos, salida, política o validación. Ejemplos dentro del ZIP: `contracts/causal_question.md`, `contracts/analysis_plan.json`, `contracts/ci_gate_policy.json`, `contracts/experiment_contract.json`, ....
- `templates/`: plantillas editables para la entrega. Ejemplos dentro del ZIP: `templates/entrega.md`.
- `ops/`: código ejecutable del laboratorio. Ejemplos dentro del ZIP: `ops/analyze_ab_experiment.py`, `ops/analyze_cluster_interference.py`, `ops/analyze_rag_experiment.py`, `ops/audit_observational_effect.py`, ....
- `tests/`: tests que comprueban que el ejercicio sigue siendo reproducible. Ejemplos dentro del ZIP: `tests/test_lab_contract.py`.
- `output/`: salidas generadas o esperadas que debes revisar. Ejemplos dentro del ZIP: `output/ci_gate_decision.md`, `output/cluster_interference_decision.md`, `output/experiment_decision.md`, `output/experiment_design_validation.md`, ....

### Ejecutar desde cero

Desde la carpeta extraída del ZIP:

```bash
make run
make test
```

`make run` construye las evidencias del ejercicio. `make test` comprueba que el kit sigue siendo ejecutable después de descargarlo, extraerlo y tocarlo.

### Qué mirar antes de entregar

- `output/ci_gate_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/cluster_interference_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/experiment_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/experiment_design_validation.md`: lectura humana de la decisión, informe o runbook.
- `output/experiment_readiness.md`: lectura humana de la decisión, informe o runbook.
- `output/flag_assignment_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/metric_maturation_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/observational_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/rag_experiment_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/ci_gate_report.json`: evidencia estructurada para validar o automatizar.
- `output/cluster_interference_report.json`: evidencia estructurada para validar o automatizar.
- `output/experiment_design_validation.json`: evidencia estructurada para validar o automatizar.

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
