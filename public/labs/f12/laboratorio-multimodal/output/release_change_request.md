# Release change request · F12 C12

Estado propuesto: `ship`.
Caso que desbloquea el candidato: `parking_video_event_triage`.

## Cambio técnico

- Se registra una policy_decision explícita para tratamiento de vídeo con PII potencial.
- Se añade evaluación de redacción por región para frames con caras o matrículas.
- Se reemplaza la evaluación temporal básica por temporal_eval_v2 con falsos positivos y falsos negativos por evento.
- Se mantiene retención corta y lineage del artefacto para auditoría posterior.

## Evidencia nueva

- `policy_decision`
- `frame_region_redaction_eval`
- `temporal_eval_v2`

## Impacto medido

- Decisión antes: `review`.
- Decisión después: `pass`.
- Delta calidad: `0.0475`.
- Delta riesgo: `0.0`.
- Delta latencia: `-100 ms`.
- Delta failure rate: `-0.007`.

## Owner y aprobación

- Owner técnico: `ai_ops_video_owner`.
- Aprobadores: `privacy_owner`, `security_owner`, `operations_owner`.

## Rollback

Si temporal_eval_v2 baja de 0.78, si la redacción por región falla o si desaparece policy_decision, desactivar la ruta de vídeo y volver a revisión manual.

## Criterio de merge

- `make test` debe pasar.
- `output/sli_slo_matrix.csv` no debe contener métricas en revisión para el escenario `candidate`.
- `output/release_candidate_diff.csv` debe explicar qué cambió respecto a `remediated`.
- `output/version_manifest.json` debe registrar versiones de datos, contratos y policy.
