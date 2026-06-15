# Revisión de herramientas de mercado por capa

Este documento no recomienda una compra automática. Ordena herramientas por la decisión técnica que cubren y por la evidencia que debería quedar si se usan.

## Evaluación offline y CI

| Herramienta | Capa | Qué hace | Cuándo usarla | Límite de ingeniería | Evidencia |
|---|---|---|---|---|---|
| [Promptfoo](https://www.promptfoo.dev/docs/red-team/quickstart/) | offline_eval | Genera y ejecuta escenarios contra API, RAG, agentes, scripts y proveedores. | Cuando hay endpoint o harness y quieres pruebas repetibles en CI. | La calidad depende de definir bien purpose, usuarios, datos y acciones permitidas. | config usada; target; dataset generado; resultados; issues revisados |
| [Garak](https://docs.garak.ai/garak/llm-scanning-basics/setting-up) | offline_eval | CLI Python para escanear modelos y sistemas conversacionales. | Cuando necesitas comparativas rápidas entre endpoints o modelos. | No sustituye escenarios propios de negocio ni gates de tools. | versión; probes; detector; target; reporte |
| [Microsoft PyRIT](https://github.com/microsoft/PyRIT) | offline_eval | Framework programable para identificar riesgos en sistemas generativos. | Cuando necesitas campañas multi-turn, scorers propios y targets personalizados. | Requiere diseñar objetivos, datasets, scorers y trazabilidad. | notebooks/scripts; scorers; prompts; resultados; revisión humana |
| [Giskard](https://docs.giskard.ai/hub/sdk/guides/scans) | offline_eval | Scans automatizados contra agentes con categorías OWASP LLM Top 10 2025 y reporting. | Cuando quieres una plataforma con scans, tags y grado agregado. | La nota global no explica todos los riesgos; hay que abrir categorías y falsos positivos. | scan_id; grade; tags; categorías; hallazgos aceptados o corregidos |

## Guardrails runtime

| Herramienta | Capa | Qué hace | Cuándo usarla | Límite de ingeniería | Evidencia |
|---|---|---|---|---|---|
| [OpenAI Guardrails Python](https://openai.github.io/openai-guardrails-python/quickstart/) | runtime_guardrail | Cliente con validación preflight, input, output y tool guardrails en Agents SDK. | Cuando el stack usa OpenAI o APIs compatibles y quieres controles de cliente. | Mide fail-safe/fail-secure, coste en tokens y efecto sobre historial. | config; resultados por etapa; token usage; tripwires; dataset de evaluación |
| [Lakera Guard](https://docs.lakera.ai/docs/prompt-defense) | runtime_guardrail | API especializada en prompt defense con soporte multilingüe. | Cuando necesitas detector dedicado en entrada o contenido externo. | No decide ACL, scopes, egress ni permisos de tool. | decisión; score; idioma; payload minimizado; latencia |
| [NVIDIA NeMo Guardrails](https://docs.nvidia.com/nemo/guardrails/0.14.0/index.html) | runtime_guardrail | Toolkit open source para rails programables, flujos y tools. | Cuando quieres controlar conversación y acciones con flujos programables. | Requiere modelar flujos y acciones; no basta con filtros de texto. | colang/config; rails activados; acciones; logs de flujo |
| [Guardrails AI](https://guardrailsai.com/guardrails/docs/concepts/guard) | runtime_guardrail | Valida salidas con Guard, parse, validators y reasks opcionales. | Cuando necesitas validación de salida estructurada o postprocesado. | Las reasks pueden sumar latencia y coste; fija cuándo se permiten. | validated_output; validation_passed; history; reasks |

## Gateways y proxies de IA

| Herramienta | Capa | Qué hace | Cuándo usarla | Límite de ingeniería | Evidencia |
|---|---|---|---|---|---|
| [LiteLLM Proxy](https://docs.litellm.ai/) | llm_gateway | Proxy compatible con muchos proveedores, logging, coste y rate limiting. | Cuando varios equipos consumen modelos y necesitas control centralizado. | No sustituye la autorización fina de negocio ni el schema de tools. | config; virtual keys; budgets; rate limits; logs redactados |
| [Portkey AI Gateway](https://portkey.ai/docs/product/ai-gateway) | llm_gateway | Gateway con routing, cache, MCP support, fallbacks, retries, circuit breakers y budgets. | Cuando quieres capa central de rutas, coste, resiliencia y modelos permitidos. | Debe integrarse con IAM y policy de aplicación; no basta como frontera única. | gateway config; rutas; fallback; budgets; status codes |
| [Portkey Guardrails](https://portkey.ai/docs/product/guardrails) | llm_gateway_guardrail | Guardrails en gateway para inputs u outputs con acciones de negar, loggear, retry o fallback. | Cuando el tráfico ya pasa por gateway y quieres controles en request/response. | Revisa streaming, latencia, logs y si el check ve todo el contexto que necesita. | guardrail config; hook results; logs; decision; fallback |

## Observabilidad y evals continuas

| Herramienta | Capa | Qué hace | Cuándo usarla | Límite de ingeniería | Evidencia |
|---|---|---|---|---|---|
| [Langfuse](https://langfuse.com/docs/metrics/overview) | observability | Métricas desde trazas de observabilidad y evaluación: calidad, coste, latencia, volumen, usuarios, tags y versiones. | Cuando necesitas reconstruir runs, comparar releases y crear datasets desde fallos. | Una traza no arregla el sistema; hay que convertir hallazgos en tests y cambios. | trace_id; scores; model; prompt version; tool calls; retrieval ids |

## Policy-as-code y autorización

| Herramienta | Capa | Qué hace | Cuándo usarla | Límite de ingeniería | Evidencia |
|---|---|---|---|---|---|
| [Open Policy Agent](https://www.openpolicyagent.org/docs/latest/) | policy_as_code | Motor general de policy-as-code para externalizar decisiones. | Cuando quieres evaluar permisos de tools y recursos como datos estructurados. | Necesita modelo de datos y pruebas de policy; no razona con lenguaje natural por sí mismo. | policy; input; decision; tests; version |
| [Cedar](https://docs.cedarpolicy.com/) | policy_as_code | Lenguaje de políticas de autorización para expresar permisos de aplicación. | Cuando quieres permisos finos por principal, acción, recurso y contexto. | Requiere modelar entidades, acciones y recursos con precisión. | policy set; PARC/PARX input; decision; tests; version |

## Decisión mínima

Para una aplicación LLM con RAG y tools, la combinación mínima razonable sería:

1. Un gate offline con escenarios propios.
2. Un control runtime para entradas, salidas o tool calls de mayor riesgo.
3. Un gateway o proxy si hay varios equipos, modelos o presupuestos.
4. Observabilidad con trazas de tool, RAG y policy versión.
5. Autorización estructurada para acciones reales.

Si falta el punto 5, el sistema puede parecer protegido, pero seguirá dejando la decisión de permisos demasiado cerca del texto generado.
