# Práctica F4 C11

Estado: `valid`.

Agentic RAG complica solo cuando necesita varias rutas de evidencia.

## Qué te llevas

Un plan pequeño de Agentic RAG/GraphRAG con evidencias combinadas.

## Evidencia

```json
{
  "status": "valid",
  "summary": "Agentic RAG complica solo cuando necesita varias rutas de evidencia.",
  "question": "compara beca pendiente y pago vencido para ampliar matrícula",
  "plan": [
    "descomponer",
    "buscar_texto",
    "buscar_grafo",
    "evaluar_evidencia",
    "responder_con_citas"
  ],
  "graph_hits": [
    [
      "beca pendiente",
      "no bloquea",
      "ampliación"
    ],
    [
      "pago vencido",
      "bloquea",
      "ampliación"
    ]
  ],
  "what_you_take": "Un plan pequeño de Agentic RAG/GraphRAG con evidencias combinadas."
}
```
