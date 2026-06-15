# Próxima fecha de gate

Fecha propuesta: `2026-06-28`.

## Condiciones para repetir

1. Export real de trazas conectado al contrato de record-keeping.
2. Evidencia de identidad del agente en runtime.
3. Prueba de separacion `prepare` / `execute`.
4. Decisión formal de retención.
5. Rollback probado para piloto.

## Comando

```bash
python3 ops/run_governance_lab.py \
  --findings data/governance_findings_student.csv \
  --output-dir output/student \
  --write
```
