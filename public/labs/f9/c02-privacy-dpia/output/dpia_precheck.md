# Prechequeo EIPD/DPIA

Una EIPD/DPIA es una evaluación previa cuando un tratamiento puede implicar alto riesgo para derechos y libertades. Este prechequeo no decide por la organización: detecta señales que justifican una revisión formal.

| Flujo | Señales detectadas | Lectura técnica |
|---|---|---|
| `F-001` | `large_scale`, `cross_border_third_party` | El tratamiento se plantea a escala alta o recurrente. Hay proveedor o transferencia internacional que debe revisarse. |
| `F-002` | `large_scale`, `long_retention_raw_text` | El tratamiento se plantea a escala alta o recurrente. Se conserva texto bruto durante una ventana larga. |
| `F-003` | `large_scale`, `cross_border_third_party`, `long_retention_raw_text` | El tratamiento se plantea a escala alta o recurrente. Hay proveedor o transferencia internacional que debe revisarse. Se conserva texto bruto durante una ventana larga. |
| `F-006` | `special_category`, `large_scale`, `cross_border_third_party`, `model_training_personal_data`, `long_retention_raw_text` | Hay categorías especiales o datos muy sensibles. El tratamiento se plantea a escala alta o recurrente. Hay proveedor o transferencia internacional que debe revisarse. Se pretende usar datos personales para entrenar o ajustar el modelo. Se conserva texto bruto durante una ventana larga. |

## Qué documentaría antes de publicar

1. Naturaleza, alcance, contexto y fines del tratamiento.
2. Categorías de datos y personas afectadas.
3. Flujos hacia proveedores, tools, memoria, logs y backups.
4. Medidas de minimización, seudonimización, cifrado, retención y borrado.
5. Cómo se atienden acceso, rectificación, supresión, oposición y limitación.
6. Riesgo residual y owner que acepta o bloquea el uso.
