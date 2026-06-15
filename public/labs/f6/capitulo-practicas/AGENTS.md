# AGENTS.md operativo

Este archivo resume cómo debe trabajar un agente o asistente automático dentro del servicio `support-rag`.

## Identidad operativa

- Servicio: `support-rag`.
- Release candidata: `support-rag@1.9.0-rc1`.
- Propietario: `equipo-ia`.
- Objetivo: ayudar en soporte con RAG sin saltarse contratos, SLO ni rollback.

## Reglas obligatorias

1. Antes de publicar una respuesta externa, valida contrato de salida y evidencia.
2. Si falta evidencia, degrada a modo revisión o pide intervención humana.
3. Si una acción modifica estado real, exige idempotency key y registro de auditoría.
4. Si se supera presupuesto de error o coste, usa fallback definido en `ops/ai/routing_policy.yaml`.
5. Si aparece una incidencia nueva, genera caso de regresión y postmortem.

## Comandos reproducibles

```bash
python3 ops/run_f6_practices.py --chapter c01 --write --fail-on-invalid
python3 ops/run_f6_practices.py --all --write --fail-on-invalid
make test
```

## Evidencia mínima

- `output/c01_decision.md`
- `output/c01_report.json`
- `ops/ai/manifest.yaml`
- `ops/ai/should.md`
- `ops/ai/release_gate.py`

Un agente que no pueda dejar evidencia reproducible no debe avanzar a producción.
