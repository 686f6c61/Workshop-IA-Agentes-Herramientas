# Revision de evidencias fuente

Este informe comprueba que el laboratorio no se apoya solo en salidas generadas. Cada decision debe conectarse con una evidencia fuente del temario: contrato, trazabilidad, slices, experimento o alcance.

- Evidencias declaradas: 5.
- Evidencias ausentes: 0.

| Evidencia | Capitulo | Ruta | Existe | Para que sirve |
|---|---|---|---|---|
| `traceability_policy` | `08.06` | `evidence/traceability_policy.md` | `true` | Define reconstruccion de decisiones y cierre de missing_trace_rate. |
| `data_quality_contract` | `08.02` | `evidence/data_quality_contract.json` | `true` | Fija columnas, umbrales bloqueantes y reglas de revisión. |
| `slice_remediation_plan` | `08.05` | `evidence/slice_remediation_plan.md` | `true` | Conecta slices críticos con acciones y evidencia esperada. |
| `experiment_exposure_contract` | `08.07` | `evidence/experiment_exposure_contract.json` | `true` | Define unidad, exposición real, metrica primaria y guardrails. |
| `data_release_scope` | `08.01` | `evidence/data_release_scope.md` | `true` | Declara alcance permitido y condiciones para avanzar. |

## Cómo usarlo

Primero se mira el estado final. Despues se abre la evidencia fuente que sostiene cada decision. Si un control está en `pass`, el archivo debe existir y debe poder defenderse sin cambiar umbrales después de ver el resultado.
