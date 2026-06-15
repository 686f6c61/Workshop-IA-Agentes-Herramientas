# Informe de validación de contratos

Este informe muestra por qué un caso no debería entrar en una evaluación de release solo porque tenga una historia de usuario bonita.

| Fuente | Caso | Estado | Errores |
|---|---|---|---|
| `candidate` | `catalog_alt_text` | `pass` | none |
| `candidate` | `invoice_table_extraction` | `pass` | none |
| `candidate` | `policy_rag_with_internal_slides` | `pass` | none |
| `candidate` | `voice_appointment_agent` | `pass` | none |
| `candidate` | `parking_video_event_triage` | `pass` | none |
| `candidate` | `computer_use_claim_submission` | `pass` | none |
| `candidate` | `visual_search_catalog` | `pass` | none |
| `candidate` | `student_multimodal_helpdesk` | `pass` | none |
| `invalid_examples` | `missing_policy_video` | `fail` | quality_too_sparse, missing_required_evidence:artifact_lineage|event_timeline|policy_decision|redaction_plan, missing_required_controls:redaction_plan, expected_pass_but_contract_fails |
| `invalid_examples` | `bad_ops_contract` | `fail` | missing_ops:cost_units, missing_ops:failure_rate, quality_too_sparse, expected_pass_but_contract_fails |
| `invalid_examples` | `external_action_without_owner` | `fail` | missing_required_evidence:approval_card|artifact_lineage|egress_policy|policy_decision|redaction_plan, missing_required_controls:approval_gate|egress_policy|redaction_plan|retention_policy|taint_label, expected_pass_but_contract_fails |

## Lectura de ingeniería

- Un contrato operativo incompleto no se arregla con más prompt.
- Un caso sensible que espera `pass` pero no tiene evidencias o controles debe fallar antes de llegar al modelo.
- Validar contratos reduce ambigüedad en CI/CD y evita discusiones tardías en producción.
