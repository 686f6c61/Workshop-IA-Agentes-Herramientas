# Plan de limpieza

Estado del gate: **block**.

## Primero: bloquear uso automatizado

No entrenes, no publiques una eval y no indexes este snapshot mientras existan fallos de bloqueo.

## Fallos de bloqueo

- `case_id_unique`
- `product_values`
- `label_values`
- `pii_risk_values`
- `license_compatibility`
- `exact_cross_split_duplicates`
- `near_cross_split_duplicates`

## Revisiones necesarias

- `label_review_queue`
- `annotator_agreement`

## Orden recomendado

1. Corregir schema, valores fuera de catalogo y licencias incompatibles.
2. Separar o eliminar duplicados que cruzan splits.
3. Abrir `label_review_queue.csv` y revisar cada etiqueta con la política de anotación.
4. Recalcular kappa tras la revisión.
5. Reejecutar el gate y guardar el nuevo reporte.
