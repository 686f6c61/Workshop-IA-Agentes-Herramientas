# Decisión C08: Motor de permisos

Estado: `valid`.

## Evidencias

- OK: acciones clasificadas. No todas las tools tienen el mismo riesgo.
- OK: escrituras con aprobación. El modelo no ejecuta efectos externos sin revisión.
- OK: cola de aprobación no vacía. El sistema separa decisión y ejecución.
- OK: lectura privada exige autenticación. Privacidad no es un comentario, es una regla.

## Qué te llevas

Un motor de permisos con cola de aprobación para acciones con efecto.

## Decisión

La autonomía queda graduada: leer, escribir y enviar no comparten permisos ni la misma ruta de aprobación.
