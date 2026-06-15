# UX contract

Este documento convierte una función de IA en una experiencia revisable. No describe estilo visual. Describe estados, evidencia, acciones, recuperación, accesibilidad, trazas y criterios de salida.

## 1. Función

**Nombre de la función:**  

**Usuario principal:**  

**Tarea que ayuda a completar:**  

**Acción máxima permitida:**  
<!-- Ejemplo: redactar, proponer, consultar, preparar payload, ejecutar con aprobación. -->

**Acciones que no puede realizar:**  

## 2. Estados visibles

| state_id | Qué ve la persona | Entrada | Salida | Acciones permitidas | Acciones bloqueadas | Trace event |
|---|---|---|---|---|---|---|
| preparing |  |  |  |  |  | ux.state.preparing |
| retrieving_evidence |  |  |  |  |  | ux.state.retrieving_evidence |
| insufficient_evidence |  |  |  |  |  | ux.state.insufficient_evidence |
| approval_pending |  |  |  |  |  | ux.state.approval_pending |
| manual_fallback |  |  |  |  |  | ux.state.manual_fallback |

## 3. Evidencia y límites

| Resultado | Evidencia visible | Límite visible | Qué no debe prometer |
|---|---|---|---|
| Respuesta sustentada |  |  |  |
| Respuesta parcial |  |  |  |
| Abstencion |  |  |  |
| Error recuperable |  |  |  |

## 4. Tarjeta de aprobación

**Acción propuesta:**  

**Sistema afectado:**  

**Objeto afectado:**  

**Motivo de la propuesta:**  

**Evidencias que debe ver la persona:**  

**Payload editable:**  

```json
{
  "action": "",
  "object_id": "",
  "fields_to_change": {}
}
```

**Permisos requeridos:**  

**Opciones de recuperación:**  

- [ ] Editar payload.
- [ ] Pedir más evidencia.
- [ ] Escalar revisión.
- [ ] Cancelar.
- [ ] Continuar manualmente.

## 5. Copy de límites

| Situación | Copy exacto que verá la persona | Siguiente paso |
|---|---|---|
| Evidencia suficiente |  |  |
| Evidencia incompleta |  |  |
| Baja confianza |  |  |
| Permiso pendiente |  |  |
| Error recuperable |  |  |

## 6. Accesibilidad

- [ ] La acción principal tiene verbo y objeto explícitos.
- [ ] La pantalla se puede operar con teclado.
- [ ] El foco visible no se pierde al cambiar de estado.
- [ ] Los errores tienen siguiente paso.
- [ ] Las fuentes y límites no dependen solo del color.
- [ ] Hay alternativa manual.

## 7. Medición

| Escenario | Tarea | Señal de éxito | Señal de recuperación | Gate |
|---|---|---|---|---|
| Evidencia completa |  |  |  |  |
| Fuente incompleta |  |  |  |  |
| Permiso pendiente |  |  |  |  |
| Error recuperable |  |  |  |  |
| Caso fuera de alcance |  |  |  |  |

## 8. Decisión UX

**Estado del gate:**  
<!-- pass, review, block. -->

**Cambios obligatorios antes del piloto:**  

1. 
2. 
3. 

**Condición de retirada por UX:**  

**Responsable de revisar el contrato:**  
