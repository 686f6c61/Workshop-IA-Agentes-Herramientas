# Heurística, horizonte y replanificación

Plan heurístico: `['validar', 'enviar', 'registrar']` con coste `4`.
Primer horizonte SAT: `k=3`.

| k | Estado | Plan |
|---:|---|---|
| 1 | UNSAT | `None` |
| 2 | UNSAT | `None` |
| 3 | SAT | `['validar', 'enviar', 'registrar']` |
| 4 | SAT | `['validar', 'enviar', 'enviar', 'registrar']` |

## Observación y replanificación

Estado observado tras el primer paso: `['cliente', 'email_pendiente_confirmacion', 'factura_validada']`.
Replan: `None`.

Si la observación contradice lo esperado, insistir no es planificar. Hay que replanificar o escalar.
