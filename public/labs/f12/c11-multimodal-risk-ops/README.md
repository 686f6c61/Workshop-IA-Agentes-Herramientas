# F12 C11 · Multimodal Risk Ops

Este laboratorio acompaña el capítulo 11 del facsímil 12. Simula un gate de privacidad, seguridad y operación para entradas multimodales: documentos, imágenes, audio, vídeo, RAG, datasets de evaluación y trazas de pantalla.

La idea no es “pasar un detector de PII y ya está”. La idea es decidir qué se redacta, qué se conserva, qué destino puede recibir cada artefacto, qué acción necesita aprobación y qué caso bloquea publicación.

## Ejecutar

Desde la carpeta extraída del ZIP:

```bash
make run
make test
```

## Casos incluidos

| Caso | Modalidad | Qué fuerza a practicar |
|---|---|---|
| `doc_dni_invoice` | Documento | OCR, DNI, correo y redacción por campo. |
| `image_badge_face` | Imagen | Cara, ID visible, metadatos y redacción por región. |
| `audio_phone_slot` | Audio | Transcript con teléfono y confirmación de slot. |
| `video_license_plate` | Vídeo | Matrícula, frame y controles faltantes. |
| `rag_confidential_slide` | RAG | Fuente interna y claim sensible no redactado. |
| `ui_api_key_prompt_injection` | UI trace | API key y prompt injection visual/OCR. |
| `computer_use_external_submit` | UI trace | Egress policy y aprobación antes de salida externa. |
| `eval_dataset_student_email` | Dataset eval | Convertir fallo real en fixture redactado. |
| `image_exif_location` | Imagen | Metadatos EXIF con GPS y dirección visible. |
| `low_res_ocr_missed_dni` | Documento | OCR de baja confianza y falso negativo de identificador. |
| `audio_noise_health_hint` | Audio | Dato sanitario en transcript con ruido. |
| `eval_reconstructible_token_fragment` | Dataset eval | Fragmento de token y cookie que no deben entrar al fixture. |
| `reflection_face_in_public_photo` | Imagen | Cara reflejada en una foto aparentemente pública. |
| `public_product_photo` | Imagen pública | Caso de bajo riesgo que debe pasar. |

## Qué genera

| Archivo | Qué contiene |
|---|---|
| `output/risk_report.md` | Informe humano por caso y modalidad. |
| `output/risk_report.json` | Informe estructurado para CI o auditoría. |
| `output/risk_matrix.csv` | Matriz con riesgo, decisión, fallos y siguiente acción. |
| `output/redaction_plan.csv` | Entidad, ubicación y operador recomendado. |
| `output/retention_matrix.csv` | Retención por caso y tipo de storage. |
| `output/threat_model.csv` | Activo, frontera de confianza, fallo, control y prueba por caso. |
| `output/artifact_lineage.csv` | Hash, owner, destino, storage, versión de detector y política. |
| `output/artifact_lineage.jsonl` | El mismo lineage en formato cómodo para SIEM o pipeline. |
| `output/policy_decisions.md` | Lectura humana de las decisiones de policy-as-code. |
| `output/policy_decisions.csv` | Decisiones `allow`, `review` y `deny` para inputs tipo OPA/Cedar. |
| `output/detector_eval_report.md` | Informe de precision, recall, falsos positivos y falsos negativos. |
| `output/detector_metrics.csv` | Métricas por tipo de entidad. |
| `output/detector_samples.csv` | Muestras concretas que necesitan revisión. |
| `output/incident_runbook.md` | Runbook para secretos, PII, OCR malicioso y salida externa. |
| `output/multimodal_risk_gate.svg` | Figura generada con firma del proyecto. |

## Qué deberías tocar

1. Abre `data/multimodal_risk_cases.json`.
2. Revisa `ui_api_key_prompt_injection` y mira por qué bloquea.
3. Revisa `video_license_plate` y localiza qué control falta.
4. Ejecuta `make run`.
5. Abre `output/risk_matrix.csv`.
6. Abre `output/redaction_plan.csv`.
7. Abre `output/threat_model.csv` y comprueba qué frontera cruza cada modalidad.
8. Abre `output/detector_eval_report.md` y localiza al menos un falso negativo.
9. Abre `output/policy_decisions.md` y compara `allow`, `review` y `deny`.
10. Abre `output/artifact_lineage.csv` y comprueba que cada caso tenga hash, policy y retención.
11. Abre `output/incident_runbook.md`.
12. Añade un caso realista de tu producto.
13. Cambia `contracts/multimodal_risk_policy.json` para añadir un destino bloqueado.
14. Ejecuta otra vez y justifica la nueva decisión en `templates/entrega.md`.

## Qué te llevas

Te llevas un patrón de ingeniería: antes de enviar o conservar una entrada multimodal, clasifica entidades, etiqueta contenido no confiable, decide operador de redacción, limita destinos, define retención y genera evidencia de release.

El artefacto reutilizable es el contrato `contracts/multimodal_risk_policy.json` más el runner `ops/run_multimodal_risk_gate.py`. Puedes cambiar los casos y conservar el mismo flujo para una práctica, un equipo de producto o un gate de CI.

Si trabajas con un equipo de plataforma, mira también `policies/egress_policy.rego` y `policies/egress_policy.cedar`. No están ahí como decoración: representan cómo llevar una decisión del capítulo a policy-as-code. La aplicación prepara un input estructurado; la política decide si permite, revisa o deniega; el runner guarda evidencia.

## Variantes para hacerlo tuyo

1. Añade una modalidad nueva, por ejemplo `medical_image` o `screen_recording`.
2. Añade una entidad nueva en `entity_sensitivity`, por ejemplo `BANK_ACCOUNT` o `ADDRESS`.
3. Endurece `approved_destinations` y comprueba qué casos pasan de `review` a `block`.
4. Cambia la retención de `eval_case_redacted` y explica por qué.
5. Añade un caso donde una imagen no tenga PII, pero sí instrucciones visuales maliciosas.
6. Añade una muestra nueva en `data/detector_eval_cases.json` y mide cómo cambia el recall.
7. Añade una decisión en `data/policy_decision_examples.json` para una tool real de tu producto.

## Rúbrica rápida

| Nivel | Qué debe entregar |
|---|---|
| Mínimo | Ejecuta `make run`, ejecuta `make test` y explica un caso `pass`, uno `review` y uno `block`. |
| Bueno | Añade un caso nuevo, define entidades, controles, retención y threat model, y justifica la decisión del gate. |
| Excelente | Modifica la política, compara antes/después, mide detectores, revisa lineage y deja un runbook concreto para el riesgo más alto. |

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `F12 C11 · Multimodal Risk Ops`.

### Qué contiene

- `README.md`: esta guía.
- `Makefile`: entrada única para ejecutar y validar.
- `requirements.txt`: dependencias declaradas; usa biblioteca estándar.
- `contracts/multimodal_risk_policy.json`: gates, entidades, operadores, destinos y retención.
- `data/multimodal_risk_cases.json`: casos multimodales auditables.
- `data/detector_eval_cases.json`: gold labels y detecciones simuladas para medir detectores.
- `data/policy_decision_examples.json`: inputs de autorización para policy-as-code.
- `policies/egress_policy.rego`: ejemplo Rego para OPA.
- `policies/egress_policy.cedar`: ejemplo Cedar para autorización fina.
- `schemas/risk_case_schema.json`: contrato mínimo de caso.
- `ops/run_multimodal_risk_gate.py`: auditor ejecutable.
- `templates/entrega.md`: plantilla de entrega.
- `tests/test_multimodal_risk_gate.py`: tests de reproducibilidad.
- `output/`: salidas generadas o esperadas.

### Ejecutar desde cero

```bash
make run
make test
```

### Qué mirar antes de entregar

- `output/risk_report.md`
- `output/risk_matrix.csv`
- `output/redaction_plan.csv`
- `output/retention_matrix.csv`
- `output/threat_model.csv`
- `output/artifact_lineage.csv`
- `output/policy_decisions.md`
- `output/detector_eval_report.md`
- `output/incident_runbook.md`
- `output/multimodal_risk_gate.svg`

### Criterio de validación

El kit está completo cuando se puede descargar, extraer, ejecutar con `make run`, validar con `make test` y explicar por qué cada caso pasa, queda en revisión o bloquea publicación.
<!-- zip-quality-audit:end -->
