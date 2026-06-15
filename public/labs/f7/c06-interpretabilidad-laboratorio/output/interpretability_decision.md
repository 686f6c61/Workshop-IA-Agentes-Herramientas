# Decisión de interpretabilidad

Estado: **defendible**.

## Lectura ejecutiva

La explicación local es defendible para diagnóstico interno porque no se acepta por intuición: se contrasta con borrado de features, importancia global, estabilidad, contrafactuales accionables, suficiencia y contrato de uso.
El contrato limita su consumo a ingeniería, soporte N2 y producto. No es una decisión final, no es una comunicación automática a usuario y no sustituye revisión operativa.

## Caso de referencia

El caso `t001` tiene score `0.859603` y predicción `1`.

| Feature | Valor | Peso | Contribución logit | Dirección |
|---|---:|---:|---:|---|
| `student_wait_days` | `12.0` | `0.13` | `1.56` | sube |
| `missing_payment` | `1.0` | `1.25` | `1.25` | sube |
| `prior_cases` | `3.0` | `0.28` | `0.84` | sube |

## Lectura global

La feature con mayor caída por permutación es `deadline_hours` con drop `0.25`. Eso no prueba causalidad, pero sí indica que el modelo depende de esa señal para mantener rendimiento.
La estabilidad top-1 es `0.9667`. Si este valor fuera bajo, la explicación cambiaría demasiado ante perturbaciones pequeñas y no sería buen soporte para una release.

## Contrafactual útil

El caso `t001` tiene un cambio accionable que modifica la decisión:

- score original: `0.859603`.
- predicción original: `1`.
- cambio propuesto: `comprobar y resolver pago pendiente si procede`.
- score después del cambio: `0.636915`.
- predicción después del cambio: `0`.

## Checks

| Check | Estado | Lectura |
|---|---|---|
| `deletion_top_feature_drop` | pasa | `{'max_drop': 0.444993, 'minimum': 0.08}` |
| `permutation_importance_drop` | pasa | `{'max_drop': 0.25, 'minimum': 0.03}` |
| `stability_top1` | pasa | `{'top1_agreement': 0.9667, 'minimum': 0.7}` |
| `counterfactual_available` | pasa | `al menos un caso tiene contrafactual accionable que cambia la decisión` |
| `comprehensiveness_top2` | pasa | `{'average': 0.210094, 'minimum': 0.12}` |
| `sufficiency_top2` | pasa | `{'average': 0.063245, 'maximum': 0.2}` |
| `feature_proxy_scan` | pasa | `{'max_abs_correlation': 0.8837, 'maximum': 0.9, 'top_pair': {'feature_a': 'prior_cases', 'feature_b': 'student_wait_days', 'correlation': 0.8837, 'abs_correlation': 0.8837}}` |

## Decisión profesional

Usaría esta explicación para depurar, revisar casos y preparar un fragmento de model card. No la usaría como mensaje automático a usuario final ni como justificación única de una acción.

## Siguiente iteración

1. Monitorizar distribución de top features en producción.
2. Revisar la pareja de features más correlacionada si se acerca al máximo permitido.
3. Mantener el contrato de explicación versionado junto al modelo y los datos.
4. Convertir estos checks en gate de CI para que una release no cambie explicaciones sin evidencia.
