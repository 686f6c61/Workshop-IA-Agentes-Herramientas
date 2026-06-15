# Glosario: Inteligencia artificial para gente curiosa

## A

**Acción.** Operación disponible en un problema de planificación que puede cambiar el estado si sus precondiciones se cumplen. (Fasc. 2, cap. 9)

**Alucinación.** Fenómeno por el cual un LLM genera información sintácticamente correcta pero factualmente falsa, expresada con total seguridad. No es un *bug*: es una propiedad emergente de la predicción estadística. (Cap. 1)

**Auditoría.** Registro revisable de qué se pidió, qué controles se aplicaron, qué decisión se tomó y qué resultado produjo una acción. (Fasc. 2, cap. 8)

## B

**Backtracking.** Técnica de búsqueda que prueba una asignación parcial, avanza si sigue siendo consistente y vuelve atrás cuando aparece una contradicción. (Fasc. 2, cap. 7)

**Bucle agente.** Ciclo operativo donde un agente propone un paso, lo valida, lo ejecuta, observa el resultado y replanifica si el estado real cambia. (Fasc. 2, cap. 10)

## C

**Camino de propiedad.** Expresión SPARQL que permite recorrer relaciones encadenadas, por ejemplo `:dependeDe+` para seguir una o más dependencias. (Fasc. 2, cap. 12)

**Clase.** Categoría de entidades dentro de una ontología, como `Cliente`, `Factura`, `Servicio` o `DocumentoFiscal`. (Fasc. 2, cap. 12)

**Consulta SPARQL.** Pregunta formal sobre un grafo RDF que busca patrones, enlaza variables y devuelve resultados, booleanos o nuevas tripletas. (Fasc. 2, cap. 12)

**CSP** (*Constraint Satisfaction Problem*). Problema definido por variables, dominios y restricciones, donde la solución es una asignación que cumple todas las reglas duras. (Fasc. 2, cap. 6)

**Consistencia de arco.** Propiedad de una restricción binaria donde cada valor de una variable tiene al menos un valor compatible en la variable vecina. (Fasc. 2, cap. 7)

## D

**Determinista (sistema).** Sistema donde la misma entrada produce siempre la misma salida. Un compilador, una consulta SQL o una función pura son ejemplos. (Cap. 2)

**Distribución de probabilidad.** Asignación de una probabilidad a cada resultado posible. En un LLM, a cada token del vocabulario. (Cap. 2)

**Dominio.** Conjunto de valores permitidos para una variable en un problema de satisfacción de restricciones. (Fasc. 2, cap. 6)

**Dominio PDDL.** Parte reutilizable de un modelo PDDL que define tipos, predicados y acciones generales. (Fasc. 2, cap. 9)

## E

**Efecto.** Cambio que una acción produce en el estado después de ejecutarse. (Fasc. 2, cap. 9)

**Entidad.** Objeto identificable del dominio sobre el que queremos decir hechos: una persona, documento, producto, servicio, concepto o lugar. (Fasc. 2, cap. 12)

**Estado.** Conjunto de hechos que describen qué es verdadero en un momento de un problema de búsqueda o planificación. (Fasc. 2, cap. 9)

**Estrategia.** Regla que decide qué acción tomar según el estado del juego y la información disponible. (Fasc. 2, cap. 11)

**Estocástico (sistema).** Sistema donde la misma entrada puede producir salidas diferentes porque incorpora elementos de probabilidad o muestreo. (Cap. 2)

## F

**FILTER.** Cláusula de SPARQL que restringe soluciones por una condición, como importe mayor que un umbral o idioma concreto de una etiqueta. (Fasc. 2, cap. 12)

**Forward checking.** Técnica de CSP que, después de asignar una variable, elimina de los dominios restantes los valores incompatibles con esa elección. (Fasc. 2, cap. 7)

**Función de evaluación.** Heurística que asigna una puntuación a un estado no terminal cuando no podemos explorar el árbol completo. (Fasc. 2, cap. 11)

**Función de transición.** Regla que describe el estado resultante después de aplicar una acción válida a un estado de partida. (Fasc. 2, cap. 10)

## G

**Guardrail.** Control ejecutable que valida, limita, bloquea o escala una acción de IA antes de que produzca efectos reales. (Fasc. 2, cap. 8)

**Grafo de conocimiento.** Representación de entidades y relaciones explícitas que permite consultar, inferir y explicar conexiones entre hechos. (Fasc. 2, cap. 12)

## H

**HITL** (*human in the loop*). Aprobación humana incorporada al flujo cuando una acción automática supera un umbral de riesgo o incertidumbre. (Fasc. 2, cap. 8)

**Heurística de planificación.** Estimación del coste o esfuerzo restante hasta alcanzar el objetivo, usada para ordenar la búsqueda de planes. (Fasc. 2, cap. 10)

**Horizonte.** Número máximo de pasos que permitimos al buscar o codificar un plan. En planificación con SAT suele probarse con \(k=1\), \(k=2\), \(k=3\)... hasta encontrar una fórmula satisfacible. (Fasc. 2, cap. 10)

## I

**Inteligencia artificial.** Rama de la informática que construye sistemas capaces de realizar tareas que normalmente requieren inteligencia humana, mediante modelos matemáticos que aprenden patrones a partir de datos. (Cap. 1)

**Inferencia simbólica.** Proceso de derivar hechos nuevos a partir de hechos y reglas explícitas. (Fasc. 2, cap. 12)

**Invariante.** Condición que debe seguir siendo verdadera antes y después de ejecutar una acción. (Fasc. 2, cap. 8)

**Instancia.** Entidad concreta que pertenece a una clase de una ontología, como `factura:f9` dentro de `Factura`. (Fasc. 2, cap. 12)

## J

**Juego con otros actores.** Problema de decisión donde otras personas, sistemas o reglas también eligen acciones y pueden cambiar nuestra utilidad. (Fasc. 2, cap. 11)

**Jugador.** Actor que toma decisiones dentro de un juego y tiene objetivos o incentivos propios. (Fasc. 2, cap. 11)

## L

**LLM** (*Large Language Model*). Modelo de lenguaje de gran escala. Red neuronal con miles de millones de parámetros entrenada sobre cantidades masivas de texto para predecir y generar lenguaje. (Cap. 1)

**Linked Data.** Conjunto de prácticas para publicar datos con identificadores estables, formatos semánticos y enlaces entre recursos. (Fasc. 2, cap. 12)

**Logit.** Puntuación cruda que asigna el modelo a cada token antes de convertirse en probabilidad. (Cap. 2)

## M

**Muestreo.** Proceso de elegir un valor concreto a partir de una distribución de probabilidad. En un LLM, se muestrea cuál será el siguiente token. (Cap. 2)

**MCTS** (*Monte Carlo Tree Search*). Búsqueda en árbol que usa simulaciones para equilibrar explotación de ramas prometedoras y exploración de ramas poco visitadas. (Fasc. 2, cap. 11)

**Minimax.** Algoritmo para juegos de suma cero donde MAX elige la acción con mejor valor garantizado suponiendo que MIN responderá para reducirlo. (Fasc. 2, cap. 11)

**Monte Carlo.** Familia de métodos que estiman valores mediante simulaciones o muestras repetidas de un proceso. (Fasc. 2, cap. 11)

**MRV** (*Minimum Remaining Values*). Heurística de CSP que elige primero la variable con menos valores legales restantes. (Fasc. 2, cap. 7)

**Mutex.** Relación de incompatibilidad que impide que dos acciones o hechos sean válidos al mismo tiempo. (Fasc. 2, cap. 10)

## N

**Neurona artificial.** Función matemática que recibe entradas numéricas, las multiplica por pesos, suma un sesgo y aplica una función de activación para producir una salida. Es la unidad mínima de cómputo en una red neuronal. (Cap. 4)

## O

**Observación.** Evidencia obtenida después de actuar que confirma o corrige el estado que el sistema creía tener. (Fasc. 2, cap. 9)

**Ontología.** Modelo compartido de un dominio que define clases, relaciones y restricciones para que distintas personas y sistemas hablen el mismo idioma. (Fasc. 2, cap. 12)

**OPTIONAL.** Cláusula de SPARQL que añade datos si existen sin eliminar la solución principal cuando ese dato falta. (Fasc. 2, cap. 12)

**OWL** (*Web Ontology Language*). Lenguaje para expresar ontologías con axiomas, clases, propiedades y restricciones más ricas que RDFS. (Fasc. 2, cap. 12)

## P

**Parámetro.** Cada uno de los números que el modelo ajusta durante el entrenamiento. Un modelo de 175 000 millones de parámetros tiene 175 000 millones de números. Son la «memoria» del modelo. (Cap. 1)

**PDDL** (*Planning Domain Definition Language*). Lenguaje formal para describir dominios y problemas de planificación automática. (Fasc. 2, cap. 9)

**Peso.** Número que multiplica una entrada de una neurona artificial. Representa la importancia de esa entrada para la salida. Se ajusta durante el entrenamiento. (Cap. 4)

**Plan.** Secuencia de acciones que transforma un estado inicial en un estado que satisface el objetivo. (Fasc. 2, cap. 9)

**Plan relajado.** Aproximación optimista de un problema de planificación que ignora algunos efectos negativos para estimar cuánto falta hasta el objetivo. (Fasc. 2, cap. 10)

**Planificación automática.** Búsqueda de un plan válido a partir de un estado inicial, acciones disponibles y un objetivo. (Fasc. 2, cap. 9)

**Planificación con SAT.** Traducción de un problema de planificación a una fórmula booleana que pregunta si existe un plan válido para un horizonte \(k\). (Fasc. 2, cap. 10)

**Poda alfa-beta.** Optimización de minimax que descarta ramas incapaces de cambiar la decisión final. (Fasc. 2, cap. 11)

**Política de permisos.** Regla ejecutable que decide quién puede hacer qué acción bajo qué condiciones. (Fasc. 2, cap. 8)

**Precondición.** Hecho que debe ser verdadero antes de poder ejecutar una acción. (Fasc. 2, cap. 9)

**Predicado.** Hecho verificable que puede ser verdadero o falso en un estado. (Fasc. 2, cap. 9)

**Problema PDDL.** Instancia concreta de un dominio PDDL con objetos, estado inicial y objetivo. (Fasc. 2, cap. 9)

**Propiedad.** Relación o atributo en una ontología; puede conectar dos entidades o asignar un valor literal a una entidad. (Fasc. 2, cap. 12)

**Propagación.** Reducción de dominios usando restricciones antes o durante la búsqueda en un CSP. (Fasc. 2, cap. 7)

**Pregunta de competencia.** Pregunta concreta que una ontología debería poder responder y que sirve para decidir su alcance. (Fasc. 2, cap. 12)

## R

**ReLU.** Función de activación que devuelve max(0, x). La más usada en capas ocultas por su simplicidad y eficiencia. (Cap. 4)

**RDF** (*Resource Description Framework*). Modelo estándar para representar hechos como tripletas sujeto-predicado-objeto. (Fasc. 2, cap. 12)

**RDFS** (*RDF Schema*). Vocabulario para definir clases, subclases, propiedades, dominio y rango sobre datos RDF. (Fasc. 2, cap. 12)

**Regla simbólica.** Condición explícita que permite aceptar, rechazar o derivar hechos dentro de un sistema de conocimiento. (Fasc. 2, cap. 12)

**Restricción.** Regla que acepta o rechaza valores o combinaciones de valores en un CSP. Si es dura, una solución no puede violarla. (Fasc. 2, cap. 6)

**Replanificación.** Construcción de un nuevo plan cuando una acción falla, el estado cambia o la observación contradice lo esperado. (Fasc. 2, cap. 9)

**Retorno.** Suma de recompensas futuras, normalmente descontadas, que mide el valor acumulado de una trayectoria. (Fasc. 2, cap. 11)

**RLHF** (*Reinforcement Learning from Human Feedback*). Técnica de post-entrenamiento donde personas evalúan respuestas del modelo y esa señal se usa para alinear su comportamiento con preferencias humanas. (Cap. 1)

## S

**Schema.** Contrato estructural que define qué campos, tipos y valores acepta una entrada o salida. (Fasc. 2, cap. 8)

**Sesgo (bias).** Valor que se suma a la suma ponderada de una neurona para desplazar su salida. Permite que la neurona se active incluso con entradas nulas. (Cap. 4)

**Sigmoide.** Función de activación que comprime cualquier valor real a un número entre 0 y 1. Se usa en clasificación binaria. (Cap. 4)

**Softmax.** Función que convierte un vector de puntuaciones en una distribución de probabilidad que suma 1. Se usa en la capa final de clasificación multiclase. (Cap. 4)

**SPARQL.** Lenguaje de consulta para grafos RDF que busca patrones de tripletas y devuelve entidades o valores que encajan con esos patrones. (Fasc. 2, cap. 12)

**Sistema experto.** Sistema basado en ontología, hechos, reglas y un motor de inferencia que razona sobre un dominio y puede explicar sus decisiones. (Fasc. 2, cap. 12)

## T

**Temperatura.** Parámetro que controla cuánta aleatoriedad se introduce al muestrear el siguiente token. Valores bajos producen respuestas más predecibles; valores altos, más creativas. (Cap. 2)

**Token.** Unidad mínima de texto que el modelo procesa. Puede ser una palabra, parte de una palabra o un carácter. El modelo razona en tokens, no en palabras. (Cap. 1)

**Transformer.** Arquitectura de red neuronal presentada en 2017 que sustituye el procesamiento secuencial por un mecanismo de atención paralela. Es la base de todos los LLMs modernos. (Cap. 1)

**Tripleta RDF.** Hecho elemental con forma \((sujeto, predicado, objeto)\), por ejemplo `factura:f9 perteneceA cliente:c42`. (Fasc. 2, cap. 12)

## U

**UCT** (*Upper Confidence bounds applied to Trees*). Regla usada en MCTS que combina valor medio observado y un bonus para explorar acciones poco visitadas. (Fasc. 2, cap. 11)

**URI** (*Uniform Resource Identifier*). Identificador estable usado para nombrar recursos de forma no ambigua en la web semántica. (Fasc. 2, cap. 12)

**Utilidad.** Valor numérico que asignamos a un resultado desde el punto de vista de un jugador. (Fasc. 2, cap. 11)

## V

**Variable CSP.** Decisión pendiente que debe recibir un valor de su dominio para construir una asignación candidata. (Fasc. 2, cap. 6)

**Vector store.** Almacén de embeddings que recupera fragmentos por similitud semántica, útil para encontrar texto parecido pero no para razonar por reglas explícitas. (Fasc. 2, cap. 12)
