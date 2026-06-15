# UX contract

## 1. Función

**Nombre de la función:** `matricula_rag_assistant`.

**Usuario principal:** personal académico que revisa solicitudes de matrícula.

**Tarea que ayuda a completar:** recuperar normativa, revisar expediente, redactar respuesta sustentada y escalar casos incompletos.

**Acción máxima permitida:** redactar y proponer siguiente paso. No ejecuta cierre de solicitud.

**Acciones que no puede realizar:** cerrar expediente, modificar pagos, enviar respuesta final sin revisión, consultar sistemas sin permiso.

## 2. Estados visibles

| state_id | Qué ve la persona | Entrada | Salida | Acciones permitidas | Acciones bloqueadas | Trace event |
|---|---|---|---|---|---|---|
| preparing | "Preparando revisión de solicitud." | Pregunta válida. | Permisos comprobados. | Cancelar, editar pregunta. | Enviar respuesta. | ux.state.preparing |
| retrieving_evidence | "Buscando normativa y expediente." | Permisos de lectura OK. | Fuentes recuperadas o insuficientes. | Limitar fuente, cancelar. | Cerrar solicitud. | ux.state.retrieving_evidence |
| insufficient_evidence | "Falta evidencia para responder con seguridad." | Menos de dos fuentes válidas. | Documento aportado o revisión escalada. | Aportar documento, escalar, continuar manualmente. | Generar respuesta final. | ux.state.insufficient_evidence |
| approval_pending | "Revisa el texto y el siguiente estado antes de continuar." | Respuesta sustentada con acción propuesta. | Aprobación, edición o rechazo. | Editar payload, aprobar, cancelar. | Ejecutar sin trace_id. | ux.state.approval_pending |
| manual_fallback | "Continúa por el flujo manual conservando trazas." | Error recuperable o caso fuera de alcance. | Tarea derivada. | Abrir checklist manual, guardar notas. | Reintentos infinitos. | ux.state.manual_fallback |

## 3. Evidencia y límites

| Resultado | Evidencia visible | Límite visible | Qué no debe prometer |
|---|---|---|---|
| Respuesta sustentada | Normativa, expediente y registro consultado. | No se ha consultado contabilidad central. | Que la respuesta sea cierre definitivo. |
| Respuesta parcial | Fuente recuperada y hueco concreto. | Falta justificante o permiso. | Que la conclusión sea completa. |
| Abstencion | Motivo de falta de fuente. | No hay evidencia suficiente. | Inventar respuesta para avanzar. |
| Error recuperable | Servicio que no respondió y trace_id. | No se pudo validar estado de pagos. | Que la consulta se completó. |

## 4. Tarjeta de aprobación

**Acción propuesta:** guardar respuesta revisada y marcar solicitud como `revision_humana`.

**Sistema afectado:** gestor interno de solicitudes.

**Objeto afectado:** `solicitud-2026-1042`.

**Motivo de la propuesta:** la normativa recuperada cubre la pregunta, pero el justificante de pago requiere revisión humana.

**Evidencias que debe ver la persona:** sección de normativa de pagos pendientes, expediente de solicitud, timestamp de retrieval y límite de contabilidad no consultada.

**Payload editable:**

```json
{
  "action": "guardar_respuesta_revisada",
  "object_id": "solicitud-2026-1042",
  "fields_to_change": {
    "response_text": "Antes de cerrar la solicitud, revise el justificante subido el 03/06.",
    "next_status": "revision_humana"
  }
}
```

**Permisos requeridos:** `role:coordinacion_academica`, `trace_id`, evidencia visible y política de retención aplicada.

**Opciones de recuperación:**

- [x] Editar payload.
- [x] Pedir más evidencia.
- [x] Escalar revisión.
- [x] Cancelar.
- [x] Continuar manualmente.

## 5. Copy de límites

| Situación | Copy exacto que verá la persona | Siguiente paso |
|---|---|---|
| Evidencia suficiente | "Respuesta basada en normativa 2026 y expediente. Revísala antes de guardar." | Editar o guardar como respuesta revisada. |
| Evidencia incompleta | "Falta una fuente que confirme el estado del pago." | Adjuntar documento o escalar. |
| Baja confianza | "La evidencia recuperada no cubre toda la pregunta. Te muestro opciones, no una conclusión final." | Elegir opción o flujo manual. |
| Permiso pendiente | "Para consultar pagos necesitas permiso de coordinación." | Solicitar permiso o continuar sin esa fuente. |
| Error recuperable | "No se pudo consultar pagos. Puedes reintentar, continuar manualmente o guardar como pendiente." | Reintentar una vez o derivar. |

## 6. Accesibilidad

- [x] La acción principal tiene verbo y objeto explícitos.
- [x] La pantalla se puede operar con teclado.
- [x] El foco visible no se pierde al cambiar de estado.
- [x] Los errores tienen siguiente paso.
- [x] Las fuentes y límites no dependen solo del color.
- [x] Hay alternativa manual.

## 7. Medición

| Escenario | Tarea | Señal de éxito | Señal de recuperación | Gate |
|---|---|---|---|---|
| Evidencia completa | Redactar respuesta sustentada. | Identifica fuentes y límite. | Puede editar antes de guardar. | pass |
| Fuente incompleta | No forzar respuesta. | Entiende qué falta. | Aporta documento o escala. | pass |
| Permiso pendiente | Revisar tarjeta de aprobación. | Distingue sugerencia y acción. | Rechaza o edita payload. | pass |
| Error recuperable | Completar tarea sin perder contexto. | Ve servicio afectado y trace_id. | Continúa manualmente. | review |
| Caso fuera de alcance | Derivar correctamente. | No recibe promesa falsa. | Escala con motivo. | pass |

## 8. Decisión UX

**Estado del gate:** `review`.

**Cambios obligatorios antes del piloto:**

1. Mostrar evidencia visible también en el escenario de error recuperable.
2. Asegurar que el error recuperable puede terminar en éxito de tarea mediante flujo manual.
3. Registrar `ux.state.manual_fallback` con `trace_id` y motivo.

**Condición de retirada por UX:** si dos ventanas consecutivas pierden evidencia visible, recuperación o separación entre sugerencia y acción, se detiene el piloto.

**Responsable de revisar el contrato:** producto, UX, ingeniería y operación académica.
