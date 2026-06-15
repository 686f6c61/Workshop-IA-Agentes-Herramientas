# Decision del dataset de preferencias

Estado: `pass`
Snapshot: `pref_dataset_2026_06_08`
Uso previsto: `pre_dpo_or_reward_model_audit`

## Diagnósticos

| Métrica | Valor |
|---|---:|
| `pairs` | 12 |
| `task_families` | 12 |
| `avg_agreement` | 0.863333 |
| `low_agreement_rate` | 0.0 |
| `chosen_win_rate` | 1.0 |
| `avg_reward_margin` | 0.500833 |
| `negative_margin_rate` | 0.0 |
| `verifier_coverage` | 0.833333 |
| `duplicate_pair_rate` | 0.0 |
| `reversed_conflicts` | 0 |
| `length_bias_ratio` | 2.135678 |

## Checks

| Check | Pasa |
|---|---|
| `schema` | si |
| `min_pairs` | si |
| `min_task_families` | si |
| `min_avg_agreement` | si |
| `max_low_agreement_rate` | si |
| `min_chosen_win_rate` | si |
| `min_avg_reward_margin` | si |
| `max_negative_margin_rate` | si |
| `min_verifier_coverage` | si |
| `max_duplicate_pair_rate` | si |
| `max_reversed_conflicts` | si |
| `max_length_bias_ratio` | si |

## Lectura tecnica

El dataset pasa el contrato mínimo para experimentar con DPO o reward modeling en un entorno controlado. No significa que el modelo ajustado sea publicable; significa que el dato deja suficiente evidencia para entrenar y evaluar sin empezar a ciegas.
