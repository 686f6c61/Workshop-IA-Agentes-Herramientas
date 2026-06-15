# Decisión OPE

Estado: `block`
Política histórica: `routing_policy_stable_v1`
Política candidata: `routing_policy_candidate_v2`

| Estimador | Valor |
|---|---:|
| `direct_method` | 0.739483 |
| `ips` | 9.341561 |
| `wis` | 0.74928 |
| `doubly_robust` | 0.903728 |

| Diagnóstico | Valor |
|---|---:|
| `events` | 6 |
| `max_importance_weight` | 31.666667 |
| `min_importance_weight` | 0.036585 |
| `ess` | 2.884691 |
| `ess_ratio` | 0.480782 |
| `logged_action_support` | 0.496667 |
| `abs_ips_wis_gap` | 8.59228 |
| `abs_dm_dr_gap` | 0.164245 |
| `bootstrap_ci_lower` | 0.772558 |
| `bootstrap_ci_upper` | 1.031696 |
| `min_slice_events` | 2 |
| `max_unsupported_target_probability_mass` | 0.905 |

## Intervalo de confianza

Estimador: `doubly_robust`
Confianza: `0.9`
Intervalo bootstrap: `0.772558` - `1.031696`

## Lectura

La política candidata no debe moverse a piloto. Hay poca cobertura, pesos extremos o desacuerdo entre estimadores; toca recoger mejor dato, limitar la política o revisar el modelo de recompensa.

## Condiciones antes del siguiente paso

1. Revisar eventos con pesos altos.
2. Confirmar que cada evento incluye propensión histórica.
3. Medir soporte por slice y acción.
4. Comparar IPS, WIS, DM y DR; si se separan demasiado, no publicar.
5. Revisar el límite inferior del intervalo bootstrap.
6. Mantener política estable como fallback.
