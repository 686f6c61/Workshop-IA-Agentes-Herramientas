# OPE quality card

Estado: `pass`
Política candidata: `routing_policy_candidate_v2`
Política histórica: `routing_policy_stable_v1`

## Lectura ejecutiva

El dataset permite una evaluación offline inicial. La siguiente fase razonable es modo sombra, no producción amplia.

## Evidencia mínima

| Check | Resultado |
|---|---:|
| `min_events` | `True` |
| `min_ess_ratio` | `True` |
| `max_importance_weight` | `True` |
| `max_abs_ips_wis_gap` | `True` |
| `max_abs_dm_dr_gap` | `True` |
| `min_logged_action_support` | `True` |
| `min_dr_estimate` | `True` |
| `min_dr_ci_lower_bound` | `True` |
| `min_slice_events` | `True` |
| `max_unsupported_target_probability_mass` | `True` |

## Slices

| Slice | Eventos | DR | ESS ratio | Max weight | Soporte |
|---|---:|---:|---:|---:|---:|
| `alta_criticidad` | 3 | 0.81484 | 0.968165 | 1.114286 | 0.6 |
| `baja_criticidad` | 4 | 0.712383 | 0.922269 | 1.538462 | 0.46 |
| `media_criticidad` | 5 | 0.726105 | 0.904065 | 1.304348 | 0.37 |

## Decisión

1. Si cualquier check queda en `False`, no hay piloto.
2. Si el intervalo inferior cae bajo el umbral, mantener en modo sombra.
3. Si una acción tiene masa candidata pero cero soporte observado, limitar la política o recoger datos.
4. Si los estimadores discrepan, revisar propensiones, reward y modelo Q.
