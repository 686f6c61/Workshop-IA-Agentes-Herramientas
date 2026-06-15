# Decisión técnica: eventos RL

Estado: `block`

Eventos revisados: 4
Episodios revisados: 3
Snapshot hash: `38f7765b720dd759989600f245390bec8a1c9641663352cec89ce35bae6a13ff`

## Interpretación

El snapshot queda bloqueado. No debería usarse para entrenamiento ni comparación de políticas hasta corregir errores.

## Checks principales

- shape_ok: `False`
- episodes_ok: `False`
- coverage_ok: `False`
- warnings_ok: `True`

## Retornos por episodio

- `bad_case_001`: 2.3
- `bad_case_002`: -0.1
- `bad_case_003`: -0.1

## Cobertura que exige revisión

- `ticket_nuevo -> pedir_dato` tiene 0 eventos; mínimo esperado 1.
- `ticket_con_evidencia -> escalar_revision` tiene 0 eventos; mínimo esperado 1.

## Qué cambiaría en un proyecto real

1. Aumentaría cobertura en parejas estado-acción críticas antes de automatizar más.
2. Guardaría este reporte junto al snapshot que alimente evaluación o entrenamiento.
3. Convertiría cada error repetido en un test de CI del pipeline de datos.
