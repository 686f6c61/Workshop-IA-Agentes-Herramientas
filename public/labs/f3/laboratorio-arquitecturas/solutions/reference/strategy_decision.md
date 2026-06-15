# Decisión de arquitectura

Decisión: `rag_local_o_controlado`.

## Scorecard

| Opción | Puntuación ponderada |
|---|---:|
| `rag_local_o_controlado` | 4.45 |
| `fine_tuning_mensual` | 2.2 |
| `api_prompt_largo` | 2.15 |

## Por qué

La normativa cambia y las respuestas deben citar documentos. Por eso conviene separar conocimiento vivo y pesos del modelo: documentos en RAG, modelo para leer, sintetizar y responder con evidencia.

Fine-tuning puede ayudar a formato o estilo, pero no es la primera herramienta para mantener conocimiento que cambia varias veces al año. El prompt largo sirve para prototipo, pero encarece contexto y mezcla demasiadas responsabilidades.

## Evaluación mínima

- `respuesta_correcta`
- `cita_correcta`
- `abstencion`
- `latencia`
- `coste`
