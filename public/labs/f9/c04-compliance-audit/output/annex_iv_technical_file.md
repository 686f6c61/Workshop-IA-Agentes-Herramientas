# Technical file mínimo · Ayuda de priorización para admisiones

Este documento es un esqueleto operativo inspirado en Annex IV. Debe completarse con documentación real antes de una revisión formal.

## 1. Identidad y alcance

- `system_id`: `admissions_prioritization_helper`.
- Owner: `equipo-datos-academicos`.
- Fecha de revisión: `2026-06-07`.
- Versión de modelo: `provider-model@2026-06-07`.
- Versión de prompt: `admissions-prompt@0.2.0`.
- Versión de índice RAG: `admissions-index@2026.1`.
- Versión de política de tools: `admissions-tools@0.1.0`.

## 2. Finalidad prevista

Ordenar expedientes para revisión de admisiones. Efecto declarado: `prioritize;rank`. Autonomía: `human_review_required`.

## 3. Clasificación inicial

- Resultado: `alto_riesgo_posible`.
- Motivo: dominio de impacto alto con efecto que prioriza, ordena o influye en una decisión relevante.
- Esta clasificación debe validarse con asesoría competente antes de producción regulada.

## 4. Arquitectura y componentes

| Componente | Versión | Qué revisar |
|---|---|---|
| Modelo | `provider-model@2026-06-07` | proveedor, región, contrato, límites y cambios de versión |
| Prompt | `admissions-prompt@0.2.0` | instrucciones, salidas, límites y pruebas de regresión |
| RAG | `admissions-index@2026.1` | linaje, ACL, vigencia, reindexado y calidad de recuperación |
| Tools | `admissions-tools@0.1.0` | scopes, aprobación, egress, idempotencia y trazas |

## 5. Datos y privacidad

- Datos personales declarados: `true`.
- Categorías especiales declaradas: `false`.
- Revisar linaje, minimización, retención, derechos y transferencias antes de publicar.

## 6. Evidencias enlazadas

| Marco | Requisito | Estado | Evidencia |
|---|---|---|---|
| ISO/IEC 42001 | `AIMS_SCOPE` | `cerrado` | `output/iso42001_aims_scope.md` |
| NIST AI RMF | `AI_INVENTORY` | `cerrado` | `output/ai_system_register.csv` |
| AI Act | `AIACT_ART9_RISK_MANAGEMENT` | `cerrado` | `../c01-risk-governance/output/risk_register.md` |
| AI Act | `AIACT_ART10_DATA_GOVERNANCE` | `condición` | `output/data_governance_pack.md` |
| AI Act | `AIACT_ART11_ANNEXIV_TECH_DOC` | `cerrado` | `output/annex_iv_technical_file.md` |
| AI Act | `AIACT_ART12_RECORD_KEEPING` | `bloqueante` | `output/trace_evidence_sample.jsonl` |
| AI Act | `AIACT_ART13_INSTRUCTIONS` | `condición` | `output/operator_manual.md` |
| AI Act | `AIACT_ART14_HUMAN_OVERSIGHT` | `condición` | `output/human_oversight_playbook.md` |
| AI Act | `AIACT_ART15_QUALITY_ROBUSTNESS` | `condición` | `output/eval_and_robustness_report.md` |
| AI Act | `AIACT_ART17_QMS` | `cerrado` | `output/change_control_record.md` |
| AI Act | `AIACT_ART27_FRIA` | `condición` | `output/fria_precheck.md` |
| AI Act | `AIACT_ART72_POST_MARKET` | `condición` | `post_deployment_monitoring_plan.md` |
| GDPR | `GDPR_DPIA` | `condición` | `../c02-privacy-dpia/output/dpia_precheck.md` |
| NIST AI RMF | `NIST_GOVERN_MAP_MEASURE_MANAGE` | `cerrado` | `output/article_to_artifact_crosswalk.csv` |

## 7. Criterio de salida

Gate actual: `revisar_antes`.

Para avanzar, todo requisito bloqueante debe tener evidencia aceptada, versionada y con owner. Las condiciones deben tener fecha de cierre y responsable.
