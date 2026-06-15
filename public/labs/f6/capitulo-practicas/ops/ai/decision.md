# Decisión operativa inicial

Servicio: `support-rag`.
Release candidata: `support-rag@1.9.0-rc1`.
Decisión: `ready_for_smoke`.

## Evidencia

- Existe `manifest.yaml` con owner, SLO, rollback y evaluación.
- Existe `should.md` con comportamiento verificable.
- Existe `release_gate.py` para producir una decisión reproducible.

## Condición de avance

El cambio solo puede pasar a smoke si el gate local devuelve `ready_for_smoke` y si el siguiente capítulo define el contrato de runtime.
