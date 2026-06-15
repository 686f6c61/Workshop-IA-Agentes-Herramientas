# Memo técnico de decisión

Decisión recomendada: `revisar_antes`.

## Motivo

El primer bloqueo es `recordkeeping_export` en `admissions_prioritization_helper`. Owner `owner-platform` debe ejecutar: conectar contrato a export real de trazas.

## Condiciones abiertas

| Sistema | Capa | Requisito | Owner | Plazo |
|---|---|---|---|---:|
| `academic_support_assistant` | `compliance` | `post_deployment_monitoring` | `owner-ops` | 21 |
| `admissions_prioritization_helper` | `privacy` | `dpia_retention_decision` | `owner-privacy` | 14 |
| `admissions_prioritization_helper` | `llm_appsec` | `tool_and_rag_boundary` | `owner-platform` | 14 |
| `admissions_prioritization_helper` | `compliance` | `fria_precheck` | `owner-governance` | 21 |
| `admissions_prioritization_helper` | `operation` | `rollback_and_monitoring` | `owner-ops` | 21 |
| `admissions_prioritization_helper` | `zero_trust_agents` | `agent_identity_and_short_lived_credentials` | `owner-platform` | 14 |
| `admissions_prioritization_helper` | `zero_trust_agents` | `least_agency_tool_boundary` | `owner-platform` | 14 |
| `academic_support_assistant` | `zero_trust_agents` | `memory_ttl_and_source_integrity` | `owner-privacy` | 21 |

## Recomendación operativa

Repetir el gate si cambia modelo, prompt, RAG, tool, política, memoria, proveedor, finalidad o fase. Conservar esta decisión, el diff de hallazgos y el `ci_gate.json` como evidencia del criterio aplicado.
