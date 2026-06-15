# Matriz de huecos de cumplimiento

Este informe no decide por el equipo legal. Sirve para que ingeniería vea qué evidencia existe, cuál falta y qué gate se deriva de los datos cargados.

| Sistema | Clasificación inicial | Decisión | Cerrados | Condiciones | Bloqueantes |
|---|---|---|---:|---:|---:|
| Asistente académico con RAG | `gobernanza_y_transparencia` | `publicar_con_condiciones` | 5 | 1 | 0 |
| Ayuda de priorización para admisiones | `alto_riesgo_posible` | `revisar_antes` | 6 | 7 | 1 |
| Asistente interno de código | `gobernanza_y_transparencia` | `publicar_con_seguimiento` | 5 | 0 | 0 |

## Asistente académico con RAG

- `system_id`: `academic_support_assistant`.
- Clasificación inicial: `gobernanza_y_transparencia`.
- Motivo: uso con personas, contenido o datos que exige límites, instrucciones, trazas y revisión.
- Gate: `publicar_con_condiciones`.

| Requisito | Estado | Evidencia | Owner | Qué hacer |
|---|---|---|---|---|
| `AIMS_SCOPE` | `cerrado` | `output/iso42001_aims_scope.md` | `owner-governance` | mantener versión y fecha de revisión |
| `AI_INVENTORY` | `cerrado` | `output/ai_system_register.csv` | `equipo-plataforma-ia` | mantener versión y fecha de revisión |
| `AIACT_ART15_QUALITY_ROBUSTNESS` | `cerrado` | `../c03-llm-appsec/output/appsec_gate_report.md` | `owner-eval` | mantener versión y fecha de revisión |
| `AIACT_ART72_POST_MARKET` | `condición` | `output/change_control_record.md` | `owner-ops` | cerrar condición y repetir gate |
| `GDPR_DPIA` | `cerrado` | `../c02-privacy-dpia/output/dpia_precheck.md` | `owner-privacy` | mantener versión y fecha de revisión |
| `NIST_GOVERN_MAP_MEASURE_MANAGE` | `cerrado` | `output/article_to_artifact_crosswalk.csv` | `owner-governance` | mantener versión y fecha de revisión |

## Ayuda de priorización para admisiones

- `system_id`: `admissions_prioritization_helper`.
- Clasificación inicial: `alto_riesgo_posible`.
- Motivo: dominio de impacto alto con efecto que prioriza, ordena o influye en una decisión relevante.
- Gate: `revisar_antes`.

| Requisito | Estado | Evidencia | Owner | Qué hacer |
|---|---|---|---|---|
| `AIMS_SCOPE` | `cerrado` | `output/iso42001_aims_scope.md` | `owner-governance` | mantener versión y fecha de revisión |
| `AI_INVENTORY` | `cerrado` | `output/ai_system_register.csv` | `equipo-datos-academicos` | mantener versión y fecha de revisión |
| `AIACT_ART9_RISK_MANAGEMENT` | `cerrado` | `../c01-risk-governance/output/risk_register.md` | `owner-risk` | mantener versión y fecha de revisión |
| `AIACT_ART10_DATA_GOVERNANCE` | `condición` | `output/data_governance_pack.md` | `owner-data` | cerrar condición y repetir gate |
| `AIACT_ART11_ANNEXIV_TECH_DOC` | `cerrado` | `output/annex_iv_technical_file.md` | `equipo-datos-academicos` | mantener versión y fecha de revisión |
| `AIACT_ART12_RECORD_KEEPING` | `bloqueante` | `output/trace_evidence_sample.jsonl` | `owner-platform` | cerrar antes de avanzar de fase |
| `AIACT_ART13_INSTRUCTIONS` | `condición` | `output/operator_manual.md` | `owner-product` | cerrar condición y repetir gate |
| `AIACT_ART14_HUMAN_OVERSIGHT` | `condición` | `output/human_oversight_playbook.md` | `owner-ops` | cerrar condición y repetir gate |
| `AIACT_ART15_QUALITY_ROBUSTNESS` | `condición` | `output/eval_and_robustness_report.md` | `owner-eval` | cerrar condición y repetir gate |
| `AIACT_ART17_QMS` | `cerrado` | `output/change_control_record.md` | `owner-quality` | mantener versión y fecha de revisión |
| `AIACT_ART27_FRIA` | `condición` | `output/fria_precheck.md` | `owner-governance` | cerrar condición y repetir gate |
| `AIACT_ART72_POST_MARKET` | `condición` | `post_deployment_monitoring_plan.md` | `operations_owner` | cerrar condición y repetir gate |
| `GDPR_DPIA` | `condición` | `../c02-privacy-dpia/output/dpia_precheck.md` | `owner-privacy` | cerrar condición y repetir gate |
| `NIST_GOVERN_MAP_MEASURE_MANAGE` | `cerrado` | `output/article_to_artifact_crosswalk.csv` | `owner-governance` | mantener versión y fecha de revisión |

## Asistente interno de código

- `system_id`: `internal_coding_helper`.
- Clasificación inicial: `gobernanza_y_transparencia`.
- Motivo: uso con personas, contenido o datos que exige límites, instrucciones, trazas y revisión.
- Gate: `publicar_con_seguimiento`.

| Requisito | Estado | Evidencia | Owner | Qué hacer |
|---|---|---|---|---|
| `AIMS_SCOPE` | `cerrado` | `output/iso42001_aims_scope.md` | `owner-governance` | mantener versión y fecha de revisión |
| `AI_INVENTORY` | `cerrado` | `output/ai_system_register.csv` | `equipo-ingenieria` | mantener versión y fecha de revisión |
| `AIACT_ART15_QUALITY_ROBUSTNESS` | `cerrado` | `output/eval_and_robustness_report.md` | `owner-eval` | mantener versión y fecha de revisión |
| `AIACT_ART72_POST_MARKET` | `cerrado` | `output/change_control_record.md` | `owner-ops` | mantener versión y fecha de revisión |
| `NIST_GOVERN_MAP_MEASURE_MANAGE` | `cerrado` | `output/article_to_artifact_crosswalk.csv` | `owner-governance` | mantener versión y fecha de revisión |
