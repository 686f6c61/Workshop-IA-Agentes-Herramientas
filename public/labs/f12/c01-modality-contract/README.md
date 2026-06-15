# Kit F12 C01: contrato multimodal

Este kit acompaña el capítulo 01 del facsímil 12. Sirve para tomar una decisión muy concreta antes de construir un sistema multimodal: qué modalidad mínima necesita cada caso, qué evidencia debe conservarse, qué contrato de salida se valida y qué riesgos aparecen al añadir imagen, documento, audio, vídeo o acción.

No entrena ningún modelo. Tampoco llama a una API externa. Es una práctica de ingeniería: convertir una idea difusa en un manifiesto verificable.

## Caso guía incluido

El caso `grant-workflow-005` es el hilo conductor del facsímil: una solicitud de beca bloqueada con ticket textual, captura de formulario, PDF de política y tabla de estados. Úsalo para practicar una decisión completa: qué modalidad aporta evidencia, qué pieza valida la causa y cuándo debe entrar revisión humana.

## Ejecutar

```bash
make run
cat output/modality_contract_report.md
```

Como gate:

```bash
make test
```

## Archivos

| Archivo | Papel |
|---|---|
| `data/modality_manifest.json` | Casos editables con entradas, modalidades, arquitectura candidata, evidencia, métricas, riesgos y revisión humana. |
| `contracts/modality_policy.json` | Reglas de validación y pesos sencillos de riesgo. |
| `ops/evaluate_modality_manifest.py` | Validador reproducible del manifiesto. |
| `output/modality_contract_report.json` | Evidencia estructurada para comparar o automatizar. |
| `output/modality_contract_report.md` | Informe humano con decisión por caso. |
| `templates/entrega.md` | Plantilla para documentar una adaptación propia. |

## Qué deberías mirar

1. `minimum_modalities`: si el caso necesita de verdad imagen, documento, audio o vídeo.
2. `candidate_architecture`: si la arquitectura propuesta encaja con las modalidades.
3. `evidence_required`: qué prueba debe conservarse para no responder “porque sí”.
4. `metrics`: cómo sabrás que el sistema funciona.
5. `risk_score`: qué añade privacidad, ambigüedad, layout, voz o alucinación.
6. `modality_tax`: el coste cualitativo de añadir modalidades: complejidad, latencia, privacidad y evaluación.

## Qué entregaría un alumno

1. `output/modality_contract_report.md`.
2. Una variante propia de `data/modality_manifest.json`.
3. Una decisión técnica: texto basta, multimodal merece la pena, falta evidencia, hace falta revisión humana o no conviene construir todavía.

## Qué te llevas

Te llevas una práctica ejecutable para diseñar contratos multimodales antes de tocar modelos. Trabajas con `data/modality_manifest.json`, lo contrastas contra `contracts/modality_policy.json` y ejecutas `ops/evaluate_modality_manifest.py` para generar `output/modality_contract_report.md`.

La idea es que puedas llevar esta estructura a soporte, producto, documentación, educación, operaciones o datos: antes de decir “usemos visión” o “mandemos el PDF al modelo”, dejas claro qué entra, qué sale, qué evidencia se guarda y qué métrica decide si el sistema sirve.

## Variantes para hacerlo tuyo

- Ejecuta `make run` sin tocar nada y usa `output/modality_contract_report.md` como línea base.
- Añade un caso en `data/modality_manifest.json` de tu trabajo o clase: una captura, una factura, una llamada, una tabla o una pantalla.
- Duplica `grant-workflow-005` y simplifícalo: primero solo texto, luego texto+captura, luego añade documento y tabla. Compara cómo suben evidencia, riesgo y coste.
- Endurece `contracts/modality_policy.json` para exigir más métricas, más evidencia o revisión humana en más casos.
- Compara antes/después y escribe una decisión de una página: seguir con texto, usar una modalidad adicional, pedir revisión humana o no construir.
- Completa `templates/entrega.md` con contexto, cambio, evidencia, decisión y límites.

## Rúbrica rápida

| Nivel | Qué demuestra |
|---|---|
| Mínimo | Ejecuta `make run` y `make test`, abre `output/modality_contract_report.md` y explica qué arquitectura recomienda para un caso. |
| Bueno | Modifica `data/modality_manifest.json`, compara antes/después y justifica la modalidad mínima con evidencia y métricas. |
| Excelente | Añade un caso propio, ajusta una regla de política, documenta riesgos y deja una decisión defendible para un equipo real. |

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `Kit F12 C01: contrato multimodal`, no escondido en una ruta del repositorio.

### Qué contiene

- `README.md`: esta guía y la explicación del ejercicio.
- `Makefile`: entrada única para ejecutar y validar el kit con `make run` y `make test`.
- `requirements.txt`: dependencias declaradas; este kit usa la biblioteca estándar de Python.
- `data/modality_manifest.json`: casos editables.
- `contracts/modality_policy.json`: reglas de validación.
- `ops/evaluate_modality_manifest.py`: código ejecutable.
- `templates/entrega.md`: plantilla editable.
- `tests/test_lab_contract.py`: tests de reproducibilidad.
- `output/`: salidas generadas o esperadas.

### Ejecutar desde cero

Desde la carpeta extraída del ZIP:

```bash
make run
make test
```

`make run` construye las evidencias del ejercicio. `make test` comprueba que el kit sigue siendo ejecutable después de descargarlo, extraerlo y tocarlo.

### Qué mirar antes de entregar

- `output/modality_contract_report.md`: informe humano de decisión.
- `output/modality_contract_report.json`: evidencia estructurada.

### Qué entregar

Una entrega útil no es una captura de pantalla. Debe incluir resultado de `make test`, artefactos de `output/`, un cambio propio en `data/modality_manifest.json` o `contracts/modality_policy.json` y una decisión técnica breve.

### Criterio de validación

El kit está completo cuando se puede descargar, extraer, ejecutar con `make run`, validar con `make test` y explicar sin depender de ninguna carpeta externa.
<!-- zip-quality-audit:end -->
