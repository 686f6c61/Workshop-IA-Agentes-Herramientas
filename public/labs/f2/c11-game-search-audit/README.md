# Kit F2 C11: minimax, alfa-beta y UCT en decisiones con otro actor

Este kit acompaña el capítulo 11 del facsímil 2. Compara minimax exacto, poda alfa-beta, rollouts Monte Carlo y selección UCT sobre el mismo árbol.

El objetivo es que el alumno vea por qué el peor caso, la media simulada y el presupuesto de exploración pueden recomendar cosas distintas. En sistemas con herramientas, permisos o incentivos, eso es una decisión de ingeniería.

## Ejecutar

Desde esta carpeta:

```bash
python3 ops/audit_game_search.py --write
cat output/game_search_decision.md
```

Como gate:

```bash
python3 ops/audit_game_search.py --write --fail-on-invalid
```

## Archivos

| Archivo | Papel |
|---|---|
| `data/game_tree.json` | Árbol de decisiones, utilidades terminales, rollouts y visitas UCT. |
| `contracts/game_policy.json` | Constante UCT y checks mínimos de poda/consistencia. |
| `ops/audit_game_search.py` | Minimax, alfa-beta, media Monte Carlo y UCT. |
| `output/game_search_report.json` | Scores, hojas visitadas, podas, medias y UCT. |
| `output/game_search_decision.md` | Lectura técnica para defender la decisión. |

## Qué deberías mirar

1. Por qué minimax prefiere la acción con mejor peor caso.
2. Por qué alfa-beta conserva la decisión pero visita menos hojas.
3. Por qué una media Monte Carlo alta puede esconder un peor caso intolerable.
4. Qué cambia al subir o bajar la constante de exploración `c`.
5. Cómo se traduce esto a agentes que usan tools, presupuestos o aprobaciones.

## Qué entregaría un alumno

1. El Markdown generado.
2. Un nodo nuevo con utilidades terminales.
3. Una comparación entre minimax y Monte Carlo.
4. Una decisión escrita: optimizar peor caso, media, revisión humana o más simulación.

## Qué te llevas

Te llevas una práctica ejecutable sobre minimax, alfa-beta y UCT en decisiones con otro actor, con datos editables, contratos y umbrales, plantillas de entrega, código ejecutable y tests reproducibles. Trabajas con `data/game_tree.json`, contrastas la decisión contra `contracts/game_policy.json` y ejecutas `ops/audit_game_search.py` para generar `output/game_search_decision.md`. La idea no es mirar una solución cerrada: es cambiar una entrada, volver a ejecutar, comparar la salida y poder defender qué harías en una revisión técnica, una asignatura o un piloto real.

## Variantes para hacerlo tuyo

- Ejecuta `make run` sin tocar nada y usa `output/game_search_decision.md` como línea base.
- Cambia o añade un caso en `data/game_tree.json` para representar un problema de tu trabajo, clase o producto.
- Endurece una regla, umbral o campo obligatorio en `contracts/game_policy.json` y explica por qué el resultado debería cambiar o bloquearse.
- Compara antes/después en `output/game_search_decision.md` y `output/game_search_report.json` y escribe una decisión de una página: seguir, bloquear, medir más o cambiar el diseño.
- Completa `templates/entrega.md` con contexto, cambio, evidencia, decisión y límite; no la dejes como checklist vacía.

## Rúbrica rápida

| Nivel | Qué demuestra |
|---|---|
| Mínimo | Ejecuta `make run` y `make test`, localiza `ops/audit_game_search.py`, abre `output/game_search_decision.md` y explica qué decisión o señal produce. |
| Bueno | Cambia `data/game_tree.json`, compara antes/después y justifica la diferencia con una evidencia concreta del output. |
| Excelente | Convierte el kit en un mini caso profesional: añade un caso propio, ajusta una regla o test, documenta el límite principal y deja una recomendación accionable para un equipo. |

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `Kit F2 C11: minimax, alfa-beta y UCT en decisiones con otro actor`, no escondido en una ruta del repositorio.

### Qué contiene

- `README.md`: esta guía y la explicación del ejercicio.
- `Makefile`: entrada única para ejecutar y validar el kit con `make run` y `make test`.
- `requirements.txt`: dependencias declaradas; muchos kits solo usan la biblioteca estándar de Python.
- `data/`: datos de entrada o casos de prueba realistas. Ejemplos dentro del ZIP: `data/game_tree.json`.
- `contracts/`: contratos de datos, salida, política o validación. Ejemplos dentro del ZIP: `contracts/game_policy.json`.
- `templates/`: plantillas editables para la entrega. Ejemplos dentro del ZIP: `templates/entrega.md`.
- `ops/`: código ejecutable del laboratorio. Ejemplos dentro del ZIP: `ops/audit_game_search.py`.
- `tests/`: tests que comprueban que el ejercicio sigue siendo reproducible. Ejemplos dentro del ZIP: `tests/test_lab_contract.py`.
- `output/`: salidas generadas o esperadas que debes revisar. Ejemplos dentro del ZIP: `output/game_search_decision.md`, `output/game_search_report.json`.

### Ejecutar desde cero

Desde la carpeta extraída del ZIP:

```bash
make run
make test
```

`make run` construye las evidencias del ejercicio. `make test` comprueba que el kit sigue siendo ejecutable después de descargarlo, extraerlo y tocarlo.

### Qué mirar antes de entregar

- `output/game_search_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/game_search_report.json`: evidencia estructurada para validar o automatizar.

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
