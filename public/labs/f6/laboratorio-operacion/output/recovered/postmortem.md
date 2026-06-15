# Postmortem técnico

## Resumen

Estado final del drill: `recovered`.

## Evidencia preservada

- métricas por release y ruta.
- trace_id con modelo, prompt, ruta e índice.
- muestra de respuestas con citas.
- decisión de canary y rollback.
- caso de regresión generado.

## Acciones

1. Añadir regresión RAG para la pregunta afectada.
2. Revisar dashboard de cola por release.
3. Ensayar rollback de índice en ventana controlada.
