# Plan de remediacion

| Prioridad | Sistema | Capa | Requisito | Estado | Owner | Plazo | Accion |
|---:|---|---|---|---|---|---:|---|
| 1 | `admissions_prioritization_helper` | `compliance` | `recordkeeping_export` | `block` | `owner-platform` | 0 | conectar contrato a export real de trazas |
| 2 | `admissions_prioritization_helper` | `privacy` | `dpia_retention_decision` | `review` | `owner-privacy` | 14 | cerrar decisión formal de retención |
| 3 | `admissions_prioritization_helper` | `zero_trust_agents` | `least_agency_tool_boundary` | `review` | `owner-platform` | 14 | separar prepare de execute y limitar scopes por tool |
| 4 | `admissions_prioritization_helper` | `llm_appsec` | `tool_and_rag_boundary` | `review` | `owner-platform` | 14 | probar escenarios de permisos en piloto |
| 5 | `admissions_prioritization_helper` | `zero_trust_agents` | `agent_identity_and_short_lived_credentials` | `review` | `owner-platform` | 14 | asignar agent_id y credenciales de corta duración |
| 6 | `admissions_prioritization_helper` | `compliance` | `fria_precheck` | `review` | `owner-governance` | 21 | cerrar precheck con deployer |
| 7 | `admissions_prioritization_helper` | `operation` | `rollback_and_monitoring` | `review` | `owner-ops` | 21 | definir rollback y thresholds |
| 8 | `academic_support_assistant` | `zero_trust_agents` | `memory_ttl_and_source_integrity` | `review` | `owner-privacy` | 21 | fijar TTL hash de origen y purga de memoria |
| 9 | `academic_support_assistant` | `compliance` | `post_deployment_monitoring` | `review` | `owner-ops` | 21 | automatizar reporte mensual |

## Criterio de cierre

Un item no se cierra por comentario verbal. Se cierra cuando existe evidencia versionada, owner, fecha y salida del gate repetida.
