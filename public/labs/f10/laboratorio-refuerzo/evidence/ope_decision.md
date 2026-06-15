# Decisión OPE

Estado: `pass`
Política histórica: `routing_policy_stable_v1`
Política candidata: `routing_policy_candidate_v2`

| Estimador | Valor |
|---|---:|
| `direct_method` | 0.732683 |
| `ips` | 0.788824 |
| `wis` | 0.748713 |
| `doubly_robust` | 0.743715 |

| Diagnóstico | Valor |
|---|---:|
| `events` | 12 |
| `max_importance_weight` | 1.538462 |
| `min_importance_weight` | 0.578947 |
| `ess` | 11.022744 |
| `ess_ratio` | 0.918562 |
| `logged_action_support` | 0.4575 |
| `abs_ips_wis_gap` | 0.040112 |
| `abs_dm_dr_gap` | 0.011031 |
| `bootstrap_ci_lower` | 0.723226 |
| `bootstrap_ci_upper` | 0.763769 |
| `min_slice_events` | 3 |
| `max_unsupported_target_probability_mass` | 0.07 |

## Intervalo de confianza

Estimador: `doubly_robust`
Confianza: `0.9`
Intervalo bootstrap: `0.723226` - `0.763769`

## Lectura

La política candidata puede pasar a modo sombra o piloto muy limitado. No queda aprobada para producción amplia: OPE reduce riesgo, no sustituye medición online.

## Condiciones antes del siguiente paso

1. Revisar eventos con pesos altos.
2. Confirmar que cada evento incluye propensión histórica.
3. Medir soporte por slice y acción.
4. Comparar IPS, WIS, DM y DR; si se separan demasiado, no publicar.
5. Revisar el límite inferior del intervalo bootstrap.
6. Mantener política estable como fallback.
