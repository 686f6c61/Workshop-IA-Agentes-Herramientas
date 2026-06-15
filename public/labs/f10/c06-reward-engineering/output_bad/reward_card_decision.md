# Decisión de reward card

Estado: `block`
Escenario: `rag_internal_policy_reward_bad`

| Diagnóstico | Valor |
|---|---:|
| `cases` | 4 |
| `slice_count` | 3 |
| `case_pass_rate` | 0.0 |
| `hidden_case_rate` | 0.0 |
| `proxy_weight_share` | 0.568182 |
| `cost_weight_share` | 0.034091 |
| `verifier_coverage` | 0.666667 |
| `positive_length_bonus` | True |
| `required_missing` | ['abstention'] |
| `hard_gate_count` | 1 |
| `hard_gates_with_verifier` | 0 |
| `normalized_cost_terms` | 1 |
| `grader_accuracy` | 0.166666 |
| `grader_precision` | 0.25 |
| `grader_recall` | 0.25 |

| Check | Pasa |
|---|---|
| `min_cases` | no |
| `min_slice_count` | no |
| `min_case_pass_rate` | no |
| `min_hidden_case_rate` | no |
| `min_hard_gates` | no |
| `hard_gates_have_verifier` | no |
| `min_normalized_cost_terms` | no |
| `max_proxy_weight_share` | no |
| `max_cost_weight_share` | sí |
| `forbid_positive_length_bonus` | no |
| `required_terms_present` | no |

## Lectura

La reward card debe bloquearse. Revisa términos ausentes, exceso de proxy, bonus por longitud, pocos casos ocultos o casos donde gana el candidato incorrecto.
