# Inspección de tokens y embeddings

Este informe usa un tokenizador y un embedding de juguete. La lectura importante es el mecanismo, no los números exactos.

## spanish_vs_english_cost

- Objetivo: comparar consumo aproximado de tokens entre idiomas.
- Este caso exige similitud alta: no.
- Similitud coseno: `0.7715`.
- Aviso de presupuesto de tokens: no.
- `machine learning is useful` -> 4 tokens: `['machine', 'learning', 'is', 'useful']`.
- `el aprendizaje automático resulta útil` -> 5 tokens: `['el', 'aprendizaje', 'automático', 'resulta', 'útil']`.

## semantic_pair

- Objetivo: deberían quedar cerca aunque compartan pocas palabras.
- Este caso exige similitud alta: sí.
- Similitud coseno: `0.8165`.
- Aviso de presupuesto de tokens: no.
- `gato doméstico` -> 2 tokens: `['gato', 'doméstico']`.
- `felino de casa` -> 3 tokens: `['felino', 'de', 'casa']`.

## code_pair

- Objetivo: misma intención de código en sintaxis distinta.
- Este caso exige similitud alta: sí.
- Similitud coseno: `0.9129`.
- Aviso de presupuesto de tokens: sí.
- `function getUser(id) { return db.user(id) }` -> 14 tokens: `['function', 'getuser', '(', 'id', ')', '{', 'return', 'db', '.', 'user', '(', 'id', ')', '}']`.
- `def get_user(id): return db.user(id)` -> 13 tokens: `['def', 'get_user', '(', 'id', ')', ':', 'return', 'db', '.', 'user', '(', 'id', ')']`.

## long_word

- Objetivo: ver subtokens y parentesco morfológico.
- Este caso exige similitud alta: sí.
- Similitud coseno: `0.8528`.
- Aviso de presupuesto de tokens: no.
- `desarrolladores responsables` -> 5 tokens: `['desa', 'rroll', 'adore', 's', 'responsables']`.
- `desarrollo responsable` -> 2 tokens: `['desarrollo', 'responsable']`.

En producción repetirías este ejercicio con el tokenizador y el modelo de embedding reales. Este kit te prepara para entender qué estás midiendo.