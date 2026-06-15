# Pregunta causal

## Intervención

Enviar una plantilla guiada de respuesta al equipo de soporte antes de resolver el caso.

## Resultado

`resolved = 1` si el caso queda resuelto en la ventana observada.

## Estimando principal

Efecto medio de la intervención:

```text
ATE = E[Y(1) - Y(0)]
```

## Supuestos mínimos

1. En el experimento A/B, la asignación a `control` o `treatment` debe ser aleatoria y trazable.
2. En la muestra observacional, `prior_priority` y `historical_resolution_rate` influyen tanto en recibir acción como en resolver.
3. La muestra observacional solo permite una lectura de triage: no sustituye un experimento bien instrumentado.

## Decisión permitida

El kit permite decidir si merece la pena pasar de lectura exploratoria a experimento controlado o si un experimento ya tiene evidencia suficiente para una decisión operativa.
