# Workshop de IA para gente curiosa

De la neurona al agente: portada, 408 slides numeradas y cierre para entender la IA moderna y aplicarla con criterio en tu dia a dia. Desde backpropagation, busqueda heuristica, planning, SAT/CSP, ML clasico, complejidad temporal, incertidumbre, causalidad, interpretabilidad, refuerzo formal, privacidad avanzada y ontologias hasta desplegar agentes en produccion, pasando por Transformers por dentro, RAG, RAG multimodal, fine-tuning, MCP, ControlNet, Hugging Face, Google Colab, evals avanzadas, Agent Workbench, computer-use, load testing LLM, red-team tooling, UX de IA, LLMOps, seguridad agentic, gobernanza, modelos open weights y vibe coding.

**[Ver presentacion](https://workshop-ia-2026.686f6c61.dev)** | Actualizado a mayo 2026 (update 05/26)

## Contenido

### Fundamentos (slides 1-36)
- [x] Que es (y que no es) la IA
- [x] Determinismo vs sistemas estocasticos
- [x] La neurona artificial, redes neuronales, backpropagation, regla de la cadena, símbolos y ejemplo numérico con gradientes
- [x] Funciones de perdida, optimizadores (Adam, SGD)
- [x] CNNs para vision, RNNs y LSTMs para secuencias
- [x] Tokens, embeddings, similitud coseno
- [x] Entrenamiento vs inferencia, quantizacion (GGUF, bitsandbytes, GPTQ = GPT Quantization, AWQ = Activation-aware Weight Quantization, Q4-Q8)
- [x] ML clasico esencial: dataset, features, labels, train/test, overfitting y validacion
- [x] Supervisado vs no supervisado vs refuerzo; clasificacion vs regresion
- [x] Complejidad temporal en ML: Big-O, entrenamiento vs inferencia y coste por algoritmo
- [x] Matriz de confusion, precision, recall, F1 y clustering/k-means

### IA clasica aplicada (slides 37-88)
- [x] Busqueda en espacios de estados: BFS, DFS, coste uniforme, greedy, A* y heuristicas admisibles
- [x] SAT y CSP: variables, dominios, restricciones, propagacion, backtracking y heuristicas
- [x] Planificacion automatica: estados, acciones, precondiciones, efectos, PDDL y planificacion heuristica
- [x] IA en juegos: minimax, poda alpha-beta, funciones de evaluacion, Monte Carlo y MCTS
- [x] Conocimiento simbolico: RDF, RDFS, OWL, SPARQL, Linked Data, ontologias y sistemas expertos
- [x] Puente practico entre IA clasica, agentes LLM, RAG, GraphRAG y validadores modernos

### Arquitecturas y modelos (slides 89-117)
- [x] LLMs, Transformers, Mixture of Experts, SSM (State Space Model)/Mamba, RWKV/RetNet, Hyena, Jamba y arquitecturas byte/latent
- [x] Dimensiones de modelos: parametros totales/activos, capas, hidden size, heads, context window
- [x] Estado del arte mayo 2026: GPT-5.5/5.4, Claude Opus 4.7, Gemini 3.1 Pro Preview (`gemini-3.1-pro-preview`), gpt-oss, Qwen3.6, DeepSeek-V4, Llama 4 y Mistral 3
- [x] Atencion en detalle: matrices Q, K, V, multi-head, RoPE
- [x] Tokenizacion en profundidad: BPE (Byte Pair Encoding), WordPiece, SentencePiece
- [x] Transformer Explainer como laboratorio visual: texto a tensores, embeddings, QKV, mascara causal, softmax, MLP, residual, LayerNorm, logits y sampling
- [x] Transfer learning: de ImageNet a GPT
- [x] Modelos multimodales nativos (texto + imagen + audio + video)
- [x] Parametros: temperature, top_p, top_k
- [x] Modelos de razonamiento (thinking tokens)
- [x] Open weights vs propietario, destilacion, inferencia optimizada
- [x] Edge AI: modelos en navegador, movil e IoT

### Uso practico (slides 118-181)
- [x] Prompt engineering y context engineering
- [x] Alucinaciones y como protegerte
- [x] Structured output / JSON mode con schema
- [x] Vision, multimodalidad, voz en tiempo real (OpenAI Realtime, ElevenLabs)
- [x] Generacion de imagenes: difusion, latent space, CFG
- [x] Entrenamiento de imagen: LoRA, DreamBooth, Textual Inversion
- [x] Herramientas: ComfyUI, Forge, Civitai, Replicate, RunPod
- [x] Tecnicas de control: ControlNet, IP-Adapter, inpainting, upscaling
- [x] Hugging Face + LM Studio: model cards, licencias, calculo RAM/VRAM, formatos y quantizaciones
- [x] Caso real DeepSeek-V4 Pro/Flash: MoE, parametros totales/activos, FP4+FP8 mixed, 1M context, eval results y terminos explicados
- [x] Glosario de fichas de Hugging Face: base, instruct, adapter, LoRA, merge, safetensors, GGUF, gated, chat template
- [x] Benchmarks en model cards: EM, Pass@1, Resolved, Acc, F1, Elo/rating y setup de evaluacion
- [x] Metodologia para mantenerse actualizado sin comprar humo
- [x] Matriz de eleccion de modelos segun coste, privacidad, contexto, tools y riesgo
- [x] Mini-lab de Hugging Face para decidir si una model card sirve
- [x] Google Colab para probar experimentos, entender limitaciones, usar repos de referencia y entregar notebooks reproducibles
- [x] Checklist de experimentos buenos, eval interna y errores comunes
- [x] RAG, agentic RAG, GraphRAG, hybrid search, contextual retrieval
- [x] RAG semantico: RAG no es una ontologia, knowledge graph vs vector store, RDF/OWL/SPARQL vs embeddings y cuando usar enfoque vectorial, semantico o hibrido
- [x] Decision fine-tuning: cuando si, cuando no y cuando es mejor RAG/prompt/cambiar de modelo
- [x] Fine-tuning con LoRA/QLoRA (Unsloth, Axolotl)
- [x] Datos sinteticos, bases de datos vectoriales
- [x] Text-to-SQL, prompt caching, context window
- [x] API hello world, streaming (SSE)
- [x] Arquitectura de apps con LLM: retry, fallback, circuit breaker, model routing

### Agentes y orquestacion (slides 182-229)
- [x] Cuando usar un agente y cuando un prompt
- [x] Bucle ReAct, Plan-and-Execute, Reflexion
- [x] Agente clasico vs moderno: estado/contexto, acciones/tools, precondiciones/schemas, planner/LLM y motor de inferencia
- [x] Arquitecturas documentadas en SVG: ReAct, ReWOO, Reflexion, manager/supervisor, handoffs y workflow critic
- [x] Memoria persistente: CLAUDE.md, Zep, MemGPT
- [x] Function calling (tool use) con ejemplo completo
- [x] Patrones: chaining, routing, paralelizacion, orchestrator-workers
- [x] Harness Engineering: entorno ejecutable del agente, capas de control, guias, sensores, plantilla operativa, reglas de mercado, metricas, safety, guardrails, trazas y ciclo de mejora
- [x] Orquestadores: LangGraph, CrewAI, Claude Agent SDK, Google ADK (Agent Development Kit), Mastra
- [x] Claude Code: rules, skills, hooks, MCPs, subagentes, plugins
- [x] Coding agents: Claude Code, Devin, OpenHands, Aider, Codex CLI
- [x] MCP: concepto (el "USB de la IA") + servidor minimo en TypeScript
- [x] Computer Use, Browser Use, A2A (Agent-to-Agent)
- [x] Human-in-the-loop: niveles de autonomia

### Realidad de construir con IA (slides 230-256)
- [x] IDE web vs terminal, comparativa de coding assistants
- [x] Benchmarks: que miden, que no miden, SWE-bench, leaderboards y evals internas
- [x] SWE-bench: Full, Verified, Lite (534), Multilingual, Multimodal (100 dev / 500 test), % Resolved, contaminacion, SWE-bench Pro y coste por resolucion
- [x] Precios y cambios actuales en herramientas de coding: Claude Code, Cursor, Copilot y Windsurf
- [x] IA en CI/CD, seguridad (OWASP Top 10 for LLMs), guardrails
- [x] Testing adversarial, red teaming, prompt injection
- [x] EU AI Act: clasificacion por riesgo, calendario
- [x] Costes comparados por tokens: Claude, GPT, Qwen, DeepSeek, GLM/Z.AI, cache, thinking y región
- [x] Prompts como codigo: versionado, evals, A/B testing
- [x] Testing de codigo generado: mutation testing, property-based
- [x] Vibe coding con disciplina
- [x] Configurar Claude Code, OpenCode y Cursor como un pro
- [x] Agentes en produccion: lecciones aprendidas y el "agent tax"

### Evals y medicion avanzada (slides 257-262)
- [x] Eval de RAG: retrieval, recall@k, MRR, nDCG, groundedness, answerability y abstencion
- [x] LLM-as-judge: rubricas, calibracion con humanos, evaluacion ciega, pares A/B y casos negativos
- [x] Eval de agentes: task success, tool success, coste, robustez, trazas y rollback
- [x] FinOps de IA: coste por tarea aceptada, routing barato/caro, cache, batch/flex y revision humana

### Incertidumbre y decision (slides 263-273)
- [x] Calibracion: confidence vs probabilidad real, reliability diagrams, Expected Calibration Error (ECE), Brier score y log loss
- [x] Politicas de decision: umbrales, abstencion, revision humana y coste esperado
- [x] Conformal prediction en regresion y clasificacion: intervalos, conjuntos de clases y limites practicos
- [x] Incertidumbre en LLMs y RAG: retrieval score, groundedness, answerability, schemas, eval historica y rutas de escalado

### Data-centric AI (slides 274-285)
- [x] Dataset como producto: owner, version, contrato, linaje, unidad de dato, target y ventana temporal
- [x] Calidad de etiquetas: ruido, desacuerdo, label delay, sesgo de proceso, guias de anotacion, gold set y adjudicacion
- [x] Tests de datos, leakage avanzado, drift, representatividad, active learning y weak supervision
- [x] Datasheets y dataset cards: composicion, recogida, anotacion, usos recomendados/no recomendados y riesgos

### Causalidad y experimentacion (slides 286-296)
- [x] Correlacion vs causalidad, DAGs, confounders, colliders, ajuste y operador do(X)
- [x] Contrafactuales, A/B testing, ATE, guardrails, sample ratio mismatch, peeking, novelty effect e interferencia
- [x] Uplift modeling y treatment effect para decidir en quien una accion cambia realmente el resultado

### Interpretabilidad practica (slides 297-307)
- [x] Interpretabilidad global, local y segmentada; feature importance interna y permutation importance
- [x] PDP, ICE, ALE, SHAP, LIME, contraejemplos y ejemplos similares, explicados con limites
- [x] Interpretabilidad no causal, error slicing y trazas de LLM/agentes para depurar comportamiento real

### Refuerzo formal (slides 308-318)
- [x] Reinforcement Learning formal: agente, entorno, estado, accion, recompensa y politica
- [x] MDP: S, A, P, R, gamma, politica, retorno, descuento, V(s), Q(s,a) y ecuacion de Bellman
- [x] Exploration vs exploitation, bandits, reward hacking y conexion con RLHF, RLAIF, Constitutional AI, RFT y RLVR

### Privacidad avanzada (slides 319-330)
- [x] PII, datos sensibles, secretos, quasi-identifiers, anonimizacion, pseudonimizacion y reidentificacion
- [x] Differential privacy: epsilon, delta, ruido, composicion, DP-SGD y evaluacion de privacidad
- [x] Federated learning, confidential computing, memorization, extraction attacks, RAG leakage, retencion y contratos

### Producto y UX de IA (slides 331-335)
- [x] Disenar para incertidumbre: citas visibles, confianza accionable, abstencion y conflictos de fuentes
- [x] Aprobacion humana: preview, diff, confirmacion, permisos minimos, logs y rollback
- [x] Conversaciones recuperables: memoria visible/editable, limites, handoff a humano y recuperacion de errores

### Operar IA en produccion (slides 336-344)
- [x] LLMOps: control plane, runtime, observabilidad, evals y gobernanza
- [x] Serving open weights con vLLM, SGLang, TensorRT-LLM, llama.cpp y Ollama
- [x] Escalado de inferencia: continuous batching, KV cache, prefix caching, speculative decoding y chunked prefill
- [x] Routing, fallback y budgets por tarea segun riesgo, coste y dificultad
- [x] EvalOps: offline evals, shadow runs, canary releases, release gates y rollback
- [x] DataOps para IA: linaje, PII, licencias, calidad del corpus y drift
- [x] Post-training avanzado: SFT, DPO, RLHF/RLAIF, Constitutional AI, RFT con graders y RL verificable/RLVR

### Seguridad, gobernanza y confianza (slides 345-351)
- [x] Seguridad agentic: tools, MCP, permisos minimos, threat modeling, confused deputy, tool poisoning y exfiltracion
- [x] OWASP LLM Top 10 aplicado a controles, CI y datasets adversariales
- [x] Privacidad y private AI: API publica, VPC (Virtual Private Cloud), on-prem, despliegue hibrido, retencion y region
- [x] Gobernanza: EU AI Act, NIST AI RMF, NIST GenAI Profile e ISO/IEC 42001
- [x] Interpretabilidad: mechanistic interpretability, sparse autoencoders, features y limites de confianza

### Modelos open weights con Ollama Cloud (slides 352-358)
- [x] Ollama Cloud: modelos open weights sin GPU
- [x] Catalogo, setup, integracion con herramientas
- [x] Cloud vs local: cuando usar cada uno

### Laboratorios IA aplicada (slides 359-371)
- [x] A* con un problema pequeno y comparacion de coste, heuristica y nodos expandidos
- [x] Mini planner: tareas como estados, acciones, precondiciones y efectos
- [x] Clasificador simple con scikit-learn, train/test y matriz de confusion
- [x] K-means visual y criterios para no confiar en clusters
- [x] Ontologia pequena + SPARQL conectada con GraphRAG y RAG hibrido
- [x] Comparativa de una misma tarea con reglas, RAG y agente LLM

### Ingenieria avanzada de IA aplicada (slides 372-399)
- [x] Agent Workbench: instrucciones, estado, scope, tools, feedback, verificacion y handoff
- [x] Workbench minimo: AGENTS.md, agent_state.json, task_board.json y trazas operativas
- [x] RAG multimodal y vision-native RAG: PDFs visuales, ColPali, late interaction, MaxSim y coste de almacenamiento
- [x] Retrieval cross-modal: texto, imagen, audio, video, fusion de senales y grounding verificable
- [x] Computer-use: GUI grounding, action schemas, screenshots, DOM, accessibility tree y benchmarks
- [x] Load testing LLM: TTFT, TPOT, ITL, goodput, P95/P99, distribucion realista de prompts y patrones steady/ramp/spike/soak
- [x] Red-team tooling: campanas repetibles, Llama Guard, Garak, PyRIT, scoring y regresion de seguridad
- [x] Labs Build It / Use It / Ship It: workbench minimo, RAG multimodal y prueba de carga/red-team

### Recursos y siguiente paso (slides 400-408 + cierre)
- [x] Recursos finales ampliados: mapa de estudio, papers, benchmarks, laboratorio practico, glosario en dos partes, checklist de exactitud, pipeline de entrega, contaminacion de benchmarks y ruta de 30 dias

Las secciones principales incluyen slides de recapitulacion con referencias cruzadas; el bloque final añade laboratorios, ingenieria avanzada, recursos, glosario ampliado, checklist de exactitud y ruta de 30 dias.

## Arrancar en local

```bash
git clone https://github.com/686f6c61/Workshop-IA-Agentes-Herramientas.git
cd Workshop-IA-Agentes-Herramientas
npm install
npm run dev
```

## Build y deploy

```bash
npm run build    # genera dist/
npm run preview  # preview local del build
```

Deploy automatico en Coolify usando el `Dockerfile`. Cada push a `main` redespliega el servicio conectado al repo. El `render.yaml` se mantiene como configuracion estatica alternativa para Render.

## Stack

- Astro 6 (static site)
- Lucide Icons (CDN)
- Space Grotesk + IBM Plex Mono
- Google Analytics + Search Console
- Coolify en VPS (Docker + nginx)

## Autor

[686f6c61](https://github.com/686f6c61)

## Licencia

MIT
