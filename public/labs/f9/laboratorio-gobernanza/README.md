# F9 · Laboratorio de gobernanza

Este laboratorio cierra el facsímil 9. Integra riesgo, privacidad, seguridad de aplicaciones LLM, Zero Trust para agentes, cumplimiento y evidencias en una decisión de publicación defendible.

## Ejecutar

Escenario inicial:

```bash
python3 ops/run_governance_lab.py --write
```

Escenario remediado:

```bash
python3 ops/run_governance_lab.py --findings data/governance_findings_remediated.csv --output-dir output/remediated --write
```

Escenario del alumno:

```bash
python3 ops/run_governance_lab.py --findings data/governance_findings_student.csv --output-dir output/student --write
```

Cómo gate:

```bash
python3 ops/run_governance_lab.py --write --fail-on-blocker
```

Validar una entrega:

```bash
python3 ops/check_student_submission.py --submission-dir solutions/reference --write
cat output/student_submission_report.md
```

## Entradas

| Archivo | Uso |
|---|---|
| `contracts/final_governance_policy.json` | Política de decisión, niveles, ventanas y capas obligatorias. |
| `data/governance_findings.csv` | Hallazgos iniciales por capa, requisito, owner y evidencia. |
| `data/governance_findings_remediated.csv` | Variante donde se cierra la evidencia más crítica. |
| `data/governance_findings_student.csv` | Variante que el alumno debe copiar, editar y defender. |
| `data/release_components.csv` | Versiones de modelo, prompt, RAG, tools, proveedor y fase. |
| `evidence/` | Evidencias fuente: identidad de agente, contrato de tools, memoria, credenciales y record-keeping. |
| `solutions/reference/` | Entrega modelo para comparar criterio, no para memorizar. |

## Salidas

| Archivo | Qué demuestra |
|---|---|
| `governance_release_decision.md` | Decisión final: publicar, publicar con condiciones o revisar antes. |
| `governance_report.json` | Reporte estructurado para CI o revisión técnica. |
| `control_evidence_matrix.csv` | Matriz capa -> requisito -> evidencia -> owner -> estado. |
| `source_evidence_matrix.csv` | Comprobación de rutas de evidencia declaradas. |
| `source_evidence_review.md` | Revisión explicada de evidencias fuente y huecos. |
| `technical_decision_memo.md` | Memo técnico que se podría mandar a dirección de ingeniería. |
| `zero_trust_agent_matrix.csv` | Matriz de identidad, credenciales, tools, memoria y límites por agente. |
| `agent_boundary_review.md` | Revisión explicada de menor capacidad de actuación y pruebas necesarias. |
| `remediation_plan.md` | Plan de cierre por owner, prioridad y días. |
| `evidence_package_index.md` | Índice del paquete de evidencias que se defendería en una revisión. |
| `risk_acceptance_record.md` | Registro de aceptación de riesgo residual, si aplica. |
| `executive_brief.md` | Resumen ejecutivo sin perder trazabilidad técnica. |
| `ci_gate.json` | Salida máquina para pipeline. |
| `trace_sample.jsonl` | Eventos mínimos del gate final. |

## Cómo leerlo

La entrega buena no intenta convencer con una frase. Enseña:

1. Qué sistema se evalúa.
2. Qué versión de modelo, prompt, RAG y tools está viva.
3. Qué requisitos quedan cerrados, condicionados o bloqueantes.
4. Quién es owner de cada cierre.
5. Qué evidencia se enseña.
6. Qué capacidad real tiene cada agente y qué límites se pueden probar.
7. Qué cambia al ejecutar el escenario remediado.

## Retos oficiales

### Reto 1: diagnosticar el paquete y decidir si puede avanzar

1. Lee `data/release_components.csv`, `data/governance_findings.csv` y `contracts/final_governance_policy.json`.
2. Ejecuta el escenario inicial.
3. Explica la decisión en `decision_memo.md`.
4. Identifica bloqueo, owner, evidencia esperada y archivo que usarías en CI.

### Reto 2: remediar, repetir el gate y construir evidencias defendibles

1. Ejecuta el escenario remediado y compara `output/` con `output/remediated/`.
2. Copia `data/governance_findings_student.csv`, modifica un control, ejecuta el gate y explica el cambio en `diff_notes.md`.
3. Construye o adapta evidencias en `solutions/tu-entrega/`: identidad de agente, contrato de tools, memoria y record-keeping.
4. Ejecuta `ops/check_student_submission.py` contra tu carpeta.
5. Defiende qué queda condicionado y qué no se debe aceptar como riesgo residual.

## Qué te llevas

Te llevas una práctica ejecutable sobre F9 · Laboratorio de gobernanza, con datos editables, contratos y umbrales, evidencias fuente, plantillas de entrega, código ejecutable y tests reproducibles. Trabajas con `data/governance_findings.csv` y `data/governance_findings_mi_equipo.csv`, contrastas la decisión contra `contracts/final_governance_policy.json` y ejecutas `ops/check_student_submission.py` para generar `output/agent_boundary_review.md`. La idea no es mirar una solución cerrada: es cambiar una entrada, volver a ejecutar, comparar la salida y poder defender qué harías en una revisión técnica, una asignatura o un piloto real.

## Variantes para hacerlo tuyo

- Ejecuta `make run` sin tocar nada y usa `output/agent_boundary_review.md` como línea base.
- Cambia o añade un caso en `data/governance_findings.csv` y `data/governance_findings_mi_equipo.csv` para representar un problema de tu trabajo, clase o producto.
- Endurece una regla, umbral o campo obligatorio en `contracts/final_governance_policy.json` y explica por qué el resultado debería cambiar o bloquearse.
- Compara antes/después en `output/agent_boundary_review.md` y `output/evidence_package_index.md` y escribe una decisión de una página: seguir, bloquear, medir más o cambiar el diseño.
- Completa `templates/entrega.md` con contexto, cambio, evidencia, decisión y límite; no la dejes como checklist vacía.

## Rúbrica rápida

| Nivel | Qué demuestra |
|---|---|
| Mínimo | Ejecuta `make run` y `make test`, localiza `ops/check_student_submission.py`, abre `output/agent_boundary_review.md` y explica qué decisión o señal produce. |
| Bueno | Cambia `data/governance_findings.csv`, compara antes/después y justifica la diferencia con una evidencia concreta del output. |
| Excelente | Convierte el kit en un mini caso profesional: añade un caso propio, ajusta una regla o test, documenta el límite principal y deja una recomendación accionable para un equipo. |

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `F9 · Laboratorio de gobernanza`, no escondido en una ruta del repositorio.

### Qué contiene

- `README.md`: esta guía y la explicación del ejercicio.
- `Makefile`: entrada única para ejecutar y validar el kit con `make run` y `make test`.
- `requirements.txt`: dependencias declaradas; muchos kits solo usan la biblioteca estándar de Python.
- `data/`: datos de entrada o casos de prueba realistas. Ejemplos dentro del ZIP: `data/governance_findings.csv`, `data/governance_findings_mi_equipo.csv`, `data/governance_findings_remediated.csv`, `data/governance_findings_student.csv`, ....
- `contracts/`: contratos de datos, salida, política o validación. Ejemplos dentro del ZIP: `contracts/final_governance_policy.json`.
- `templates/`: plantillas editables para la entrega. Ejemplos dentro del ZIP: `templates/entrega.md`.
- `evidence/`: evidencias preconstruidas que el kit usa como entrada o referencia. Ejemplos dentro del ZIP: `evidence/memory_retention_policy.md`, `evidence/release_scope.md`, `evidence/recordkeeping_contract.json`, `evidence/credential_scope_register.csv`, ....
- `ops/`: código ejecutable del laboratorio. Ejemplos dentro del ZIP: `ops/check_student_submission.py`, `ops/run_governance_lab.py`.
- `tests/`: tests que comprueban que el ejercicio sigue siendo reproducible. Ejemplos dentro del ZIP: `tests/test_lab_contract.py`.
- `output/`: salidas generadas o esperadas que debes revisar. Ejemplos dentro del ZIP: `output/agent_boundary_review.md`, `output/evidence_package_index.md`, `output/executive_brief.md`, `output/governance_release_decision.md`, ....
- `solutions/`: soluciones de referencia o carpeta para la entrega del alumno. Ejemplos dentro del ZIP: `solutions/mi-equipo/decision_memo.md`, `solutions/mi-equipo/diff_notes.md`, `solutions/mi-equipo/memory_retention_policy.md`, `solutions/mi-equipo/next_gate_date.md`, ....

### Ejecutar desde cero

Desde la carpeta extraída del ZIP:

```bash
make run
make test
```

`make run` construye las evidencias del ejercicio. `make test` comprueba que el kit sigue siendo ejecutable después de descargarlo, extraerlo y tocarlo.

### Qué mirar antes de entregar

- `output/agent_boundary_review.md`: lectura humana de la decisión, informe o runbook.
- `output/evidence_package_index.md`: lectura humana de la decisión, informe o runbook.
- `output/executive_brief.md`: lectura humana de la decisión, informe o runbook.
- `output/governance_release_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/mi_equipo/agent_boundary_review.md`: lectura humana de la decisión, informe o runbook.
- `output/mi_equipo/evidence_package_index.md`: lectura humana de la decisión, informe o runbook.
- `output/mi_equipo/executive_brief.md`: lectura humana de la decisión, informe o runbook.
- `output/mi_equipo/governance_release_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/mi_equipo/remediation_plan.md`: lectura humana de la decisión, informe o runbook.
- `output/mi_equipo/risk_acceptance_record.md`: lectura humana de la decisión, informe o runbook.
- `output/mi_equipo/source_evidence_review.md`: lectura humana de la decisión, informe o runbook.
- `output/mi_equipo/student_submission_report.md`: lectura humana de la decisión, informe o runbook.

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
