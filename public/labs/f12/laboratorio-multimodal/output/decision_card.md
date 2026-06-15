# Decision card · laboratorio multimodal

Decisión remediada: `review_release`.
Release candidate propuesto: `ship`.

## Condiciones

- Mantener gates de privacidad y seguridad del capítulo 11.
- No publicar casos `review` sin owner y plan de remediación.
- Ejecutar regresión multimodal antes de cada cambio de modelo, prompt, OCR, ASR, retrieval o tool.
- Aceptar el candidato solo si el change request conserva owner, aprobadores, rollback y SLI/SLO en verde.

## Casos pendientes

- `parking_video_event_triage`: `review` · Completar evidencias: policy_decision

## Criterio de salida

El sistema puede avanzar como candidato solo si los casos pendientes quedan cerrados en `output/release_change_request.md` y `output/sli_slo_matrix.csv`.
