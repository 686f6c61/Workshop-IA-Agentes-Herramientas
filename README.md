# Workshop de IA para gente curiosa

De la neurona al agente: portada, 273 slides numeradas y cierre para entender la IA moderna y aplicarla con criterio en tu dia a dia. Desde backpropagation, busqueda heuristica, planning, SAT/CSP, ML clasico y ontologias hasta desplegar agentes en produccion, pasando por RAG, fine-tuning, MCP, ControlNet, Hugging Face, Google Colab, evals avanzadas, UX de IA, LLMOps, seguridad agentic, gobernanza, modelos open weights y vibe coding.

**[Ver presentacion](https://workshop-ia-2026.686f6c61.dev)** | Actualizado a mayo 2026 (update 05/26)

## Contenido

### Fundamentos (slides 2-27)
- [x] Que es (y que no es) la IA
- [x] Determinismo vs sistemas estocasticos
- [x] La neurona artificial, redes neuronales, backpropagation
- [x] Funciones de perdida, optimizadores (Adam, SGD)
- [x] CNNs para vision, RNNs y LSTMs para secuencias
- [x] Tokens, embeddings, similitud coseno
- [x] Entrenamiento vs inferencia, quantizacion (GGUF, bitsandbytes, GPTQ = GPT Quantization, AWQ = Activation-aware Weight Quantization, Q4-Q8)
- [x] ML clasico esencial: dataset, features, labels, train/test, overfitting y validacion
- [x] Supervisado vs no supervisado vs refuerzo; clasificacion vs regresion
- [x] Matriz de confusion, precision, recall, F1 y clustering/k-means

### IA clasica aplicada (slides 28-79)
- [x] Busqueda en espacios de estados: BFS, DFS, coste uniforme, greedy, A* y heuristicas admisibles
- [x] SAT y CSP: variables, dominios, restricciones, propagacion, backtracking y heuristicas
- [x] Planificacion automatica: estados, acciones, precondiciones, efectos, PDDL y planificacion heuristica
- [x] IA en juegos: minimax, poda alpha-beta, funciones de evaluacion, Monte Carlo y MCTS
- [x] Conocimiento simbolico: RDF, RDFS, OWL, SPARQL, Linked Data, ontologias y sistemas expertos
- [x] Puente practico entre IA clasica, agentes LLM, RAG, GraphRAG y validadores modernos

### Arquitecturas y modelos (slides 80-96)
- [x] LLMs, Transformers, Mixture of Experts, SSM (State Space Model)/Mamba, RWKV/RetNet, Hyena, Jamba y arquitecturas byte/latent
- [x] Dimensiones de modelos: parametros totales/activos, capas, hidden size, heads, context window
- [x] Estado del arte mayo 2026: GPT-5.5/5.4, Claude Opus 4.7, Gemini 3.1 Pro Preview (`gemini-3.1-pro-preview`), gpt-oss, Qwen3.6, DeepSeek-V4, Llama 4 y Mistral 3
- [x] Atencion en detalle: matrices Q, K, V, multi-head, RoPE
- [x] Tokenizacion en profundidad: BPE (Byte Pair Encoding), WordPiece, SentencePiece
- [x] Transfer learning: de ImageNet a GPT
- [x] Modelos multimodales nativos (texto + imagen + audio + video)
- [x] Parametros: temperature, top_p, top_k
- [x] Modelos de razonamiento (thinking tokens)
- [x] Open weights vs propietario, destilacion, inferencia optimizada
- [x] Edge AI: modelos en navegador, movil e IoT

### Uso practico (slides 97-152)
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

### Agentes y orquestacion (slides 153-191)
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

### Realidad de construir con IA (slides 192-217)
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

### Evals y medicion avanzada (slides 218-223)
- [x] Eval de RAG: retrieval, recall@k, MRR, nDCG, groundedness, answerability y abstencion
- [x] LLM-as-judge: rubricas, calibracion con humanos, evaluacion ciega, pares A/B y casos negativos
- [x] Eval de agentes: task success, tool success, coste, robustez, trazas y rollback
- [x] FinOps de IA: coste por tarea aceptada, routing barato/caro, cache, batch/flex y revision humana

### Producto y UX de IA (slides 224-228)
- [x] Disenar para incertidumbre: citas visibles, confianza accionable, abstencion y conflictos de fuentes
- [x] Aprobacion humana: preview, diff, confirmacion, permisos minimos, logs y rollback
- [x] Conversaciones recuperables: memoria visible/editable, limites, handoff a humano y recuperacion de errores

### Operar IA en produccion (slides 229-237)
- [x] LLMOps: control plane, runtime, observabilidad, evals y gobernanza
- [x] Serving open weights con vLLM, SGLang, TensorRT-LLM, llama.cpp y Ollama
- [x] Escalado de inferencia: continuous batching, KV cache, prefix caching, speculative decoding y chunked prefill
- [x] Routing, fallback y budgets por tarea segun riesgo, coste y dificultad
- [x] EvalOps: offline evals, shadow runs, canary releases, release gates y rollback
- [x] DataOps para IA: linaje, PII, licencias, calidad del corpus y drift
- [x] Post-training avanzado: SFT, DPO, RLHF/RLAIF, Constitutional AI, RFT con graders y RL verificable/RLVR

### Seguridad, gobernanza y confianza (slides 238-244)
- [x] Seguridad agentic: tools, MCP, permisos minimos, threat modeling, confused deputy, tool poisoning y exfiltracion
- [x] OWASP LLM Top 10 aplicado a controles, CI y datasets adversariales
- [x] Privacidad y private AI: API publica, VPC (Virtual Private Cloud), on-prem, despliegue hibrido, retencion y region
- [x] Gobernanza: EU AI Act, NIST AI RMF, NIST GenAI Profile e ISO/IEC 42001
- [x] Interpretabilidad: mechanistic interpretability, sparse autoencoders, features y limites de confianza

### Modelos open weights con Ollama Cloud (slides 245-251)
- [x] Ollama Cloud: modelos open weights sin GPU
- [x] Catalogo, setup, integracion con herramientas
- [x] Cloud vs local: cuando usar cada uno

### Laboratorios IA aplicada (slides 252-264)
- [x] A* con un problema pequeno y comparacion de coste, heuristica y nodos expandidos
- [x] Mini planner: tareas como estados, acciones, precondiciones y efectos
- [x] Clasificador simple con scikit-learn, train/test y matriz de confusion
- [x] K-means visual y criterios para no confiar en clusters
- [x] Ontologia pequena + SPARQL conectada con GraphRAG y RAG hibrido
- [x] Comparativa de una misma tarea con reglas, RAG y agente LLM

### Recursos y siguiente paso (slides 265-273 + cierre)
- [x] Recursos finales ampliados: mapa de estudio, papers, benchmarks, laboratorio practico, glosario en dos partes, checklist de exactitud, pipeline de entrega, contaminacion de benchmarks y ruta de 30 dias

Las secciones principales incluyen slides de recapitulacion con referencias cruzadas; el bloque final añade laboratorios, recursos, glosario ampliado, checklist de exactitud y ruta de 30 dias.

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
