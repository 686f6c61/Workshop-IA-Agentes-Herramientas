# Kit F2 C03: auditar heurísticas

Este kit acompaña el capítulo 03 del facsímil 2. Ejecuta UCS, Greedy, A*, A* con heurística nula, A* con una heurística exacta de demostración y Weighted A* sobre el mismo grafo ponderado.

El objetivo no es memorizar fórmulas: es comprobar con datos cuándo una heurística conserva garantías, cuándo solo acelera y cuándo puede romper la optimalidad.

## Ejecutar

Desde esta carpeta:

```bash
python3 ops/audit_heuristics.py --write
cat output/heuristic_decision.md
```

Como gate:

```bash
python3 ops/audit_heuristics.py --write --fail-on-invalid
```

## Archivos

| Archivo | Papel |
|---|---|
| `data/heuristic_graph.json` | Grafo ponderado, inicio, meta y heurísticas candidatas. |
| `contracts/heuristic_policy.json` | Reglas de auditoría, peso de Weighted A* y condiciones mínimas del gate. |
| `ops/audit_heuristics.py` | Implementación de auditoría, UCS, Greedy, A* y Weighted A* sin dependencias externas. |
| `output/heuristic_report.json` | Resultados estructurados: coste real, pruebas de heurística y métricas de búsqueda. |
| `output/heuristic_decision.md` | Informe legible para revisión o entrega. |

## Qué deberías mirar

1. Qué heurísticas son admisibles y consistentes.
2. Qué heurística domina a otra sin sobreestimar.
3. Cuántos nodos expande A* con `h_zero`, `h_safe` y `h_exact_demo`.
4. Qué solución devuelve Greedy cuando solo mira `h(n)`.
5. Qué ocurre cuando Weighted A* usa `f(n)=g(n)+w·h(n)` con `w>1`.
6. Por qué una heurística que sobreestima no debería entrar en un sistema que promete optimalidad.

## Qué entregaría un alumno

1. El Markdown generado.
2. Una heurística propia añadida al JSON.
3. La prueba de si esa heurística es admisible y consistente.
4. Una comparación entre coste óptimo, expansiones y frontera máxima.
5. Una decisión escrita: qué algoritmo usaría si necesita optimalidad y cuál usaría si acepta una respuesta aproximada más barata.

## Qué te llevas

Te llevas una práctica ejecutable sobre auditar heurísticas, con datos editables, contratos y umbrales, plantillas de entrega, código ejecutable y tests reproducibles. Trabajas con `data/heuristic_graph.json`, contrastas la decisión contra `contracts/heuristic_policy.json` y ejecutas `ops/audit_heuristics.py` para generar `output/heuristic_decision.md`. La idea no es mirar una solución cerrada: es cambiar una entrada, volver a ejecutar, comparar la salida y poder defender qué harías en una revisión técnica, una asignatura o un piloto real.

## Variantes para hacerlo tuyo

- Ejecuta `make run` sin tocar nada y usa `output/heuristic_decision.md` como línea base.
- Cambia o añade un caso en `data/heuristic_graph.json` para representar un problema de tu trabajo, clase o producto.
- Endurece una regla, umbral o campo obligatorio en `contracts/heuristic_policy.json` y explica por qué el resultado debería cambiar o bloquearse.
- Compara antes/después en `output/heuristic_decision.md` y `output/heuristic_report.json` y escribe una decisión de una página: seguir, bloquear, medir más o cambiar el diseño.
- Completa `templates/entrega.md` con contexto, cambio, evidencia, decisión y límite; no la dejes como checklist vacía.

## Rúbrica rápida

| Nivel | Qué demuestra |
|---|---|
| Mínimo | Ejecuta `make run` y `make test`, localiza `ops/audit_heuristics.py`, abre `output/heuristic_decision.md` y explica qué decisión o señal produce. |
| Bueno | Cambia `data/heuristic_graph.json`, compara antes/después y justifica la diferencia con una evidencia concreta del output. |
| Excelente | Convierte el kit en un mini caso profesional: añade un caso propio, ajusta una regla o test, documenta el límite principal y deja una recomendación accionable para un equipo. |

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `Kit F2 C03: auditar heurísticas`, no escondido en una ruta del repositorio.

### Qué contiene

- `README.md`: esta guía y la explicación del ejercicio.
- `Makefile`: entrada única para ejecutar y validar el kit con `make run` y `make test`.
- `requirements.txt`: dependencias declaradas; muchos kits solo usan la biblioteca estándar de Python.
- `data/`: datos de entrada o casos de prueba realistas. Ejemplos dentro del ZIP: `data/heuristic_graph.json`.
- `contracts/`: contratos de datos, salida, política o validación. Ejemplos dentro del ZIP: `contracts/heuristic_policy.json`.
- `templates/`: plantillas editables para la entrega. Ejemplos dentro del ZIP: `templates/entrega.md`.
- `ops/`: código ejecutable del laboratorio. Ejemplos dentro del ZIP: `ops/audit_heuristics.py`.
- `tests/`: tests que comprueban que el ejercicio sigue siendo reproducible. Ejemplos dentro del ZIP: `tests/test_lab_contract.py`.
- `output/`: salidas generadas o esperadas que debes revisar. Ejemplos dentro del ZIP: `output/heuristic_decision.md`, `output/heuristic_report.json`.

### Ejecutar desde cero

Desde la carpeta extraída del ZIP:

```bash
make run
make test
```

`make run` construye las evidencias del ejercicio. `make test` comprueba que el kit sigue siendo ejecutable después de descargarlo, extraerlo y tocarlo.

### Qué mirar antes de entregar

- `output/heuristic_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/heuristic_report.json`: evidencia estructurada para validar o automatizar.

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
