# Validación de diseño experimental

Estado: **pass**.

| Check | Estado | Mensaje |
|---|---|---|
| `plan_field:hypothesis` | `pass` | Campo hypothesis presente en analysis_plan.json. |
| `plan_field:unit` | `pass` | Campo unit presente en analysis_plan.json. |
| `plan_field:population` | `pass` | Campo population presente en analysis_plan.json. |
| `plan_field:treatment` | `pass` | Campo treatment presente en analysis_plan.json. |
| `plan_field:control` | `pass` | Campo control presente en analysis_plan.json. |
| `plan_field:primary_metric` | `pass` | Campo primary_metric presente en analysis_plan.json. |
| `plan_field:metric_window` | `pass` | Campo metric_window presente en analysis_plan.json. |
| `plan_field:guardrail_metrics` | `pass` | Campo guardrail_metrics presente en analysis_plan.json. |
| `plan_field:planned_looks` | `pass` | Campo planned_looks presente en analysis_plan.json. |
| `plan_field:decision_rules` | `pass` | Campo decision_rules presente en analysis_plan.json. |
| `primary_metric_in_catalog` | `pass` | La metrica primaria debe existir en metric_catalog.json y tener type=primary. |
| `guardrail_in_catalog:negative_feedback` | `pass` | Cada guardrail del plan debe existir en el catalogo con type=guardrail. |
| `guardrail_in_catalog:latency_ms` | `pass` | Cada guardrail del plan debe existir en el catalogo con type=guardrail. |
| `guardrail_in_catalog:cost_eur` | `pass` | Cada guardrail del plan debe existir en el catalogo con type=guardrail. |
| `guardrail_in_catalog:citation_valid` | `pass` | Cada guardrail del plan debe existir en el catalogo con type=guardrail. |
| `one_primary_metric` | `pass` | Debe haber una metrica primaria clara; el resto se reporta como guardrail o diagnostico. |
| `exposure_fields` | `pass` | La flag debe exigir campo de exposición real. |
| `targeting_key_matches_unit` | `pass` | La unidad del plan debe coincidir con el targeting_key o estar justificada. |
