# Revision de evidencias fuente

Este informe comprueba que las rutas declaradas en la matriz apuntan a artefactos reales dentro del kit o a salidas generadas por capítulos anteriores. No decide calidad legal; obliga a que la conversación técnica tenga archivos concretos delante.

- Evidencias revisadas: 17.
- Evidencias en `pass` sin archivo local visible: 0.

| Sistema | Capa | Requisito | Estado | Evidencia | Existe | Lectura |
|---|---|---|---|---|---|---|
| `academic_support_assistant` | `risk` | `risk_register_complete` | `pass` | `../c01-risk-governance/output/risk_register.md` | `true` | evidencia presente; revisar calidad y vigencia |
| `academic_support_assistant` | `privacy` | `dpia_precheck_and_minimization` | `pass` | `../c02-privacy-dpia/output/dpia_precheck.md` | `true` | evidencia presente; revisar calidad y vigencia |
| `academic_support_assistant` | `llm_appsec` | `rag_tool_gate` | `pass` | `../c03-llm-appsec/output/appsec_gate_report.md` | `true` | evidencia presente; revisar calidad y vigencia |
| `academic_support_assistant` | `compliance` | `post_deployment_monitoring` | `review` | `../c04-compliance-audit/output/change_control_record.md` | `true` | condición abierta; necesita cierre con owner y nuevo gate |
| `admissions_prioritization_helper` | `risk` | `high_impact_risk_register` | `pass` | `../c01-risk-governance/output/risk_register.md` | `true` | evidencia presente; revisar calidad y vigencia |
| `admissions_prioritization_helper` | `privacy` | `dpia_retention_decision` | `review` | `../c02-privacy-dpia/output/dpia_precheck.md` | `true` | condición abierta; necesita cierre con owner y nuevo gate |
| `admissions_prioritization_helper` | `llm_appsec` | `tool_and_rag_boundary` | `review` | `../c03-llm-appsec/output/appsec_gate_report.md` | `true` | condición abierta; necesita cierre con owner y nuevo gate |
| `admissions_prioritization_helper` | `compliance` | `recordkeeping_export` | `block` | `evidence/recordkeeping_contract.json` | `true` | evidencia insuficiente para avanzar aunque exista contrato técnico |
| `admissions_prioritization_helper` | `compliance` | `fria_precheck` | `review` | `../c04-compliance-audit/output/compliance_gap_matrix.md` | `true` | condición abierta; necesita cierre con owner y nuevo gate |
| `admissions_prioritization_helper` | `operation` | `rollback_and_monitoring` | `review` | `../c04-compliance-audit/output/audit_gate.md` | `true` | condición abierta; necesita cierre con owner y nuevo gate |
| `internal_coding_helper` | `risk` | `internal_use_register` | `pass` | `../c01-risk-governance/output/control_matrix.csv` | `true` | evidencia presente; revisar calidad y vigencia |
| `internal_coding_helper` | `llm_appsec` | `repo_tool_scope` | `pass` | `../c03-llm-appsec/output/tool_contract_matrix.csv` | `true` | evidencia presente; revisar calidad y vigencia |
| `internal_coding_helper` | `operation` | `local_runtime_monitoring` | `pass` | `../c04-compliance-audit/output/provider_due_diligence_checklist.md` | `true` | evidencia presente; revisar calidad y vigencia |
| `admissions_prioritization_helper` | `zero_trust_agents` | `agent_identity_and_short_lived_credentials` | `review` | `evidence/agent_identity_policy.yaml` | `true` | condición abierta; necesita cierre con owner y nuevo gate |
| `admissions_prioritization_helper` | `zero_trust_agents` | `least_agency_tool_boundary` | `review` | `evidence/tool_boundary_contract.yaml` | `true` | condición abierta; necesita cierre con owner y nuevo gate |
| `academic_support_assistant` | `zero_trust_agents` | `memory_ttl_and_source_integrity` | `review` | `evidence/memory_retention_policy.md` | `true` | condición abierta; necesita cierre con owner y nuevo gate |
| `internal_coding_helper` | `zero_trust_agents` | `repo_scoped_agent_identity` | `pass` | `evidence/credential_scope_register.csv` | `true` | evidencia presente; revisar calidad y vigencia |

## Uso en una revisión

Primero se mira el estado del gate. Después se abre la evidencia. Una evidencia existe, pero aún puede ser insuficiente: por ejemplo, un contrato de trazas no cierra record-keeping si todavía no hay export real conectado al pipeline.
