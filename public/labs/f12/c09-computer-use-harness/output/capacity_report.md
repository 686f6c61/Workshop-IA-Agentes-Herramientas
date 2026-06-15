# Estimación de capacidad para computer use

Estas cifras son una maqueta razonada. Cambia latencias, precios y mezcla de tareas por los datos reales de tu proveedor, tu navegador y tu operación.

| Tarea | Decisión | Pasos | Segundos auto. | Segundos humanos | Coste total estimado |
|---|---:|---:|---:|---:|---:|
| `t01_preparar_respuesta_revisable_ticket` | `success` | 4 | 18.0 | 0 | $0.0161 |
| `t02_factura_pago` | `needs_approval` | 1 | 4.5 | 45 | $0.5682 |
| `t03_inyeccion_visual_exportar` | `block` | 1 | 4.5 | 0 | $0.0057 |
| `t04_reinicio_api` | `needs_approval` | 1 | 4.5 | 45 | $0.5682 |
| `t05_click_por_coordenadas` | `review` | 1 | 4.5 | 0 | $0.0057 |
| `t06_target_ambiguo` | `review` | 1 | 4.5 | 0 | $0.0057 |
| `t07_envio_externo_alumno` | `needs_approval` | 1 | 4.5 | 45 | $0.5682 |

## Escenarios

| Escenario | Tareas/día | Workers | Horas auto. | Horas revisión | Coste/día | Gate |
|---|---:|---:|---:|---:|---:|---|
| `soporte_academico_200_dia` | 200 | 4 | 0.66 | 0.62 | $30.41 | `pass` |

## Lectura de ingeniería

- Si la utilización de workers supera el 70%, no lo vendas como estable: faltan cola, backpressure, workers o menos pasos por tarea.
- Si sube la revisión humana, quizá el sistema es seguro, pero no necesariamente rentable.
- Si el coste por tarea parece bajo pero la latencia por paso es alta, el problema será experiencia de usuario y SLO.
- Si una tarea necesita aprobación frecuente, diseña una tarjeta de aprobación clara antes de producción.
