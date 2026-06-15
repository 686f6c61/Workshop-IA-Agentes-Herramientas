# Reglas policy-as-code del gate

Estas reglas explican la decisión del script. Pueden traducirse a CI, OPA, checks propios o un pipeline interno.

```python
PRIORIDAD = {
    'publicar_con_seguimiento': 0,
    'publicar_con_condiciones': 1,
    'revisar_antes': 2,
}

def subir(decision_actual, decision_nueva):
    if PRIORIDAD[decision_nueva] > PRIORIDAD[decision_actual]:
        return decision_nueva
    return decision_actual

def decidir_gate(classification, personal_data, missing_requirements, evidence_age_days, provider_exit_missing):
    decision = 'publicar_con_seguimiento'
    if classification == 'alto_riesgo_posible' and 'AIACT_ART12_RECORD_KEEPING' in missing_requirements:
        decision = subir(decision, 'revisar_antes')
    if classification == 'alto_riesgo_posible' and 'AIACT_ART11_ANNEXIV_TECH_DOC' in missing_requirements:
        decision = subir(decision, 'revisar_antes')
    if personal_data and 'GDPR_DPIA' in missing_requirements:
        decision = subir(decision, 'publicar_con_condiciones')
    if evidence_age_days is not None and evidence_age_days > 120:
        decision = subir(decision, 'publicar_con_condiciones')
    if provider_exit_missing:
        decision = subir(decision, 'publicar_con_condiciones')
    return decision

```

## Criterio de diseño

- Las reglas bloqueantes deben ser pocas, explícitas y defendibles.
- Las condiciones deben tener owner, fecha y evidencia esperada.
- Cada excepción debe quedar documentada con `system_id`, versión y motivo.
- Si cambia modelo, prompt, RAG, tool, finalidad o proveedor, se repite el gate.
