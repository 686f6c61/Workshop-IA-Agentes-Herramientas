# Runbook: high burn rate en sistema de IA

## Cuándo se activa

Este runbook se activa cuando el presupuesto de error se consume demasiado rápido. En el kit, la alerta se dispara desde `ops/ai/observability.yaml` cuando el coste, la latencia o la tasa de error del sistema superan el umbral definido para la ventana de observación.

## Qué mirar primero

1. Revisa `output/c04_report.json` y confirma qué SLI está quemando presupuesto: latencia, coste, errores de contrato o fallos de proveedor.
2. Comprueba si el cambio coincide con una nueva `model_version`, `prompt_version`, política de routing o despliegue de herramienta.
3. Separa síntoma de causa: una subida de coste puede venir de más tokens, más reintentos, peor cache, modelos más caros o más llamadas a herramientas.

## Acciones de contención

1. Congela cambios de prompt/modelo hasta cerrar la investigación.
2. Activa el fallback de menor coste si existe y no viola el contrato de calidad.
3. Reduce concurrencia o desactiva rutas no críticas si la latencia compromete el SLO.
4. Abre una decisión técnica con responsable, ventana afectada, métrica, hipótesis y rollback aplicado.

## Criterio de cierre

El incidente se cierra cuando el SLI vuelve bajo el umbral, el burn rate deja de crecer, queda registrada la causa probable y se añade al menos una prueba o alerta que detecte antes el mismo patrón.
