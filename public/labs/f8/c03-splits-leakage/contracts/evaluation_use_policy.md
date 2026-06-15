# Politica de uso de evaluación

Este documento define que se puede hacer con cada partición. Si cambia está política, hay que regenerar `output/split_manifest.json` y volver a justificar la decisión.

## Principio

El split no es solo una carpeta de datos. Es un contrato operativo. Cada partición tiene permisos distintos:

| Split | Se puede usar para | No se debe usar para |
|---|---|---|
| `train` | Entrenar, ajustar transformadores, crear vocabularios, construir ejemplos de desarrollo. | Medir la calidad final. |
| `validation` | Elegir modelo, prompt, umbral, chunking, retriever o configuracion. | Publicar una metrica como resultado final. |
| `test` | Medir una decisión ya cerrada. | Tomar decisiones de diseño después de mirar el resultado. |
| `holdout` | Comprobar una conclusion importante antes de comunicarla fuera del equipo. | Iterar hasta que el resultado mejore. |

## Regla de degradación

Si se mira `test` para elegir una opcion, ese `test` pasa a comportarse como `validation`. No hay drama, pero hay que decirlo. La salida correcta es reservar un nuevo holdout o crear una nueva versión de evaluación.

## Registro mínimo

Antes de publicar resultados, guarda:

1. Dataset y hash.
2. Politica y hash.
3. Estrategia de split.
4. Fecha de generacion.
5. IDs por split.
6. Fallos bloqueantes y fallos en revisión.
7. Persona o equipo responsable.

El archivo `output/split_manifest.json` contiene está información para el kit.
