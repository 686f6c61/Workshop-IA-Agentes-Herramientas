# F12 C12 · Laboratorio multimodal

Este laboratorio cierra el facsímil 12. No es un cuestionario: es un mini release review de un sistema multimodal con imágenes, PDFs, OCR, RAG, voz, vídeo, computer use, evaluación, privacidad y operación.

La práctica tiene dos momentos:

1. Diagnosticar el estado inicial (`baseline`).
2. Aplicar una remediación y decidir qué queda pendiente (`remediated`).
3. Convertir el caso pendiente en un `candidate` defendible como release.

## Ejecutar

Desde la carpeta extraída del ZIP:

```bash
make run
make test
```

## Qué contiene

| Archivo | Para qué sirve |
|---|---|
| `contracts/release_policy.json` | Gates de calidad, riesgo, coste, latencia, evidencias y trazabilidad por capítulo. |
| `data/baseline_cases.json` | Ocho casos iniciales con fallos reales de release. |
| `data/remediated_cases.json` | Los mismos casos después de remediar evidencias, controles y operación. |
| `data/candidate_patch.json` | Parche técnico que convierte el caso de vídeo en release candidate. |
| `data/invalid_case_examples.json` | Casos que deberían fallar antes de release por contrato incompleto. |
| `schemas/case_schema.json` | Contrato mínimo de un caso del laboratorio. |
| `schemas/candidate_patch_schema.json` | Contrato mínimo del parche de candidato. |
| `contracts/release_gate_policy.rego` | Ejemplo de policy-as-code para bloquear o permitir release. |
| `ops/run_multimodal_release_lab.py` | Runner que calcula decisiones, fallos, matrices y evidencias. |
| `templates/entrega.md` | Plantilla de entrega técnica. |
| `solutions/reference/expected_decision.md` | Solución de referencia explicada. |

## Qué genera

| Archivo | Qué mirar |
|---|---|
| `output/baseline_release_report.md` | Diagnóstico inicial: qué bloquea, qué queda en revisión y por qué. |
| `output/remediated_release_report.md` | Estado tras remediación. |
| `output/candidate_release_report.md` | Estado tras aplicar el parche de release candidate. |
| `output/release_matrix.csv` | Matriz completa por caso y escenario. |
| `output/remediation_diff.csv` | Diferencia antes/después. |
| `output/release_candidate_diff.csv` | Diferencia entre remediación y candidato. |
| `output/chapter_traceability.csv` | Qué capítulos del facsímil aparecen en cada caso. |
| `output/modality_coverage.csv` | Cobertura por modalidad y riesgo medio. |
| `output/sli_slo_matrix.csv` | SLI/SLO por caso: calidad, riesgo, latencia, coste, fallo y evidencias. |
| `output/contract_validation_report.md` | Informe de contract tests con ejemplos válidos e inválidos. |
| `output/contract_validation_matrix.csv` | Matriz de errores de contrato por caso. |
| `output/evidence_pack.md` | Paquete de evidencias para defender la decisión. |
| `output/decision_card.md` | Decisión final de release. |
| `output/release_change_request.md` | Cambio propuesto como si fuera una revisión de PR. |
| `output/release_pr_checklist.md` | Checklist de merge para un release multimodal. |
| `output/version_manifest.json` | Versiones de datos, contratos y política de regresión. |
| `output/multimodal_lab_architecture.svg` | Figura firmada del laboratorio. |

## Reto 1: diagnosticar baseline

1. Ejecuta `make run`.
2. Abre `output/baseline_release_report.md`.
3. Identifica los dos casos bloqueados.
4. Abre `output/release_matrix.csv`.
5. Para cada bloqueo, separa:
   - evidencia faltante;
   - control faltante;
   - fallo operativo;
   - riesgo que no debe depender del prompt.
6. Abre `output/chapter_traceability.csv` y comprueba que la decisión usa conceptos del facsímil, no intuiciones sueltas.

La salida mínima del reto es una decisión razonada: qué no publicarías, qué revisarías y qué sí se podría publicar con monitorización.

## Reto 2: remediar y defender release

1. Compara `data/baseline_cases.json` y `data/remediated_cases.json`.
2. Abre `output/remediation_diff.csv`.
3. Identifica qué casos pasaron de `block` a `pass`.
4. Explica por qué `parking_video_event_triage` sigue en `review`.
5. Completa `templates/entrega.md`.
6. Contrasta tu respuesta con `solutions/reference/expected_decision.md`.

La salida buena no dice “he arreglado el dataset”. Dice qué evidencia añadiste, qué control cerraste, qué métrica mejoró, qué riesgo bajó y qué sigue sin estar listo.

## Reto 3: convertir la revisión en release candidate

1. Abre `data/candidate_patch.json`.
2. Identifica qué cambia en `parking_video_event_triage`.
3. Abre `output/release_candidate_diff.csv`.
4. Comprueba que `output/candidate_release_report.md` termina en `ship`.
5. Abre `output/sli_slo_matrix.csv` y filtra el escenario `candidate`.
6. Abre `output/release_change_request.md`.
7. Abre `output/release_pr_checklist.md`.
8. Abre `output/contract_validation_report.md`.
9. Decide si aceptarías ese cambio en una revisión técnica.

La salida buena no dice “ahora pasa”. Dice qué evidencia permite que pase, quién la aprueba, qué rollback existe y qué eval se repetiría si cambia modelo, OCR, ASR, retrieval, prompt, tool o policy.

## Rúbrica rápida

| Nivel | Evidencia |
|---|---|
| Mínimo | Ejecuta el laboratorio, identifica pass/review/block y explica un bloqueo. |
| Bueno | Explica la remediación caso por caso y conecta cada decisión con capítulos concretos. |
| Excelente | Propone una tercera iteración: qué caso convertiría en `pass`, con qué evidencia y qué test añadiría. |
| Profesional | Defiende un release candidate con change request, SLI/SLO, owner, aprobadores, rollback y versionado. |

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `F12 C12 · Laboratorio multimodal`.

### Ejecutar desde cero

```bash
make run
make test
```

### Qué mirar antes de entregar

- `output/baseline_release_report.md`
- `output/remediated_release_report.md`
- `output/remediation_diff.csv`
- `output/release_candidate_diff.csv`
- `output/chapter_traceability.csv`
- `output/sli_slo_matrix.csv`
- `output/contract_validation_report.md`
- `output/contract_validation_matrix.csv`
- `output/evidence_pack.md`
- `output/decision_card.md`
- `output/release_change_request.md`
- `output/release_pr_checklist.md`
- `output/version_manifest.json`
- `solutions/reference/expected_decision.md`

### Criterio de validación

El kit está completo cuando se puede descargar, extraer, ejecutar con `make run`, validar con `make test` y defender por qué el baseline bloquea y por qué la remediación deja un único caso en revisión.
<!-- zip-quality-audit:end -->
