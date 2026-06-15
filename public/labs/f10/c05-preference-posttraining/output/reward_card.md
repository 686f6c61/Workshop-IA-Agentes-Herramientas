# Reward card / preference card

Snapshot: `pref_dataset_2026_06_08`
Estado: `pass`

## Senal

Pares de preferencia `prompt/chosen/rejected` con razon de preferencia, rubric scores, acuerdo y verificador cuando existe.

## Cobertura

- Pares: 12
- Familias de tarea: 12
- Cobertura de verificador: 0.833333
- Acuerdo medio: 0.863333
- Margen medio chosen-rejected: 0.500833

## Riesgos conocidos

- La recompensa es una aproximacion de preferencia, no una prueba de verdad.
- Los pares sin verificador requieren revision humana retenida.
- Si cambia la rubrica, este snapshot debe auditarse de nuevo.
- El entrenamiento posterior debe compararse contra prompt baseline y SFT.

## Decision

Puede pasar a experimento controlado con eval retenida y revision de samples.
