# Decisión C03: Contrato operativo de tool

Estado: `valid`.

## Evidencias

- OK: schema de entrada completo. La tool no acepta texto libre como contrato.
- OK: schema de salida completo. La observación vuelve estructurada.
- OK: permiso explícito. La tool declara su frontera de acceso.
- OK: errores nombrados. El agente puede distinguir fallo de negocio y fallo técnico.
- OK: trazas nombradas. La ejecución se puede reconstruir.

## Qué te llevas

Un contrato de tool con schema, permiso, errores, timeout y eventos de traza.

## Decisión

La tool puede integrarse en un agente: no depende de una descripción bonita, sino de schema, permisos, errores y trazas.
