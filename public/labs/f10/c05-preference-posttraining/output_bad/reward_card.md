# Reward card / preference card

Snapshot: `pref_dataset_2026_06_08`
Estado: `block`

## Senal

Pares de preferencia `prompt/chosen/rejected` con razon de preferencia, rubric scores, acuerdo y verificador cuando existe.

## Cobertura

- Pares: 6
- Familias de tarea: 5
- Cobertura de verificador: 0.5
- Acuerdo medio: 0.411667
- Margen medio chosen-rejected: -0.351667

## Riesgos conocidos

- La recompensa es una aproximacion de preferencia, no una prueba de verdad.
- Los pares sin verificador requieren revision humana retenida.
- Si cambia la rubrica, este snapshot debe auditarse de nuevo.
- El entrenamiento posterior debe compararse contra prompt baseline y SFT.

## Decision

No debe pasar a entrenamiento hasta corregir los checks fallidos.
