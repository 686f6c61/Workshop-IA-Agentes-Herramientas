# Paquete de evidencias del laboratorio multimodal

## Decisión ejecutiva

- Baseline: `block_release`.
- Remediado: `review_release`.
- Candidate: `ship`.
- Casos bloqueados al inicio: `2`.
- Casos publicables tras remediación: `7`.

## Casos que no pueden publicarse en baseline

- `policy_rag_with_internal_slides`: Bloquear, escanear secretos, redactar artefactos y definir runbook de revocación.
- `computer_use_claim_submission`: Bloquear, escanear secretos, redactar artefactos y definir runbook de revocación.

## Evidencias mínimas para defender el release

- Contratos de entrada y salida por capacidad.
- Golden set y slices de evaluación.
- Manifest de retrieval, ACL de fuentes y grounding.
- Trazas de turnos, latencia y tool calls.
- Redaction plan, policy decision y artifact lineage.
- Runbook para secretos, PII y acciones externas.
- SLI/SLO por caso y por escenario.
- Change request con owner, aprobadores y rollback.

## Qué mirar en una revisión

1. Ningún caso con secreto o acción externa puede depender solo del prompt.
2. Las métricas deben estar separadas por modalidad y por slice.
3. El coste y la latencia forman parte del release, no del apéndice.
4. La evidencia debe poder descargarse, reproducirse y explicarse.
5. Un release candidate debe incluir diff, manifest de versiones, contract tests y checklist de PR.
