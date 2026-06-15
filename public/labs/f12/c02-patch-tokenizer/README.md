# Kit F12 C02: de píxeles a patches

Este kit acompaña el capítulo 02 del facsímil 12. Construye una maqueta pequeña de lo que hace un encoder visual tipo Vision Transformer: toma una imagen, la divide en patches, calcula un embedding de juguete por patch y estima cuántos tokens visuales aparecen al cambiar resolución o tamaño de patch.

No usa un modelo real. Justo por eso es útil: puedes ver el mecanismo sin esconderlo detrás de una librería.

## Caso guía incluido

`data/resolution_cases.json` incluye comparaciones para una captura de beca completa (`captura_beca_larga_p16`) y para un recorte de alerta (`captura_beca_region_alerta_p16`). La pregunta práctica es deliberada: si la evidencia está en el aviso y el botón, quizá no necesitas mandar toda la pantalla.

## Ejecutar

```bash
make run
cat output/patch_report.md
```

Como gate:

```bash
make test
```

## Archivos

| Archivo | Papel |
|---|---|
| `data/synthetic_ticket.ppm` | Imagen sintética 8x8 en formato PPM ASCII. |
| `data/resolution_cases.json` | Casos de resolución y tamaño de patch para comparar coste. |
| `contracts/patch_policy.json` | Configuración del patch size, normalización y gates. |
| `ops/inspect_patches.py` | Script que divide la imagen, calcula tokens y genera el reporte. |
| `output/patch_report.json` | Evidencia estructurada. |
| `output/patch_report.md` | Informe humano. |
| `output/patch_grid.svg` | Visualización de la rejilla de patches. |
| `templates/entrega.md` | Plantilla para adaptar el ejercicio. |

## Qué deberías mirar

1. `visual_token_count`: cuántos tokens visuales salen de la imagen.
2. `attention_pairs`: cómo crece el coste si todos los tokens atienden a todos.
3. `patches`: qué resume cada patch y qué pierde.
4. `resolution_budgets`: qué ocurre al subir resolución o cambiar `patch_size`.
5. `patch_grid.svg`: si mirando la rejilla todavía se intuye la información importante.

## Qué entregaría un alumno

1. `output/patch_report.md`.
2. `output/patch_grid.svg`.
3. Una variante propia de `data/resolution_cases.json` o `data/synthetic_ticket.ppm`.
4. Una decisión técnica: más resolución, patches más pequeños, recorte, OCR previo o representación más barata.

## Qué te llevas

Te llevas una práctica ejecutable para entender que una imagen no entra “como imagen” al modelo. Primero se convierte en una secuencia de piezas. Cada pieza resume una región, ocupa un token visual y participa en atención. Si duplicas tokens, no solo duplicas coste: en atención completa puedes multiplicar pares de interacción.

## Variantes para hacerlo tuyo

- Cambia `patch_size` en `contracts/patch_policy.json` de `2` a `4` y compara tokens visuales.
- Añade una nueva resolución en `data/resolution_cases.json`, por ejemplo una foto de móvil o una página escaneada.
- Compara `captura_beca_larga_p16` contra `captura_beca_region_alerta_p16` y calcula cuántos tokens visuales te ahorra el recorte.
- Edita `data/synthetic_ticket.ppm` para poner el aviso rojo en otra zona y observa qué patch lo captura.
- Usa `output/patch_grid.svg` para explicar qué se pierde cuando una región se resume demasiado.
- Completa `templates/entrega.md` con una decisión de diseño.

## Rúbrica rápida

| Nivel | Qué demuestra |
|---|---|
| Mínimo | Ejecuta `make run` y `make test`, abre `output/patch_grid.svg` y explica cuántos tokens visuales hay. |
| Bueno | Cambia resolución o patch size y compara tokens, atención y pérdida de detalle. |
| Excelente | Propone una política de preprocesado para un caso real: recorte, OCR, resolución, patch size y métrica de evaluación. |

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `Kit F12 C02: de píxeles a patches`, no escondido en una ruta del repositorio.

### Qué contiene

- `README.md`: esta guía y la explicación del ejercicio.
- `Makefile`: entrada única para ejecutar y validar el kit con `make run` y `make test`.
- `requirements.txt`: dependencias declaradas; este kit usa la biblioteca estándar de Python.
- `data/synthetic_ticket.ppm`: imagen sintética.
- `data/resolution_cases.json`: escenarios de resolución.
- `contracts/patch_policy.json`: contrato de ejecución.
- `ops/inspect_patches.py`: código ejecutable.
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

- `output/patch_report.md`: informe humano.
- `output/patch_report.json`: evidencia estructurada.
- `output/patch_grid.svg`: visualización de patches.

### Qué entregar

Una entrega útil debe incluir el resultado de `make test`, el SVG generado, una modificación razonada y una decisión técnica sobre resolución, patch size, recorte u OCR.

### Criterio de validación

El kit está completo cuando se puede descargar, extraer, ejecutar con `make run`, validar con `make test` y explicar sin depender de ninguna carpeta externa.
<!-- zip-quality-audit:end -->
