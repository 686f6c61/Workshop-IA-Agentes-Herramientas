# Decisión de preprocesado

Estrategia de split usada: `time_group_holdout`.
Decisión: `block_fit_all_data`.

## Lectura

El vectorizador ajustado con todo el dataset aprende terminos que solo aparecen en validation o test. En un proyecto real, eso significa que el vocabulario ya conoce parte de los datos reservados.

| Fit | Tamano de vocabulario | Lectura |
|---|---:|---|
| Solo train | 40 | Correcto para desarrollo. |
| Todo el dataset | 56 | No usar para medir. |

## Términos que entrarian indebidamente

`abonado`, `ampliacion`, `asignada`, `asociadas`, `aula`, `bloqueada`, `confirmacion`, `convocatoria`, `justificante`, `pendiente`, `pregunta`, `recibo`, `seminario`, `sesion`, `tasas`, `ya`

## Regla operativa

Crea el split, ajusta el vectorizador con train y aplica ese mismo vectorizador a validation y test. Guarda los parámetros del vectorizador junto al manifiesto de split.
