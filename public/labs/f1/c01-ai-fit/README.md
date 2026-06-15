# Kit F1 C01: decidir si necesitas IA generativa

Este kit acompaña el capítulo 01 del facsímil 1. Convierte la idea central del capítulo en una práctica de ingeniería: antes de pedirle algo a un LLM, decide si el problema necesita generación, consulta exacta, recuperación documental, una herramienta, revisión humana o una mezcla.

El objetivo no es llamar a ningún proveedor. El objetivo es aprender a no tratar un modelo como un oráculo.

## Ejecutar

Desde esta carpeta:

```bash
python3 ops/triage_ai_fit.py --write
cat output/ai_fit_decision.md
```

Si prefieres tratarlo como mini proyecto:

```bash
make run
make test
```

Como gate de revisión:

```bash
python3 ops/triage_ai_fit.py --write --fail-on-review
```

## Requisitos

No necesitas credenciales ni proveedor de IA. El kit usa solo la biblioteca estándar de Python. `requirements.txt` está incluido para que quede explícito que no hay dependencias externas: Python 3.10 o superior basta.

## Archivos

| Archivo | Papel |
|---|---|
| `Makefile` | Atajos reproducibles para ejecutar, probar y limpiar salidas. |
| `requirements.txt` | Declara que el kit no requiere paquetes externos. |
| `data/use_cases.json` | Casos realistas que un equipo podría intentar resolver con IA. |
| `contracts/decision_policy.json` | Política de decisión: umbrales, controles mínimos y vocabulario permitido. |
| `ops/triage_ai_fit.py` | Script ejecutable sin dependencias externas. |
| `tests/test_triage_ai_fit.py` | Tests que comprueban que la política no deja pasar recomendaciones peligrosas. |
| `output/ai_fit_report.json` | Recomendaciones estructuradas por caso. |
| `output/ai_fit_decision.md` | Decisión legible para revisar en clase o en un equipo. |

## Qué deberías mirar

1. Si el caso requiere cálculo exacto, el script empuja hacia SQL o código determinista.
2. Si el caso necesita información cambiante o documentos fuente, empuja hacia buscador/RAG.
3. Si el caso actúa sobre sistemas reales, añade herramienta/API y aprobación.
4. Si el impacto es alto, exige revisión humana aunque haya LLM.
5. Si solo necesitas tono, resumen o redacción, permite LLM con controles ligeros.

## Criterios de aceptación

El ejercicio está bien resuelto cuando:

1. `make test` termina sin errores.
2. `output/ai_fit_report.json` contiene una fila por cada caso de `data/use_cases.json`.
3. Ningún caso con cálculo exacto queda recomendado como `llm_generation` puro.
4. Todo caso con impacto alto o acción externa incluye `human_review`.
5. Puedes explicar, caso por caso, qué pieza resuelve el problema: SQL/código determinista, RAG, LLM, herramienta/API, revisión humana o sistema híbrido.

Si activas `--fail-on-review`, el comando debe salir con código distinto de cero cuando haya casos que exigen revisión humana. Ese modo imita un gate de CI: no significa que el sistema esté mal, significa que no puede pasar como automatización directa.

## Cómo adaptarlo a un proyecto real

1. Sustituye los cinco casos de `data/use_cases.json` por decisiones reales de tu equipo, clase o producto.
2. Añade campos si tu contexto los necesita: datos personales, coste por error, latencia máxima, regulación, criticidad operativa o propietario responsable.
3. Ajusta `contracts/decision_policy.json`: cambia el umbral de revisión, añade controles mínimos y elimina componentes que tu organización no permita.
4. Ejecuta `make run` y revisa `output/ai_fit_decision.md` como si fuera una propuesta que presentarías en una reunión técnica.
5. Entrega el diff de datos y política junto con una nota breve: qué caso parecía necesitar IA y, después de auditarlo, qué arquitectura mínima usarías.

## Qué entregaría un alumno

1. `ai_fit_decision.md` generado.
2. Una modificación de `data/use_cases.json` con dos casos propios.
3. Una explicación de por qué un caso no debería resolverse con un LLM puro.
4. Una propuesta de controles mínimos para un caso de impacto alto.
5. El resultado de `make test` y una frase explicando qué protege cada test.

## Qué te llevas

Te llevas una práctica ejecutable sobre decidir si necesitas IA generativa, con datos editables, contratos y umbrales, plantillas de entrega, código ejecutable y tests reproducibles. Trabajas con `data/use_cases.json`, contrastas la decisión contra `contracts/decision_policy.json` y ejecutas `ops/triage_ai_fit.py` para generar `output/ai_fit_decision.md`. La idea no es mirar una solución cerrada: es cambiar una entrada, volver a ejecutar, comparar la salida y poder defender qué harías en una revisión técnica, una asignatura o un piloto real.

## Variantes para hacerlo tuyo

- Ejecuta `make run` sin tocar nada y usa `output/ai_fit_decision.md` como línea base.
- Cambia o añade un caso en `data/use_cases.json` para representar un problema de tu trabajo, clase o producto.
- Endurece una regla, umbral o campo obligatorio en `contracts/decision_policy.json` y explica por qué el resultado debería cambiar o bloquearse.
- Compara antes/después en `output/ai_fit_decision.md` y `output/ai_fit_report.json` y escribe una decisión de una página: seguir, bloquear, medir más o cambiar el diseño.
- Completa `templates/entrega.md` con contexto, cambio, evidencia, decisión y límite; no la dejes como checklist vacía.

## Rúbrica rápida

| Nivel | Qué demuestra |
|---|---|
| Mínimo | Ejecuta `make run` y `make test`, localiza `ops/triage_ai_fit.py`, abre `output/ai_fit_decision.md` y explica qué decisión o señal produce. |
| Bueno | Cambia `data/use_cases.json`, compara antes/después y justifica la diferencia con una evidencia concreta del output. |
| Excelente | Convierte el kit en un mini caso profesional: añade un caso propio, ajusta una regla o test, documenta el límite principal y deja una recomendación accionable para un equipo. |

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `Kit F1 C01: decidir si necesitas IA generativa`, no escondido en una ruta del repositorio.

### Qué contiene

- `README.md`: esta guía y la explicación del ejercicio.
- `Makefile`: entrada única para ejecutar y validar el kit con `make run` y `make test`.
- `requirements.txt`: dependencias declaradas; muchos kits solo usan la biblioteca estándar de Python.
- `data/`: datos de entrada o casos de prueba realistas. Ejemplos dentro del ZIP: `data/use_cases.json`.
- `contracts/`: contratos de datos, salida, política o validación. Ejemplos dentro del ZIP: `contracts/decision_policy.json`.
- `templates/`: plantillas editables para la entrega. Ejemplos dentro del ZIP: `templates/entrega.md`.
- `ops/`: código ejecutable del laboratorio. Ejemplos dentro del ZIP: `ops/triage_ai_fit.py`.
- `tests/`: tests que comprueban que el ejercicio sigue siendo reproducible. Ejemplos dentro del ZIP: `tests/test_triage_ai_fit.py`.
- `output/`: salidas generadas o esperadas que debes revisar. Ejemplos dentro del ZIP: `output/ai_fit_decision.md`, `output/ai_fit_report.json`.

### Ejecutar desde cero

Desde la carpeta extraída del ZIP:

```bash
make run
make test
```

`make run` construye las evidencias del ejercicio. `make test` comprueba que el kit sigue siendo ejecutable después de descargarlo, extraerlo y tocarlo.

### Qué mirar antes de entregar

- `output/ai_fit_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/ai_fit_report.json`: evidencia estructurada para validar o automatizar.

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
