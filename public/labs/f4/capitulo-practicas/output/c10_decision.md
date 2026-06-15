# Práctica F4 C10

Estado: `valid`.

La evaluación separa retrieval, citas y soporte de afirmaciones.

## Qué te llevas

Una separación práctica entre retrieval, citas y groundedness.

## Evidencia

```json
{
  "status": "valid",
  "summary": "La evaluación separa retrieval, citas y soporte de afirmaciones.",
  "runs": [
    {
      "retrieved": [
        [
          "a",
          2
        ],
        [
          "b",
          0
        ]
      ],
      "gold": [
        "a"
      ],
      "citations": [
        "a"
      ],
      "claims_supported": true
    },
    {
      "retrieved": [
        [
          "b",
          0
        ],
        [
          "a",
          2
        ]
      ],
      "gold": [
        "a"
      ],
      "citations": [
        "b"
      ],
      "claims_supported": false
    }
  ],
  "hit_at_1": 0.5,
  "citation_precision": 0.5,
  "groundedness": 0.5,
  "what_you_take": "Una separación práctica entre retrieval, citas y groundedness."
}
```
