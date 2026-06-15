# Kit F7 C06: interpretabilidad práctica y laboratorio

Este kit acompaña al capítulo 06 del facsímil 7. Construye un informe reproducible de interpretabilidad para un modelo lineal pequeño de priorización de tickets.

El objetivo no es fingir que un modelo lineal representa todos los sistemas de IA. El objetivo es que el alumno vea, con números, que una explicación debe poder probarse: contribuciones locales, importancia global, estabilidad, contrafactuales accionables, contrato de explicación, gate de CI y decisión técnica.

## Ejecutar

Desde esta carpeta:

```bash
python3 ops/ai/interpretability_audit.py --write
cat output/interpretability_decision.md
cat output/model_card_interpretability.md
python3 -m json.tool output/explanation_contract.json
python3 -m json.tool output/ci_explanation_gate.json
```

La ejecución genera un expediente, no una única métrica. Lee los artefactos en este orden:

1. `interpretability_decision.md`: decisión ejecutiva y lectura de checks.
2. `interpretability_report.json`: evidencia completa caso a caso.
3. `explanation_contract.json`: quién puede consumir la explicación y para qué.
4. `ci_explanation_gate.json`: condiciones automatizables de release.
5. `model_card_interpretability.md`: fragmento que podría entrar en documentación de modelo.

## Archivos

| Archivo | Papel |
|---|---|
| `data/ticket_features.csv` | Dataset pequeño con features tabulares y etiqueta. |
| `policies/interpretability_policy.json` | Pesos del modelo, umbral, rangos y criterios de auditoría. |
| `ops/ai/interpretability_audit.py` | Script sin dependencias externas. |
| `output/interpretability_report.json` | Predicciones, explicaciónes, estabilidad, importancia y checks. |
| `output/explanation_contract.json` | Contrato de uso de explicaciónes: finalidad, consumidores, campos y hashes. |
| `output/ci_explanation_gate.json` | Gate automatizable para CI con checks y recomendación. |
| `output/model_card_interpretability.md` | Fragmento de model card centrado en explicabilidad. |
| `output/interpretability_decision.md` | Decisión técnica sobre si la explicación es defendible. |

## Qué deberías mirar

1. `local_explanations`: por qué un caso concreto supera o no el umbral.
2. `deletion_tests`: si quitar la feature más importante cambia la salida como esperabas.
3. `permutation_importance`: qué features importan globalmente.
4. `stability`: si pequeñas perturbaciones cambian demasiado la explicación.
5. `counterfactuals`: qué cambios accionables moverían la decisión.
6. `comprehensiveness_top2` y `sufficiency_top2`: si las features explicadas de verdad sostienen el score.
7. `feature_proxy_scan`: si dos features están demasiado correlacionadas y piden revisión.
8. `explanation_contract.json`: para qué se puede usar la explicación y para qué no.
9. `ci_explanation_gate.json`: si la explicación pasa requisitos mínimos.

## Cómo leer el resultado

No basta con decir "la explicación pasa". Una lectura profesional separa cuatro niveles:

| Nivel | Pregunta | Artefacto |
|---|---|---|
| Caso local | Qué explica `t001` y qué cambiaría la decisión. | `local_explanations`, `counterfactuals`. |
| Comportamiento global | De qué features depende el modelo. | `permutation_importance`, `top_feature_distribution`. |
| Robustez | La explicación resiste perturbaciones y pruebas de borrado. | `deletion_tests`, `stability`, `top_k_fidelity`. |
| Uso permitido | Quién puede usar la explicación y con qué límites. | `explanation_contract.json`, `ci_explanation_gate.json`. |

Si alguno de esos niveles falta, el resultado no está listo para una release seria.

## Qué entregaría un alumno

1. Reporte JSON generado.
2. Decisión Markdown.
3. Un caso explicado localmente.
4. Una feature global criticada con datos.
5. Un contrafactual accionable y uno rechazado por no ser accionable.
6. Un contrato de explicación revisado.
7. Una propuesta de gate de CI para una release.
8. Una mejora propuesta para datos, modelo o evaluación.

## Entrega esperada

La entrega buena cabe en una carpeta `release-interpretability-review/` con:

```text
release-interpretability-review/
  interpretability_decision.md
  interpretability_report.json
  explanation_contract.json
  ci_explanation_gate.json
  model_card_interpretability.md
  reviewer_notes.md
```

`reviewer_notes.md` debe responder en lenguaje técnico:

1. Qué decisión permite tomar la explicación.
2. Qué evidencia sostiene el caso local.
3. Qué feature domina globalmente y por qué importa.
4. Qué contrafactual es accionable.
5. Qué no se permite hacer con esta explicación.
6. Qué condición meterías en CI para no degradar explicabilidad en la siguiente release.

## Qué te llevas

Te llevas una práctica ejecutable sobre interpretabilidad práctica y laboratorio, con datos editables, políticas de decisión, plantillas de entrega, código ejecutable y tests reproducibles. Trabajas con `data/ticket_features.csv`, contrastas la decisión contra `policies/interpretability_policy.json` y ejecutas `ops/ai/calibrate_policy.py` para generar `output/decision.md`. La idea no es mirar una solución cerrada: es cambiar una entrada, volver a ejecutar, comparar la salida y poder defender qué harías en una revisión técnica, una asignatura o un piloto real.

## Variantes para hacerlo tuyo

- Ejecuta `make run` sin tocar nada y usa `output/decision.md` como línea base.
- Cambia o añade un caso en `data/ticket_features.csv` para representar un problema de tu trabajo, clase o producto.
- Endurece una regla, umbral o campo obligatorio en `policies/interpretability_policy.json` y explica por qué el resultado debería cambiar o bloquearse.
- Compara antes/después en `output/decision.md` y `output/interpretability_decision.md` y escribe una decisión de una página: seguir, bloquear, medir más o cambiar el diseño.
- Completa `templates/entrega.md` con contexto, cambio, evidencia, decisión y límite; no la dejes como checklist vacía.

## Rúbrica rápida

| Nivel | Qué demuestra |
|---|---|
| Mínimo | Ejecuta `make run` y `make test`, localiza `ops/ai/calibrate_policy.py`, abre `output/decision.md` y explica qué decisión o señal produce. |
| Bueno | Cambia `data/ticket_features.csv`, compara antes/después y justifica la diferencia con una evidencia concreta del output. |
| Excelente | Convierte el kit en un mini caso profesional: añade un caso propio, ajusta una regla o test, documenta el límite principal y deja una recomendación accionable para un equipo. |

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `Kit F7 C06: interpretabilidad práctica y laboratorio`, no escondido en una ruta del repositorio.

### Qué contiene

- `README.md`: esta guía y la explicación del ejercicio.
- `Makefile`: entrada única para ejecutar y validar el kit con `make run` y `make test`.
- `requirements.txt`: dependencias declaradas; muchos kits solo usan la biblioteca estándar de Python.
- `data/`: datos de entrada o casos de prueba realistas. Ejemplos dentro del ZIP: `data/ticket_features.csv`.
- `policies/`: umbrales, reglas de decisión o políticas operativas. Ejemplos dentro del ZIP: `policies/interpretability_policy.json`.
- `templates/`: plantillas editables para la entrega. Ejemplos dentro del ZIP: `templates/entrega.md`.
- `ops/`: código ejecutable del laboratorio. Ejemplos dentro del ZIP: `ops/ai/calibrate_policy.py`, `ops/ai/interpretability_audit.py`, `ops/build_release_eval_pack.py`, `ops/check_student_submission.py`.
- `tests/`: tests que comprueban que el ejercicio sigue siendo reproducible. Ejemplos dentro del ZIP: `tests/test_lab_contract.py`.
- `output/`: salidas generadas o esperadas que debes revisar. Ejemplos dentro del ZIP: `output/decision.md`, `output/interpretability_decision.md`, `output/model_card_fragment.md`, `output/model_card_interpretability.md`, ....
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
- `output/interpretability_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/model_card_fragment.md`: lectura humana de la decisión, informe o runbook.
- `output/model_card_interpretability.md`: lectura humana de la decisión, informe o runbook.
- `output/student/decision.md`: lectura humana de la decisión, informe o runbook.
- `output/student/model_card_fragment.md`: lectura humana de la decisión, informe o runbook.
- `solutions/reference/decision.md`: lectura humana de la decisión, informe o runbook.
- `solutions/reference/model_card_fragment.md`: lectura humana de la decisión, informe o runbook.
- `output/calibration_manifest.json`: evidencia estructurada para validar o automatizar.
- `output/calibration_report.json`: evidencia estructurada para validar o automatizar.
- `output/ci_explanation_gate.json`: evidencia estructurada para validar o automatizar.
- `output/ci_release_gate.json`: evidencia estructurada para validar o automatizar.

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
4. Revisa `policies/` para adaptar límites de riesgo, criterios de bloqueo o reglas de negocio.
5. Usa `templates/` como base documental; no entregues una plantilla sin completar.
6. Coloca tu versión en `solutions/mi-equipo/` y compárala contra la referencia o contra los tests.
7. Guarda los outputs finales y una nota breve con la decisión técnica que tomarías en un proyecto real.

### Criterio de validación

El kit está completo cuando se puede descargar, extraer, ejecutar con `make run`, validar con `make test` y explicar sin depender de ninguna carpeta externa. Si una práctica menciona código, datos, contrato, CSV, SQL, política o plantilla, ese contenido debe venir dentro del ZIP.
<!-- zip-quality-audit:end -->
