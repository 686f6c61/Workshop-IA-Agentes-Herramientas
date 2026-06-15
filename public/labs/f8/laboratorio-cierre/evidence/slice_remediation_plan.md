# Plan de corrección por slices

## Slices críticos del laboratorio

| Slice | Motivo | Evidencia que exige |
|---|---|---|
| `language=en` | Casos en ingles concentran miss rate alto. | Revision de datos, instrucciones, cobertura documental y test por idioma. |
| `segment=practicas` | Segmento con vocabulario y reglas propias. | Corpus revisado, ejemplos etiquetados y metrica por segmento. |
| `source=form` | Entrada desde formulario tiene distribución distinta. | Validación de campos, normalizacion y control de calidad de fuente. |

## Criterio de cierre

Un slice no se cierra por mejorar la media global. Se cierra cuando el miss rate del slice baja del umbral declarado o cuando se limita explicitamente el alcance del sistema.

## Siguiente paso

Proponer una intervencion medible para `segment=practicas` y `language=en`, conectada con el kit de experimentos del capítulo 07.
