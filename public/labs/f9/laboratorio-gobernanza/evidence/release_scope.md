# Alcance del piloto

## Sistema principal

`admissions_prioritization_helper`

## Alcance permitido

- Fase: piloto interno.
- Uso: preparar una priorización revisable para el equipo de admisiones.
- Decisión final: siempre humana.
- Tools permitidas: lectura de políticas y preparación de explicación.
- Tools no disponibles en piloto: publicación de ranking, actualización de expediente, notificación.

## Condiciones de salida

1. Record-keeping exportable conectado al pipeline.
2. Identidad de agente trazable en cada run.
3. Credenciales con TTL y scopes limitados.
4. Separación entre preparar y ejecutar.
5. Plan de rollback y thresholds operativos.
6. Decisión de retención cerrada por privacidad.
