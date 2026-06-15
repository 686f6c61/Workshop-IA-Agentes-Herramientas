# F9 C04 · Paquete de evidencias para AI Act, ISO 42001 y auditoría

Este kit construye un paquete de evidencias revisable para tres sistemas de IA. La idea no es dar una conclusión legal automática. La idea es entrenar una forma de trabajo: inventario, clasificación inicial, requisitos aplicables, evidencias, huecos, owners y gate de publicación.

## Ejecutar

```bash
python3 ops/build_audit_pack.py --write
```

Cómo gate de CI:

```bash
python3 ops/build_audit_pack.py --write --fail-on-blocker
```

El gate puede fallar a propósito si hay evidencias bloqueantes sin cerrar. Eso es parte del ejercicio.

## Archivos de entrada

| Archivo | Uso |
|---|---|
| `contracts/compliance_policy.json` | Catálogo de requisitos, criterios de clasificación inicial y reglas del gate. |
| `data/ai_systems.csv` | Inventario de sistemas de IA con uso previsto, dominio, efecto, roles y versiones. |
| `data/evidence_catalog.csv` | Evidencias disponibles por sistema y requisito. |
| `data/providers.csv` | Terceros usados por sistema: modelo, vector DB, observabilidad, cloud y plan de salida. |

## Salidas

| Archivo | Qué demuestra |
|---|---|
| `output/ai_system_register.csv` | Inventario enriquecido con clasificación inicial y explicación técnica. |
| `output/article_to_artifact_crosswalk.csv` | Requisito -> control -> evidencia -> owner -> estado. |
| `output/compliance_gap_matrix.md` | Huecos por sistema y plan mínimo de cierre. |
| `output/evidence_package_manifest.json` | Manifest versionado del paquete de evidencias. |
| `output/annex_iv_technical_file.md` | Technical file mínimo para el sistema más exigente del conjunto. |
| `output/iso42001_aims_scope.md` | Alcance AIMS y procesos cubiertos por el sistema de gestión de IA. |
| `output/change_control_record.md` | Cambios que obligan a reabrir revisión. |
| `output/audit_gate.md` | Decisión de publicación y condiciones. |
| `output/trace_evidence_sample.jsonl` | Muestra de trazas mínimas de record-keeping. |
| `output/recordkeeping_schema.json` | Contrato de campos mínimos para trazas revisables. |
| `output/provider_due_diligence_checklist.md` | Checklist técnico de terceros y evidencias que faltan. |
| `output/ai_bom.md` | Inventario operativo de modelo, prompt, RAG, tools, terceros, políticas y límites de agente. |
| `output/evidence_maturity_model.md` | Madurez de evidencias por sistema y requisito. |
| `output/policy_as_code_rules.md` | Reglas que explican por qué el gate permite, condiciona o detiene. |

## Cómo adaptarlo

1. Sustituye `data/ai_systems.csv` por el inventario real del equipo.
2. Cambia `data/evidence_catalog.csv` por evidencias reales: rutas, owners, versiones y fecha de revisión.
3. Ajusta `contracts/compliance_policy.json` si tu organización tiene más marcos, thresholds o requisitos internos.
4. Ejecuta el gate en CI antes de publicar o cambiar modelo, prompt, RAG, tool, política o finalidad.
5. Añade tus proveedores reales en `data/providers.csv` y exige evidencia de región, retención, logs, subprocesadores, contrato y plan de salida.
6. Revisa `output/ai_bom.md` como inventario vivo antes de aprobar cambios de agente, memoria, credenciales o tools.

## Qué te llevas

Te llevas una práctica ejecutable sobre F9 C04 · Paquete de evidencias para AI Act, ISO 42001 y auditoría, con datos editables, contratos y umbrales, plantillas de entrega, código ejecutable y tests reproducibles. Trabajas con `data/ai_systems.csv` y `data/evidence_catalog.csv`, contrastas la decisión contra `contracts/compliance_policy.json` y ejecutas `ops/build_audit_pack.py` para generar `output/ai_bom.md`. La idea no es mirar una solución cerrada: es cambiar una entrada, volver a ejecutar, comparar la salida y poder defender qué harías en una revisión técnica, una asignatura o un piloto real.

## Variantes para hacerlo tuyo

- Ejecuta `make run` sin tocar nada y usa `output/ai_bom.md` como línea base.
- Cambia o añade un caso en `data/ai_systems.csv` y `data/evidence_catalog.csv` para representar un problema de tu trabajo, clase o producto.
- Endurece una regla, umbral o campo obligatorio en `contracts/compliance_policy.json` y explica por qué el resultado debería cambiar o bloquearse.
- Compara antes/después en `output/ai_bom.md` y `output/annex_iv_technical_file.md` y escribe una decisión de una página: seguir, bloquear, medir más o cambiar el diseño.
- Completa `templates/entrega.md` con contexto, cambio, evidencia, decisión y límite; no la dejes como checklist vacía.

## Rúbrica rápida

| Nivel | Qué demuestra |
|---|---|
| Mínimo | Ejecuta `make run` y `make test`, localiza `ops/build_audit_pack.py`, abre `output/ai_bom.md` y explica qué decisión o señal produce. |
| Bueno | Cambia `data/ai_systems.csv`, compara antes/después y justifica la diferencia con una evidencia concreta del output. |
| Excelente | Convierte el kit en un mini caso profesional: añade un caso propio, ajusta una regla o test, documenta el límite principal y deja una recomendación accionable para un equipo. |

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `F9 C04 · Paquete de evidencias para AI Act, ISO 42001 y auditoría`, no escondido en una ruta del repositorio.

### Qué contiene

- `README.md`: esta guía y la explicación del ejercicio.
- `Makefile`: entrada única para ejecutar y validar el kit con `make run` y `make test`.
- `requirements.txt`: dependencias declaradas; muchos kits solo usan la biblioteca estándar de Python.
- `data/`: datos de entrada o casos de prueba realistas. Ejemplos dentro del ZIP: `data/ai_systems.csv`, `data/evidence_catalog.csv`, `data/providers.csv`.
- `contracts/`: contratos de datos, salida, política o validación. Ejemplos dentro del ZIP: `contracts/compliance_policy.json`.
- `templates/`: plantillas editables para la entrega. Ejemplos dentro del ZIP: `templates/entrega.md`.
- `ops/`: código ejecutable del laboratorio. Ejemplos dentro del ZIP: `ops/build_audit_pack.py`.
- `tests/`: tests que comprueban que el ejercicio sigue siendo reproducible. Ejemplos dentro del ZIP: `tests/test_lab_contract.py`.
- `output/`: salidas generadas o esperadas que debes revisar. Ejemplos dentro del ZIP: `output/ai_bom.md`, `output/annex_iv_technical_file.md`, `output/audit_gate.md`, `output/change_control_record.md`, ....

### Ejecutar desde cero

Desde la carpeta extraída del ZIP:

```bash
make run
make test
```

`make run` construye las evidencias del ejercicio. `make test` comprueba que el kit sigue siendo ejecutable después de descargarlo, extraerlo y tocarlo.

### Qué mirar antes de entregar

- `output/ai_bom.md`: lectura humana de la decisión, informe o runbook.
- `output/annex_iv_technical_file.md`: lectura humana de la decisión, informe o runbook.
- `output/audit_gate.md`: lectura humana de la decisión, informe o runbook.
- `output/change_control_record.md`: lectura humana de la decisión, informe o runbook.
- `output/compliance_gap_matrix.md`: lectura humana de la decisión, informe o runbook.
- `output/evidence_maturity_model.md`: lectura humana de la decisión, informe o runbook.
- `output/iso42001_aims_scope.md`: lectura humana de la decisión, informe o runbook.
- `output/policy_as_code_rules.md`: lectura humana de la decisión, informe o runbook.
- `output/provider_due_diligence_checklist.md`: lectura humana de la decisión, informe o runbook.
- `output/evidence_package_manifest.json`: evidencia estructurada para validar o automatizar.
- `output/recordkeeping_schema.json`: evidencia estructurada para validar o automatizar.
- `output/trace_evidence_sample.jsonl`: eventos o registros línea a línea.

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
