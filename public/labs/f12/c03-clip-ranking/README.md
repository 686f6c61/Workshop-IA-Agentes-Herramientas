# F12 C03 · CLIP y ranking contrastivo

Este laboratorio enseña, con vectores sintéticos, cómo funciona una pieza clave de CLIP y de muchas búsquedas multimodales: acercar una imagen y su texto positivo, separar negativos y evaluar si el ranking sirve.

No usa embeddings reales ni llama a ninguna API. Eso es intencionado: primero vemos el mecanismo con números controlados. Después puedes sustituir `data/catalog_pairs.json` por embeddings reales de tu proveedor o librería.

## Caso guía incluido

El dataset trae `grant_form_blocked` y `grant_policy_pdf`. La primera representa una captura de solicitud de beca bloqueada; la segunda, un documento de política de becas. Son útiles porque comparten dominio, pero no resuelven la misma tarea. Si el ranking los acerca demasiado, necesitas mirar margen, metadatos, OCR, reranking o revisión humana.

## Ejecutar

```bash
make run
make test
```

El script genera:

| Archivo | Qué contiene |
|---|---|
| `output/clip_ranking_report.md` | Informe legible con métricas, negativos duros y consultas externas. |
| `output/clip_ranking_report.json` | Mismo informe en JSON para CI o notebooks. |
| `output/similarity_matrix.csv` | Matriz imagen-texto con similitud coseno. |
| `output/retrieval_errors.csv` | Confusiones o márgenes bajos que conviene revisar. |
| `output/contrastive_matrix.svg` | Visualización de la matriz con diagonal positiva. |

## Qué deberías mirar

1. La diagonal de `output/similarity_matrix.csv`.
2. Las celdas altas fuera de diagonal: son negativos duros.
3. `Recall@1` en las dos direcciones: imagen->texto y texto->imagen.
4. La pérdida InfoNCE: no como número mágico, sino como señal de separación entre positivos y negativos.
5. Las consultas externas: simulan el uso real, donde el texto de búsqueda no es exactamente el texto positivo del entrenamiento.

## Cambios útiles

- Baja `temperature` en `contracts/retrieval_policy.json` y observa cómo se vuelve más agresiva la distribución.
- Mira `q_beca_bloqueada` en `output/clip_ranking_report.md` y explica por qué recuperar la captura no valida por sí solo la política.
- Añade una imagen parecida a `invoice_total` y mira si aparece un negativo duro.
- Cambia el texto de `black_chair` para que sea más genérico y comprueba si pierde margen.
- Añade metadatos a mano y escribe qué filtro usarías antes del ranking vectorial.

## Qué te llevas

Un sistema de búsqueda multimodal no se valida mirando una demo bonita. Se valida con pares positivos, negativos duros, métricas de recuperación, consultas reales y revisión de errores. Este kit deja una versión mínima que puedes llevar a un catálogo, soporte con capturas o búsqueda documental visual.

## Auditoría del ZIP

El ZIP debe incluir datos, contrato, script, tests, outputs y plantilla de entrega. Si el capítulo habla de ranking o `Recall@k`, este laboratorio permite calcularlo.

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `F12 C03 · CLIP y ranking contrastivo`, no escondido en una ruta del repositorio.

### Qué contiene

- `README.md`: esta guía y la explicación del ejercicio.
- `Makefile`: entrada única para ejecutar y validar el kit con `make run` y `make test`.
- `requirements.txt`: dependencias declaradas; este kit usa la biblioteca estándar de Python.
- `data/catalog_pairs.json`: pares imagen-texto y consultas externas.
- `contracts/retrieval_policy.json`: contrato de evaluación.
- `ops/run_contrastive_ranking.py`: código ejecutable.
- `templates/entrega.md`: plantilla editable.
- `tests/test_lab_contract.py`: tests de reproducibilidad.
- `output/`: matriz, informe, errores y SVG generados.

### Ejecutar desde cero

Desde la carpeta extraída del ZIP:

```bash
make run
make test
```

`make run` construye las evidencias del ejercicio. `make test` comprueba que el kit sigue siendo ejecutable después de descargarlo, extraerlo y tocarlo.

### Qué mirar antes de entregar

- `output/similarity_matrix.csv`: diagonal positiva y celdas oscuras fuera de diagonal.
- `output/retrieval_errors.csv`: negativos duros o márgenes bajos.
- `output/clip_ranking_report.md`: métricas, queries y decisión.

### Qué entregar

Una entrega útil debe incluir resultado de `make test`, un cambio propio en `data/catalog_pairs.json` o `contracts/retrieval_policy.json`, una lectura de `Recall@k` y una decisión técnica sobre metadatos, OCR, reranking o revisión humana.

### Criterio de validación

El kit está completo cuando se puede descargar, extraer, ejecutar con `make run`, validar con `make test` y explicar sin depender de ninguna carpeta externa.
<!-- zip-quality-audit:end -->
