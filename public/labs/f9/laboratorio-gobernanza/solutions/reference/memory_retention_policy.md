# Politica de memoria de referencia

## Sistema

`admissions_prioritization_helper`

## Regla

- TTL: 4 horas.
- Aislamiento: caso + revisor + agente.
- Purga: al cerrar la revisión.
- Evidencia: muestra before/after de purga y hash de origen.

## Cierre

El control se cierra cuando la traza demuestra TTL, purga y ausencia de memoria compartida entre expedientes.
