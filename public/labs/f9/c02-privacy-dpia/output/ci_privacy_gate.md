# Gate CI de privacidad

Estado: `fail`

Este gate comprueba que la privacidad no queda como intención editorial: revisa trazas redactadas, retención, flujos altos, señales EIPD/DPIA y entrenamiento con datos personales.

## Hallazgos

| Severidad | Check | Dónde | Mensaje |
|---|---|---|---|
| fail | `retention_too_long` | `retention_plan.csv:F-003` | retención 90 días supera el valor esperado 14 para `traza_operativa` |
| fail | `retention_too_long` | `retention_plan.csv:F-006` | retención 365 días supera el valor esperado 0 para `entrenamiento` |
| fail | `training_personal_data` | `F-006` | uso de datos personales para entrenamiento o ajuste sin decisión específica cerrada |
| fail | `release_gate` | `privacy_release_gate.md` | el gate de privacidad indica revisar antes de publicar |

## Cómo convertirlo en CI real

1. Genera el paquete con `python3 ops/build_privacy_pack.py --write`.
2. Ejecuta `python3 ops/privacy_ci_gate.py --write --fail-on-blocker` en tu pipeline.
3. Falla el release si el estado es `fail`.
