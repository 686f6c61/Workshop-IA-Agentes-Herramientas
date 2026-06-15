# Decision del dataset de preferencias

Estado: `block`
Snapshot: `pref_dataset_2026_06_08`
Uso previsto: `pre_dpo_or_reward_model_audit`

## Diagnósticos

| Métrica | Valor |
|---|---:|
| `pairs` | 6 |
| `task_families` | 5 |
| `avg_agreement` | 0.411667 |
| `low_agreement_rate` | 1.0 |
| `chosen_win_rate` | 0.166667 |
| `avg_reward_margin` | -0.351667 |
| `negative_margin_rate` | 0.833333 |
| `verifier_coverage` | 0.5 |
| `duplicate_pair_rate` | 0.0 |
| `reversed_conflicts` | 1 |
| `length_bias_ratio` | 1.299065 |

## Checks

| Check | Pasa |
|---|---|
| `schema` | si |
| `min_pairs` | no |
| `min_task_families` | si |
| `min_avg_agreement` | no |
| `max_low_agreement_rate` | no |
| `min_chosen_win_rate` | no |
| `min_avg_reward_margin` | no |
| `max_negative_margin_rate` | no |
| `min_verifier_coverage` | no |
| `max_duplicate_pair_rate` | si |
| `max_reversed_conflicts` | no |
| `max_length_bias_ratio` | si |

## Lectura tecnica

El dataset debe bloquearse antes de entrenar. Revisa pares con margen negativo, bajo acuerdo, duplicados, contradicciones, cobertura de verificador y sesgo de longitud antes de gastar GPU.
