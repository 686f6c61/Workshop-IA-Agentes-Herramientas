# Práctica F4 C08

Estado: `valid`.

El filtro evita que contenido antiguo gane por parecido superficial.

## Qué te llevas

Un ejemplo de búsqueda híbrida con filtro para evitar documentos antiguos pero parecidos.

## Evidencia

```json
{
  "status": "valid",
  "summary": "El filtro evita que contenido antiguo gane por parecido superficial.",
  "query": "moodle mfa acceso",
  "filter": {
    "year": 2026,
    "active": true
  },
  "dense": [
    [
      "doc-01",
      0.6550169061016156
    ],
    [
      "doc-02",
      0.09458856551293483
    ]
  ],
  "lexical": [
    [
      "doc-01",
      2
    ],
    [
      "doc-02",
      0
    ]
  ],
  "hybrid": [
    [
      "doc-01",
      0.03278688524590164
    ],
    [
      "doc-02",
      0.03225806451612903
    ]
  ],
  "what_you_take": "Un ejemplo de búsqueda híbrida con filtro para evitar documentos antiguos pero parecidos."
}
```
