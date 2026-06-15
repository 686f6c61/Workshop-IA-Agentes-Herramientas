# Decisión de arquitectura

Este informe no elige modelo por moda. Elige una primera arquitectura por forma de datos, restricciones y coste aproximado.

## vision_defects_edge: Control visual de piezas en una línea de fabricación

- Entrada: `image_grid`.
- Despliegue: `edge_gpu`.
- Recomendación: **CNN**.
- Riesgos: sin bloqueos iniciales.
- Candidatos revisados:
  - `CNN`: la entrada tiene estructura de rejilla y patrones locales.
  - `Vision Transformer`: posible si hay muchos datos y GPU, pero suele ser más caro al inicio.

## maintenance_sensor: Predicción de fallo con señales de sensores

- Entrada: `time_series`.
- Despliegue: `edge_cpu`.
- Recomendación: **LSTM/GRU o 1D CNN temporal**.
- Riesgos: sin bloqueos iniciales.
- Candidatos revisados:
  - `LSTM/GRU`: la secuencia es corta y el despliegue edge penaliza atención cuadrática.
  - `1D CNN temporal`: buena alternativa si importan patrones locales y latencia baja.

## support_ticket_short_text: Clasificación de tickets de soporte cortos

- Entrada: `text_sequence`.
- Despliegue: `cloud_cpu`.
- Recomendación: **Embedding + clasificador, comparado contra Transformer pequeño**.
- Riesgos: sin bloqueos iniciales.
- Candidatos revisados:
  - `Embedding + clasificador lineal`: para texto corto y pocas clases puede bastar antes de usar un LLM.
  - `Transformer pequeño`: útil si el orden y el contexto completo cambian la etiqueta.

## legal_contract_review: Revisión de contratos largos con referencias cruzadas

- Entrada: `long_text`.
- Despliegue: `cloud_gpu`.
- Recomendación: **Transformer con RAG o chunking**.
- Riesgos: pocos_ejemplos_para_deep_learning, atencion_cuadratica_cara.
- Candidatos revisados:
  - `Transformer con RAG/chunking`: el texto largo exige recuperar o trocear antes de pasar todo al contexto.
  - `Clasificador por recuperación de fragmentos`: si hay pocos ejemplos, conviene recuperar pasajes relevantes y clasificar sobre evidencias antes de entrenar.
