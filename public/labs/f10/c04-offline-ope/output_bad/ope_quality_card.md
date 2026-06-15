# OPE quality card

Estado: `block`
Política candidata: `routing_policy_candidate_v2`
Política histórica: `routing_policy_stable_v1`

## Lectura ejecutiva

El dataset no permite avanzar. El siguiente trabajo es mejorar cobertura, reducir pesos extremos o revisar reward/modelo Q.

## Evidencia mínima

| Check | Resultado |
|---|---:|
| `min_events` | `False` |
| `min_ess_ratio` | `True` |
| `max_importance_weight` | `False` |
| `max_abs_ips_wis_gap` | `False` |
| `max_abs_dm_dr_gap` | `False` |
| `min_logged_action_support` | `True` |
| `min_dr_estimate` | `True` |
| `min_dr_ci_lower_bound` | `True` |
| `min_slice_events` | `True` |
| `max_unsupported_target_probability_mass` | `False` |

## Slices

| Slice | Eventos | DR | ESS ratio | Max weight | Soporte |
|---|---:|---:|---:|---:|---:|
| `alta_criticidad` | 2 | 1.0928 | 0.98666 | 24.0 | 0.955 |
| `baja_criticidad` | 2 | 0.721049 | 0.990099 | 0.055556 | 0.045 |
| `media_criticidad` | 2 | 0.897335 | 0.501155 | 31.666667 | 0.49 |

## Decisión

1. Si cualquier check queda en `False`, no hay piloto.
2. Si el intervalo inferior cae bajo el umbral, mantener en modo sombra.
3. Si una acción tiene masa candidata pero cero soporte observado, limitar la política o recoger datos.
4. Si los estimadores discrepan, revisar propensiones, reward y modelo Q.
