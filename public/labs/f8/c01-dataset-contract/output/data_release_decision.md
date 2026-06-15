# Decisión de datos

Estado: **pass**.

## Lectura

Este dataset puede usarse como material didactico porque tiene contrato, schema esperado, splits definidos, licencias compatibles, linaje por fila y hashes reproducibles.
Antes de usar datos reales, el contrato debería ampliarse con fuentes originales, política de retención, revisión de etiquetas, evaluación por slices y propietario operativo.

## Checks

- `schema_columns`: pasa — {'missing_columns': [], 'extra_columns': []}
- `case_id_unique`: pasa — {'duplicate_case_ids': []}
- `split_values`: pasa — {'invalid_splits': []}
- `label_values`: pasa — {'invalid_labels': []}
- `missing_rate`: pasa — {'missing_rate': 0.0, 'missing_by_column': {}}
- `split_minimums`: pasa — {}
- `label_minimums`: pasa — {}
- `license_compatibility`: pasa — {'license_mismatches': []}
- `pii_risk_allowed`: pasa — {'invalid_pii_risk_values': []}
- `lineage_complete`: pasa — {'lineage_missing': []}
- `duplicate_text_across_splits`: pasa — {'duplicates': []}
