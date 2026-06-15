# Memo de decision de datos

## Decisión

`block`.

## Motivo principal

El dataset inicial no puede sostener una publicación porque `missing_trace_rate` y `missing_required_fields_rate` son mayores que `0.0`.

## Lectura técnica

El schema existe, pero eso no basta. Una fila sin `trace_id` impide reconstruir una decisión y una fila con campos obligatorios incompletos invalida la ingesta para release.

## Siguiente paso

Corregir trazabilidad y campos obligatorios sin tocar umbrales después de ver el resultado.
