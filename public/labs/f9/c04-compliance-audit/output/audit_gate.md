# Gate de auditoría

Decisión global: `revisar_antes`.

| Sistema | Decisión | Bloqueantes | Condiciones |
|---|---|---:|---:|
| Asistente académico con RAG | `publicar_con_condiciones` | 0 | 1 |
| Ayuda de priorización para admisiones | `revisar_antes` | 1 | 7 |
| Asistente interno de código | `publicar_con_seguimiento` | 0 | 0 |

## Lectura operativa

No avanzar de fase en los sistemas con requisitos bloqueantes. El siguiente paso es cerrar evidencias, repetir el script y conservar el diff del paquete.

## Checklist para defender el gate

- Enseñar inventario y clasificación inicial.
- Enseñar crosswalk requisito -> evidencia.
- Abrir los huecos bloqueantes y explicar owner, fecha y criterio de cierre.
- Confirmar que cada cambio relevante reabre revisión.
- Guardar manifest como evidencia de la versión evaluada.
