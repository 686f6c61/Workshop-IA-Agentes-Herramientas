# Kit F3 C03: auditoría QKV y máscara causal

Este kit acompaña el capítulo 03 del facsímil 3. Implementa una self-attention causal mínima y comprueba que ningún token mira al futuro.

## Ejecutar

```bash
python3 ops/audit_causal_attention.py --write
cat output/causal_attention_decision.md
```

Como gate:

```bash
python3 ops/audit_causal_attention.py --write --fail-on-invalid
```

## Archivos

| Archivo | Papel |
|---|---|
| `data/qkv_case.json` | Matriz de entrada y pesos Wq, Wk, Wv. |
| `contracts/causal_attention_policy.json` | Tolerancia y regla de no mirar al futuro. |
| `ops/audit_causal_attention.py` | Matmul, softmax, atención causal y checks. |
| `output/causal_attention_report.json` | Q, K, V, pesos y salida. |
| `output/causal_attention_decision.md` | Informe legible. |

## Qué deberías mirar

1. `q`, `k` y `v`: cada matriz responde a una pregunta distinta, aunque salgan del mismo input.
2. `raw_scores`: similitudes antes de aplicar máscara.
3. `masked_scores`: posiciones futuras anuladas por la máscara causal.
4. `attention_weights`: distribución válida solo sobre tokens anteriores o presentes.
5. `future_leakage_checks`: si algún token mira al futuro, el ejemplo debe bloquearse.

## Cómo lo adaptas a tu caso

Añade una fila nueva en `data/qkv_case.json` y comprueba que las posiciones posteriores siguen enmascaradas. La práctica sirve para defender un punto esencial de los modelos autoregresivos: durante generación, el token actual no puede usar información de tokens futuros.

## Qué entregaría un alumno

El Markdown generado, una fila nueva de entrada y una explicación de qué posiciones están enmascaradas.

## Qué te llevas

Te llevas una práctica ejecutable sobre auditoría QKV y máscara causal, con datos editables, contratos y umbrales, plantillas de entrega, código ejecutable y tests reproducibles. Trabajas con `data/qkv_case.json`, contrastas la decisión contra `contracts/causal_attention_policy.json` y ejecutas `ops/audit_causal_attention.py` para generar `output/causal_attention_decision.md`. La idea no es mirar una solución cerrada: es cambiar una entrada, volver a ejecutar, comparar la salida y poder defender qué harías en una revisión técnica, una asignatura o un piloto real.

## Variantes para hacerlo tuyo

- Ejecuta `make run` sin tocar nada y usa `output/causal_attention_decision.md` como línea base.
- Cambia o añade un caso en `data/qkv_case.json` para representar un problema de tu trabajo, clase o producto.
- Endurece una regla, umbral o campo obligatorio en `contracts/causal_attention_policy.json` y explica por qué el resultado debería cambiar o bloquearse.
- Compara antes/después en `output/causal_attention_decision.md` y `output/causal_attention_report.json` y escribe una decisión de una página: seguir, bloquear, medir más o cambiar el diseño.
- Completa `templates/entrega.md` con contexto, cambio, evidencia, decisión y límite; no la dejes como checklist vacía.

## Rúbrica rápida

| Nivel | Qué demuestra |
|---|---|
| Mínimo | Ejecuta `make run` y `make test`, localiza `ops/audit_causal_attention.py`, abre `output/causal_attention_decision.md` y explica qué decisión o señal produce. |
| Bueno | Cambia `data/qkv_case.json`, compara antes/después y justifica la diferencia con una evidencia concreta del output. |
| Excelente | Convierte el kit en un mini caso profesional: añade un caso propio, ajusta una regla o test, documenta el límite principal y deja una recomendación accionable para un equipo. |

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `Kit F3 C03: auditoría QKV y máscara causal`, no escondido en una ruta del repositorio.

### Qué contiene

- `README.md`: esta guía y la explicación del ejercicio.
- `Makefile`: entrada única para ejecutar y validar el kit con `make run` y `make test`.
- `requirements.txt`: dependencias declaradas; muchos kits solo usan la biblioteca estándar de Python.
- `data/`: datos de entrada o casos de prueba realistas. Ejemplos dentro del ZIP: `data/qkv_case.json`.
- `contracts/`: contratos de datos, salida, política o validación. Ejemplos dentro del ZIP: `contracts/causal_attention_policy.json`.
- `templates/`: plantillas editables para la entrega. Ejemplos dentro del ZIP: `templates/entrega.md`.
- `ops/`: código ejecutable del laboratorio. Ejemplos dentro del ZIP: `ops/audit_causal_attention.py`.
- `tests/`: tests que comprueban que el ejercicio sigue siendo reproducible. Ejemplos dentro del ZIP: `tests/test_lab_contract.py`.
- `output/`: salidas generadas o esperadas que debes revisar. Ejemplos dentro del ZIP: `output/causal_attention_decision.md`, `output/causal_attention_report.json`.

### Ejecutar desde cero

Desde la carpeta extraída del ZIP:

```bash
make run
make test
```

`make run` construye las evidencias del ejercicio. `make test` comprueba que el kit sigue siendo ejecutable después de descargarlo, extraerlo y tocarlo.

### Qué mirar antes de entregar

- `output/causal_attention_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/causal_attention_report.json`: evidencia estructurada para validar o automatizar.

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
