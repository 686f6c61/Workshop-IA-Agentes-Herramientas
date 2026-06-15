# Revisión inicial de privacidad: Asistente académico con RAG y revisión humana

Esta revisión es deliberadamente mínima. Su función es abrir preguntas técnicas antes de hacer una DPIA completa cuando aplique.

## Datos tratados

- Clases declaradas: `documentos_publicos`, `normativa_interna`, `tickets_seudonimizados`, `trazas_operativas`.
- La práctica asume seudonimización para tickets y trazas.
- La práctica no conserva texto bruto de usuario en la traza de muestra.

## Preguntas obligatorias

1. ¿Qué dato personal entra en prompt, RAG, memoria, logs y proveedor?
2. ¿Qué dato se conserva y durante cuánto tiempo?
3. ¿Qué dato se puede borrar sin romper observabilidad?
4. ¿Qué finalidad justifica cada dato?
5. ¿Qué owner revisa excepciones?

## Decisión provisional

No subiría de fase sin revisar retención, seudonimización, muestreo de trazas y rutas de borrado.
