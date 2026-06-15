# Decisión de calibración

Estado del gate: **pasa**.

## Política recomendada

- `low`: 0.15
- `high`: 0.75
- tasa de revisión: 0.4444
- cobertura automática: 0.5556
- error automático: 0.15 con intervalo Wilson 95 % `[0.0524, 0.3604]`
- coste estimado: 18.8

## Evidencia mínima

- ECE bruto: 0.0911
- ECE calibrado: 0.0526
- Brier bruto: 0.1773
- Brier calibrado: 0.173
- hash dataset: `01d8033ef36e`
- hash política: `b85a3e0e72f8`

## Lectura operativa

Automatiza solo fuera de la zona gris y conserva revisión cuando el conjunto conformal no permite una clase única.
Si cambia el modelo, el prompt, el retrieval, el dominio o la mezcla de tickets, recalibra antes de conservar estos umbrales.
