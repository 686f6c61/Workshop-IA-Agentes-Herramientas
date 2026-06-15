# Decisión C01: Manifest operativo de agente

Estado: `valid`.

## Evidencias

- OK: manifest declara objetivo. El objetivo se puede revisar sin leer código.
- OK: tools tienen permisos. Cada herramienta declara su permiso.
- OK: acciones persistentes requieren aprobación. La escritura no queda en manos del modelo.
- OK: hay presupuesto operativo. La autonomía tiene límite medible.
- OK: memoria separa contexto, sesión y persistencia. La memoria no se confunde con prompt largo.

## Qué te llevas

Un manifest de agente con objetivo, memoria, tools, permisos, presupuesto y reglas de parada.

## Decisión

El agente puede pasar de idea a diseño: tiene objetivo, tools, permisos, memoria y presupuesto antes de escribir una integración real.
