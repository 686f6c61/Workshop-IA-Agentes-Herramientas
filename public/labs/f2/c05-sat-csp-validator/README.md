# Kit F2 C05: validador SAT y CSP

Este kit acompaña el capítulo 05 del facsímil 2. Contiene dos problemas pequeños pero completos:

- Una campaña codificada como SAT.
- Una agenda codificada como CSP con restricciones duras y preferencias blandas.

El objetivo es ver la diferencia entre generar candidatos y aceptar solo soluciones verificables.

## Ejecutar

Desde esta carpeta:

```bash
python3 ops/validate_constraints.py --write
cat output/constraint_decision.md
```

Como gate:

```bash
python3 ops/validate_constraints.py --write --fail-on-invalid
```

## Archivos

| Archivo | Papel |
|---|---|
| `data/constraint_case.json` | Variables SAT, cláusulas, CSP de agenda, preferencias y candidatos. |
| `contracts/constraint_policy.json` | Condiciones esperadas para validar que el ejercicio no se ha roto. |
| `ops/validate_constraints.py` | Enumerador SAT/CSP, validador de candidatos y explicador. |
| `output/constraint_report.json` | Resultado estructurado para revisión automática. |
| `output/constraint_decision.md` | Informe legible para entregar. |

## Qué deberías mirar

1. Cuántas asignaciones prueba SAT.
2. Cuántos modelos satisfacen todas las cláusulas.
3. Qué restricciones duras eliminan horarios.
4. Por qué un candidato falla.
5. Qué agenda válida gana por coste de preferencias blandas.

## Qué entregaría un alumno

1. El Markdown generado.
2. Una cláusula SAT nueva con traducción desde lenguaje natural.
3. Una restricción CSP nueva.
4. Un candidato inválido y su explicación.
5. Una propuesta de qué reglas serían duras y cuáles blandas en un caso profesional.

## Qué te llevas

Te llevas una práctica ejecutable sobre validador SAT y CSP, con datos editables, contratos y umbrales, plantillas de entrega, código ejecutable y tests reproducibles. Trabajas con `data/constraint_case.json`, contrastas la decisión contra `contracts/constraint_policy.json` y ejecutas `ops/validate_constraints.py` para generar `output/constraint_decision.md`. La idea no es mirar una solución cerrada: es cambiar una entrada, volver a ejecutar, comparar la salida y poder defender qué harías en una revisión técnica, una asignatura o un piloto real.

## Variantes para hacerlo tuyo

- Ejecuta `make run` sin tocar nada y usa `output/constraint_decision.md` como línea base.
- Cambia o añade un caso en `data/constraint_case.json` para representar un problema de tu trabajo, clase o producto.
- Endurece una regla, umbral o campo obligatorio en `contracts/constraint_policy.json` y explica por qué el resultado debería cambiar o bloquearse.
- Compara antes/después en `output/constraint_decision.md` y `output/constraint_report.json` y escribe una decisión de una página: seguir, bloquear, medir más o cambiar el diseño.
- Completa `templates/entrega.md` con contexto, cambio, evidencia, decisión y límite; no la dejes como checklist vacía.

## Rúbrica rápida

| Nivel | Qué demuestra |
|---|---|
| Mínimo | Ejecuta `make run` y `make test`, localiza `ops/validate_constraints.py`, abre `output/constraint_decision.md` y explica qué decisión o señal produce. |
| Bueno | Cambia `data/constraint_case.json`, compara antes/después y justifica la diferencia con una evidencia concreta del output. |
| Excelente | Convierte el kit en un mini caso profesional: añade un caso propio, ajusta una regla o test, documenta el límite principal y deja una recomendación accionable para un equipo. |

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `Kit F2 C05: validador SAT y CSP`, no escondido en una ruta del repositorio.

### Qué contiene

- `README.md`: esta guía y la explicación del ejercicio.
- `Makefile`: entrada única para ejecutar y validar el kit con `make run` y `make test`.
- `requirements.txt`: dependencias declaradas; muchos kits solo usan la biblioteca estándar de Python.
- `data/`: datos de entrada o casos de prueba realistas. Ejemplos dentro del ZIP: `data/constraint_case.json`.
- `contracts/`: contratos de datos, salida, política o validación. Ejemplos dentro del ZIP: `contracts/constraint_policy.json`.
- `templates/`: plantillas editables para la entrega. Ejemplos dentro del ZIP: `templates/entrega.md`.
- `ops/`: código ejecutable del laboratorio. Ejemplos dentro del ZIP: `ops/validate_constraints.py`.
- `tests/`: tests que comprueban que el ejercicio sigue siendo reproducible. Ejemplos dentro del ZIP: `tests/test_lab_contract.py`.
- `output/`: salidas generadas o esperadas que debes revisar. Ejemplos dentro del ZIP: `output/constraint_decision.md`, `output/constraint_report.json`.

### Ejecutar desde cero

Desde la carpeta extraída del ZIP:

```bash
make run
make test
```

`make run` construye las evidencias del ejercicio. `make test` comprueba que el kit sigue siendo ejecutable después de descargarlo, extraerlo y tocarlo.

### Qué mirar antes de entregar

- `output/constraint_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/constraint_report.json`: evidencia estructurada para validar o automatizar.

### Qué entregar

Una entrega útil no es una captura de pantalla. Debe incluir los artefactos generados, la modificación razonada que hayas hecho y una decisión escrita que explique qué harías en un sistema real.

Como mínimo:

1. Resultado de `make test`.
2. Artefactos de `output/` que sostienen tu decisión.
3. Cambio propio en datos, contrato, política, plantilla o código, según el objetivo del kit.
4. Nota técnica breve: qué has probado, qué ha fallado o pasado, y qué decisión tomarías.

### Cómo adaptarlo a tu caso

1. Ejecuta primero `make run` sin tocar nada para obtener la línea base reproducible.
2. Ejecuta `make test` antes de cambiar el ejercicio; así sabes que el ZIP llegó completo.
3. Sustituye o amplía los archivos de `data/` con casos de tu dominio manteniendo el mismo contrato de campos.
4. Ajusta `contracts/` cuando cambien tipos, campos obligatorios, umbrales o catálogos permitidos.
5. Usa `templates/` como base documental; no entregues una plantilla sin completar.
6. Guarda los outputs finales y una nota breve con la decisión técnica que tomarías en un proyecto real.

### Criterio de validación

El kit está completo cuando se puede descargar, extraer, ejecutar con `make run`, validar con `make test` y explicar sin depender de ninguna carpeta externa. Si una práctica menciona código, datos, contrato, CSV, SQL, política o plantilla, ese contenido debe venir dentro del ZIP.
<!-- zip-quality-audit:end -->
