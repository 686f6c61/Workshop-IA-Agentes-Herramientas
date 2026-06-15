# Memo de decisión técnica

## Decisión

`revisar_antes`.

## Motivo principal

El sistema `admissions_prioritization_helper` tiene el control `recordkeeping_export` en estado `block`. No basta con tener una idea de trazabilidad: hay que poder exportar una traza revisable que conecte modelo, prompt, RAG, tools, política, agente, decisión y condiciones.

## Primer owner

`owner-platform`.

## Evidencia que debe cerrar el bloqueo

`evidence/recordkeeping_contract.json` debe conectarse con una muestra real de trazas exportadas para el sistema de admisiones.

## Condiciones que siguen abiertas

- Decisión formal de retención.
- Separacion real entre `prepare` y `execute`.
- Identidad de agente y credenciales acotadas.
- FRIA/precheck.
- Rollback y thresholds operativos.

## Decisión profesional

No se amplia el alcance del piloto hasta cerrar el bloqueo, repetir el gate y conservar el diff de evidencias.
