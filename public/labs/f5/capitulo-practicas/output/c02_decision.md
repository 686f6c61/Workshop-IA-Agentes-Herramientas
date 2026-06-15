# Decisión C02: Bucle estado-acción-observación

Estado: `valid`.

## Evidencias

- OK: hay trayectoria. La práctica no evalúa solo respuesta final.
- OK: cada paso tiene acción y observación. El bucle agente es observable.
- OK: la parada es explícita. La run no queda abierta por inercia.
- OK: presupuesto respetado. El agente no tiene autonomía infinita.

## Qué te llevas

Una trayectoria estado-acción-observación que permite depurar una run.

## Decisión

El bucle es apto para enseñar agentes: cada acción produce una observación, consume presupuesto y termina por regla.
