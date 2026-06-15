# Decisión de reward card

Estado: `pass`
Escenario: `rag_internal_policy_reward`

| Diagnóstico | Valor |
|---|---:|
| `cases` | 9 |
| `slice_count` | 6 |
| `case_pass_rate` | 1.0 |
| `hidden_case_rate` | 0.333333 |
| `proxy_weight_share` | 0.0 |
| `cost_weight_share` | 0.13 |
| `verifier_coverage` | 1.0 |
| `positive_length_bonus` | False |
| `required_missing` | [] |
| `hard_gate_count` | 3 |
| `hard_gates_with_verifier` | 3 |
| `normalized_cost_terms` | 3 |
| `grader_accuracy` | 1.0 |
| `grader_precision` | 1.0 |
| `grader_recall` | 1.0 |

| Check | Pasa |
|---|---|
| `min_cases` | sí |
| `min_slice_count` | sí |
| `min_case_pass_rate` | sí |
| `min_hidden_case_rate` | sí |
| `min_hard_gates` | sí |
| `hard_gates_have_verifier` | sí |
| `min_normalized_cost_terms` | sí |
| `max_proxy_weight_share` | sí |
| `max_cost_weight_share` | sí |
| `forbid_positive_length_bonus` | sí |
| `required_terms_present` | sí |

## Lectura

La reward card puede pasar a experimento controlado. Aun así, debe versionarse junto al dataset, los verificadores y la evaluación retenida.
