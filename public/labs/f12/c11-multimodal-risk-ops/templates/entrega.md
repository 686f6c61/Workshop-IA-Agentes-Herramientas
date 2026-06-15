# Entrega · F12 C11 · Privacidad, seguridad y operación multimodal

## Contexto

- Sistema o flujo auditado:
- Modalidades implicadas:
- Datos personales o secretos posibles:
- Destinos externos:
- Owner técnico:
- Fecha:

## Ejecución

Comandos:

```bash
make run
make test
```

Archivos revisados:

- `output/risk_report.md`
- `output/risk_matrix.csv`
- `output/redaction_plan.csv`
- `output/retention_matrix.csv`
- `output/threat_model.csv`
- `output/artifact_lineage.csv`
- `output/policy_decisions.md`
- `output/detector_eval_report.md`
- `output/incident_runbook.md`
- `output/multimodal_risk_gate.svg`

## Resultado

- Decisión global:
- Casos bloqueados:
- Casos en revisión:
- Modalidad que más riesgo concentra:
- Control faltante más importante:
- Redacción o minimización aplicada:
- Falso negativo más peligroso:
- Decisión de policy-as-code que bloquea o revisa:
- Artifact hash o lineage que usaría para auditar:

## Cambio realizado

- Caso nuevo añadido en `data/multimodal_risk_cases.json`:
- Control añadido en `contracts/multimodal_risk_policy.json`:
- Destino revisado:
- Retención modificada:
- Muestra añadida en `data/detector_eval_cases.json`:
- Decisión añadida en `data/policy_decision_examples.json`:
- Regla modificada en `policies/egress_policy.rego` o `policies/egress_policy.cedar`:

## Decisión técnica

Marca una:

- [ ] Publicaría.
- [ ] Publicaría con condiciones.
- [ ] Revisaría antes de publicar.
- [ ] Bloquearía el release.

Justificación:

Threat model del caso:

- Activo:
- Frontera de confianza:
- Fallo que intentas prevenir:
- Control técnico:
- Prueba que lo demuestra:

Policy-as-code:

- Input que llega a la política:
- Resultado esperado:
- Razón de `allow`, `review` o `deny`:

Detector:

- Entidad que debe detectar:
- Precision/recall observado:
- Falso negativo que no aceptarías:

## Límites

- Qué no detecta este kit:
- Qué falsos negativos buscaría:
- Qué herramienta real evaluaría después:
- Qué evidencia pediría a legal, seguridad o plataforma:
- Qué metadato oculto revisaría antes de publicar:
- Qué salida externa bloquearía aunque el modelo la proponga:

## Próximo paso

- Caso de regresión:
- Ticket de seguridad:
- Revisión de privacidad:
- Cambio de arquitectura:
