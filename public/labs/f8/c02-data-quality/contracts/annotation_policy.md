# Politica de anotación: soporte académico

Esta política define como asignar etiquetas al dataset del capítulo.

## Etiquetas permitidas

| Etiqueta | Se usa cuando | No se usa cuando |
|---|---|---|
| `answer` | El caso contiene información suficiente para responder con evidencia. | Falta un dato clave o hay una decisión administrativa excepcional. |
| `ask_more` | La consulta está incompleta y hace falta pedir un dato concreto. | La respuesta se puede dar con la información disponible. |
| `escalate` | El caso requiere revisión de una persona o equipo responsable. | Solo falta una aclaración sencilla del usuario. |

## Casos frontera

| Situacion | Etiqueta preferida | Razon |
|---|---|---|
| El usuario pregunta por una beca, pero no indica convocatoria. | `ask_more` | La acción correcta es pedir convocatoria o curso. |
| El usuario reclama un pago duplicado. | `escalate` | Puede requerir comprobación administrativa. |
| El usuario pregunta un plazo publicado y vigente. | `answer` | Hay evidencia suficiente. |
| El usuario mezcla dos tramites distintos. | `ask_more` | Primero hay que separar la intencion. |

## Proceso de revisión

1. Dos personas anotan una muestra comun.
2. Se calcula acuerdo observado y kappa.
3. Los desacuerdos pasan a cola de revisión.
4. Se decide si la política estaba incompleta o si una etiqueta fue un error.
5. Se actualiza la política antes de reetiquetar en lote.

## Regla de desempate

Si una respuesta podría ser `answer` o `ask_more`, se elige `ask_more` cuando la respuesta sin aclaración pueda inducir una decisión equivocada.

Si una respuesta podría ser `ask_more` o `escalate`, se elige `escalate` cuando el siguiente paso dependa de una comprobación externa al asistente.
