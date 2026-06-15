# Decisión de búsqueda vectorial

Encoder local: `deterministic_hash_projection`.
Dimensiones: `64`.
Indice usado: `train`.
Gate: `review`.

## Lectura

La búsqueda usa un embedding denso local y similitud coseno. Es suficiente para probar contrato, top-k, metadata y errores de cobertura antes de sustituir el encoder por un modelo neural.

## Consultas

| Query | Producto esperado en top-k | Términos fuera de vocabulario | Vecinos |
|---|---|---|---|
| `q001` | True | `documentos` | `s002`, `s014`, `s007` |
| `q002` | True | `justificante`, `pendiente` | `s010`, `s006`, `s001` |
| `q003` | True | ninguno | `s011`, `s004`, `s015` |
| `q004` | True | `bloqueada` | `s005`, `s001`, `s009` |

## Siguiente mejora

Sustituye el encoder local por embeddings reales, conserva `case_id`, `split`, dimension, versión del modelo, normalizacion y metadata. Despues evalúa recall@k por producto y por canal.
