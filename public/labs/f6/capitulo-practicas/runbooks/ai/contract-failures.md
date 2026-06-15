# Runbook: fallos de contrato en salidas de IA

## Cuándo se activa

Este runbook se activa cuando aumenta `contract_failed_ratio`: la salida del modelo no cumple el contrato esperado, falta un campo obligatorio, aparece un tipo incorrecto o una política exige bloquear la respuesta.

## Qué mirar primero

1. Revisa ejemplos fallidos en la traza y localiza `prompt_version`, `schema_version`, `model_version` y `tool_version`.
2. Distingue fallo de formato, fallo semántico y fallo de permisos. No se corrigen igual.
3. Comprueba si el contrato cambió sin actualizar evals, fixtures o documentación del consumidor.

## Acciones de contención

1. Bloquea la release si el contrato alimenta una acción externa, una decisión de impacto o un dato que otro sistema consumirá automáticamente.
2. Vuelve a la versión anterior de prompt o modelo si el fallo empezó con un cambio reciente.
3. Añade casos mínimos al dataset de evaluación antes de relajar el contrato.
4. Si el fallo es recuperable, devuelve una respuesta segura y registra el evento para revisión.

## Criterio de cierre

El incidente se cierra cuando el contrato vuelve a cumplirse en los casos afectados, existe una prueba de regresión y la decisión queda trazada con causa, cambio aplicado y propietario.
