# Threshold calibration

Esta recomendacion prioriza reducir falsos pases. Si tu dominio prefiere no bloquear respuestas utiles, cambia el criterio y vuelve a ejecutar el script.

| Slice | Threshold | Precision | Recall | Falsos pases | Falsos bloqueos | Casos a revisar |
|---|---:|---:|---:|---:|---:|---|
| `all` | 0.65 | 1.0 | 0.666667 | 0 | 3 | rag_sin_fuente;sensibilidad_evidencia;sql_ejecutable |
| `coste` | 0.7 | 1.0 | 1.0 | 0 | 0 | none |
| `herramientas` | 0.65 | 1.0 | 1.0 | 0 | 0 | none |
| `privacidad` | 0.65 | 1.0 | 1.0 | 0 | 0 | none |
| `rag` | 0.6 | 1.0 | 1.0 | 0 | 0 | none |
| `salida_estructurada` | 0.7 | 1.0 | 1.0 | 0 | 0 | none |
| `sql` | 0.6 | 1.0 | 1.0 | 0 | 0 | none |
