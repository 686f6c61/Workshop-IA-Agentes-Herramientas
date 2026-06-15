# Práctica F4 C09

Estado: `valid`.

RAG mínimo: recuperar, citar o abstenerse.

## Qué te llevas

Un mini RAG que recupera, cita o se abstiene.

## Evidencia

```json
{
  "status": "valid",
  "summary": "RAG mínimo: recuperar, citar o abstenerse.",
  "traces": [
    {
      "question": "cuando se solicita ampliación",
      "gold": [
        "norm#1"
      ],
      "retrieved": [
        "norm#1"
      ],
      "abstain": false,
      "ok": true
    },
    {
      "question": "puedo ampliar con pagos vencidos",
      "gold": [
        "norm#2"
      ],
      "retrieved": [
        "norm#2"
      ],
      "abstain": false,
      "ok": true
    },
    {
      "question": "cual es el teléfono del rectorado",
      "gold": [],
      "retrieved": [],
      "abstain": true,
      "ok": true
    }
  ],
  "what_you_take": "Un mini RAG que recupera, cita o se abstiene."
}
```
