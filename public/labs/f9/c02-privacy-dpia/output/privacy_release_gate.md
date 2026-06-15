# Gate de privacidad

Decisión: `revisar_antes_de_publicar`

## Bloqueos

- hay texto bruto retenido por encima del límite
- hay uso de datos personales para entrenamiento sin decisión específica
- hay señales que exigen prechequeo EIPD/DPIA documentado

## Condiciones por flujo

| Flujo | Banda | Condición mínima |
|---|---|---|
| `F-001` | bajo | Revisar `platform_ai` y conservar evidencias: `provider_dpa`, `prompt_contract`, `redaction_test`. |
| `F-002` | medio | Revisar `rag_owner` y conservar evidencias: `index_manifest`, `access_policy`, `source_catalog`. |
| `F-003` | alto | Revisar `ops_owner` y conservar evidencias: `trace_contract`, `retention_policy`. |
| `F-006` | alto | Revisar `ml_owner` y conservar evidencias: `dataset_card`, `dpia_note`, `training_decision`. |

## Evidencias obligatorias

- `data_flow_inventory.json`
- `minimization_report.md`
- `dpia_precheck.md`
- `retention_plan.csv`
- `redacted_trace_sample.jsonl`
- `presidio_style_findings.json`
- `presidio_detection_report.md`
- `privacy_release_gate.md`
- `ci_privacy_gate.json`
- `ci_privacy_gate.md`
