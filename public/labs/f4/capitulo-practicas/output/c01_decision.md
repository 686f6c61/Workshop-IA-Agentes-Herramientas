# Práctica F4 C01

Estado: `valid`.

RAG gana porque el conocimiento vivo pesa más que actuar fuera.

## Qué te llevas

Una matriz para decidir si usar prompt/schema, RAG, tool, ajuste, modelo local o mezcla.

## Evidencia

```json
{
  "status": "valid",
  "summary": "RAG gana porque el conocimiento vivo pesa más que actuar fuera.",
  "input_case": {
    "conocimiento_vivo": 5,
    "accion_externa": 0,
    "formato": 3,
    "conducta_repetida": 2,
    "privacidad_local": 4,
    "coste": 3
  },
  "ranking": [
    [
      "rag",
      56
    ],
    [
      "tool",
      52
    ],
    [
      "modelo_local",
      47
    ],
    [
      "ajuste_lora",
      45
    ],
    [
      "prompt_schema",
      38
    ]
  ],
  "what_you_take": "Una matriz para decidir si usar prompt/schema, RAG, tool, ajuste, modelo local o mezcla."
}
```
