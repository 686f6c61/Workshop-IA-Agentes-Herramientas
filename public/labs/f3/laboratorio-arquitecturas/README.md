# F3 · Laboratorio de arquitecturas y modelos

Este kit convierte el laboratorio del facsímil 3 en una decisión técnica reproducible. La idea no es ejecutar scripts por cumplir, sino salir con dos entregables defendibles: una estrategia de modelo para conocimiento cambiante y una estimación de serving antes de prometer latencia.

Trabaja dos retos:

| Reto | Qué practicas | Entregable principal |
|---|---|---|
| 1 | Elegir entre prompt largo, RAG y fine-tuning. | `output/strategy_decision.md` |
| 2 | Estimar pesos, KV cache, decode y rediseño de serving. | `output/deployment_memo.md` |

## Ejecutar

Desde la raíz del proyecto:

```bash
cd labs/f3/laboratorio-arquitecturas
python3 ops/score_architecture_strategy.py --write
python3 ops/estimate_inference_budget.py --write
python3 ops/check_student_submission.py --submission-dir solutions/reference --write --fail-on-missing
```

Como gates independientes:

```bash
python3 ops/score_architecture_strategy.py --write --fail-on-review
python3 ops/estimate_inference_budget.py --write --fail-on-review
```

Generar solución de referencia:

```bash
python3 ops/score_architecture_strategy.py --output-dir solutions/reference --write
python3 ops/estimate_inference_budget.py --output-dir solutions/reference --write
python3 ops/check_student_submission.py --submission-dir solutions/reference --write --fail-on-missing
```

## Entradas

| Archivo | Uso |
|---|---|
| `contracts/arquitecturas_lab_contract.json` | Gates de estrategia, presupuesto de inferencia y checker final. |
| `data/strategy_case.json` | Caso de normativa interna, opciones comparadas y pesos de decisión. |
| `data/inference_scenario.json` | Parámetros, cuantización, capas, KV cache, batch, contexto y decode. |

## Salidas

| Archivo | Qué demuestra |
|---|---|
| `output/strategy_scorecard.json` | Ranking ponderado entre API con prompt largo, RAG/local y fine-tuning. |
| `output/strategy_decision.md` | Decisión técnica con razones, riesgos y evaluación mínima. |
| `output/inference_budget.json` | Pesos, KV cache, memoria total, tokens/s por usuario y tiempo de decode. |
| `output/deployment_memo.md` | Memo de rediseño antes de comprar hardware o prometer producto. |
| `output/student_submission_report.md` | Checker de entrega: conceptos mínimos y puntuación. |

## Reto 1: estrategia para normativa viva

Una organización quiere un asistente sobre normativa interna. Las normas cambian varias veces al año, las respuestas deben citar documentos y no se quiere convertir cada cambio de política en un reentrenamiento.

Tienes tres rutas:

| Opción | Lectura técnica |
|---|---|
| API potente con prompt largo | Prototipa rápido, pero puede disparar coste de contexto y dependencia externa. |
| Modelo abierto local con RAG | Separa conocimiento vivo de pesos y permite citar documentos recuperados. |
| Fine-tuning mensual | Puede enseñar formato o estilo, pero no es la forma más limpia de actualizar normativa. |

La solución esperada debe explicar por qué RAG encaja como primera estrategia, qué medirías y qué riesgos quedan abiertos. No vale responder “RAG porque sí”: tienes que hablar de contexto, citas, evaluación, privacidad, coste y mantenimiento.

El script que lo trabaja:

```bash
python3 ops/score_architecture_strategy.py --write
cat output/strategy_decision.md
```

## Reto 2: presupuesto de inferencia antes de prometer

Un equipo propone servir un modelo de 7B cuantizado a 4 bits para generar informes. Hay usuarios concurrentes, contexto de entrada y salidas largas. La pregunta profesional no es solo si los pesos caben: es si el sistema puede responder con una experiencia aceptable.

El cálculo separa:

| Pieza | Por qué importa |
|---|---|
| Pesos | Memoria mínima del modelo cargado. |
| KV cache | Memoria que crece con capas, contexto, batch y cabezas KV. |
| Decode | Tiempo secuencial de generación, repartido entre usuarios. |
| Margen operativo | Runtime, buffers, sistema, colas y p95 no aparecen gratis. |

El script que lo trabaja:

```bash
python3 ops/estimate_inference_budget.py --write
cat output/deployment_memo.md
```

La solución esperada debe detectar si la propuesta necesita rediseño. Si el decode por usuario se va a decenas de segundos, la conclusión no puede ser “el modelo cabe”; debe hablar de streaming, reducir salida, colas, batch, modelo más pequeño, destilación, hardware o cambio de experiencia.

## Cómo saber si está bien

Una buena entrega:

- distingue parámetros, contexto y sistema;
- separa RAG, prompt largo y fine-tuning;
- estima pesos y KV cache con unidades;
- explica TTFT, decode y tokens/s por usuario;
- propone evaluación mínima antes de producción;
- cambia al menos un peso o parámetro y explica cómo afecta la decisión.

El checker de referencia debe terminar con puntuación completa:

```bash
python3 ops/check_student_submission.py --submission-dir solutions/reference --write --fail-on-missing
cat output/student_submission_report.md
```

## En resumen

La versión corta del facsímil no es “los LLMs son Transformers”. Es más concreta: un modelo es una arquitectura entrenada, adaptada y servida bajo restricciones. Este laboratorio obliga a convertir esa frase en una decisión con datos, costes y límites.

## Qué te llevas

Te llevas una práctica ejecutable sobre F3 · Laboratorio de arquitecturas y modelos, con datos editables, contratos y umbrales, plantillas de entrega, código ejecutable y tests reproducibles. Trabajas con `data/inference_scenario.json` y `data/strategy_case.json`, contrastas la decisión contra `contracts/arquitecturas_lab_contract.json` y ejecutas `ops/check_student_submission.py` para generar `output/deployment_memo.md`. La idea no es mirar una solución cerrada: es cambiar una entrada, volver a ejecutar, comparar la salida y poder defender qué harías en una revisión técnica, una asignatura o un piloto real.

## Variantes para hacerlo tuyo

- Ejecuta `make run` sin tocar nada y usa `output/deployment_memo.md` como línea base.
- Cambia o añade un caso en `data/inference_scenario.json` y `data/strategy_case.json` para representar un problema de tu trabajo, clase o producto.
- Endurece una regla, umbral o campo obligatorio en `contracts/arquitecturas_lab_contract.json` y explica por qué el resultado debería cambiar o bloquearse.
- Compara antes/después en `output/deployment_memo.md` y `output/strategy_decision.md` y escribe una decisión de una página: seguir, bloquear, medir más o cambiar el diseño.
- Completa `templates/entrega.md` con contexto, cambio, evidencia, decisión y límite; no la dejes como checklist vacía.

## Rúbrica rápida

| Nivel | Qué demuestra |
|---|---|
| Mínimo | Ejecuta `make run` y `make test`, localiza `ops/check_student_submission.py`, abre `output/deployment_memo.md` y explica qué decisión o señal produce. |
| Bueno | Cambia `data/inference_scenario.json`, compara antes/después y justifica la diferencia con una evidencia concreta del output. |
| Excelente | Convierte el kit en un mini caso profesional: añade un caso propio, ajusta una regla o test, documenta el límite principal y deja una recomendación accionable para un equipo. |

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `F3 · Laboratorio de arquitecturas y modelos`, no escondido en una ruta del repositorio.

### Qué contiene

- `README.md`: esta guía y la explicación del ejercicio.
- `Makefile`: entrada única para ejecutar y validar el kit con `make run` y `make test`.
- `requirements.txt`: dependencias declaradas; muchos kits solo usan la biblioteca estándar de Python.
- `data/`: datos de entrada o casos de prueba realistas. Ejemplos dentro del ZIP: `data/inference_scenario.json`, `data/strategy_case.json`.
- `contracts/`: contratos de datos, salida, política o validación. Ejemplos dentro del ZIP: `contracts/arquitecturas_lab_contract.json`.
- `templates/`: plantillas editables para la entrega. Ejemplos dentro del ZIP: `templates/entrega.md`.
- `ops/`: código ejecutable del laboratorio. Ejemplos dentro del ZIP: `ops/check_student_submission.py`, `ops/estimate_inference_budget.py`, `ops/score_architecture_strategy.py`.
- `tests/`: tests que comprueban que el ejercicio sigue siendo reproducible. Ejemplos dentro del ZIP: `tests/test_lab_contract.py`.
- `output/`: salidas generadas o esperadas que debes revisar. Ejemplos dentro del ZIP: `output/deployment_memo.md`, `output/strategy_decision.md`, `output/student_submission_report.md`, `output/inference_budget.json`, ....
- `solutions/`: soluciones de referencia o carpeta para la entrega del alumno. Ejemplos dentro del ZIP: `solutions/reference/deployment_memo.md`, `solutions/reference/strategy_decision.md`, `solutions/reference/inference_budget.json`, `solutions/reference/strategy_scorecard.json`.

### Ejecutar desde cero

Desde la carpeta extraída del ZIP:

```bash
make run
make test
```

`make run` construye las evidencias del ejercicio. `make test` comprueba que el kit sigue siendo ejecutable después de descargarlo, extraerlo y tocarlo.

### Qué mirar antes de entregar

- `output/deployment_memo.md`: lectura humana de la decisión, informe o runbook.
- `output/strategy_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/student_submission_report.md`: lectura humana de la decisión, informe o runbook.
- `solutions/reference/deployment_memo.md`: lectura humana de la decisión, informe o runbook.
- `solutions/reference/strategy_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/inference_budget.json`: evidencia estructurada para validar o automatizar.
- `output/strategy_scorecard.json`: evidencia estructurada para validar o automatizar.
- `solutions/reference/inference_budget.json`: evidencia estructurada para validar o automatizar.
- `solutions/reference/strategy_scorecard.json`: evidencia estructurada para validar o automatizar.

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
6. Usa `solutions/` como contraste de calidad, no como sustituto de tu razonamiento.
7. Guarda los outputs finales y una nota breve con la decisión técnica que tomarías en un proyecto real.

### Criterio de validación

El kit está completo cuando se puede descargar, extraer, ejecutar con `make run`, validar con `make test` y explicar sin depender de ninguna carpeta externa. Si una práctica menciona código, datos, contrato, CSV, SQL, política o plantilla, ese contenido debe venir dentro del ZIP.
<!-- zip-quality-audit:end -->
