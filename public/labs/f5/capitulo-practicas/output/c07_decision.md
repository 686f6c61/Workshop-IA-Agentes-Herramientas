# Decisión C07: Contrato antes del SDK

Estado: `valid`.

## Evidencias

- OK: contrato portable. La app habla su idioma antes del SDK.
- OK: eventos normalizados. Las trazas se comparan entre proveedores.
- OK: tres familias cubiertas. OpenAI, Anthropic y ADK se tratan como adaptadores.
- OK: no delega permisos al SDK. La política vive fuera del proveedor.

## Qué te llevas

Un contrato portable antes de acoplarte a un SDK concreto.

## Decisión

La integración es portable: se puede cambiar proveedor sin reescribir política, salida esperada ni evaluación de eventos.
