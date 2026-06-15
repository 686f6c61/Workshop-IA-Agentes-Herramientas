# Decisión de serving

Estado: `block`
Ventana actual: `current_2026_w24_bad`
Política candidata: `policy_candidate_v4`

| Diagnóstico | Valor |
|---|---:|
| `slice_population_stability_index` | 0.402894 |
| `action_population_stability_index` | 0.867753 |
| `blocked_slices` | 4 |
| `blocked_rollout_stages` | 3 |
| `plan_status` | block |

## Lectura

La política no debería avanzar. Revisa slices bloqueados, drift de población, plan de rollout, trazas y preparación de rollback.
