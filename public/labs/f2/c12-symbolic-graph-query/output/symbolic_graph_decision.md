# Micrografo simbólico

Tripletas base: `7`.
Tripletas inferidas: `2`.

## Consultas

| Consulta | Resultado |
|---|---|
| `tipos_factura` | `['Documento', 'DocumentoFiscal', 'Factura']` |
| `facturas_cliente` | `['factura:f9']` |
| `dependencias_db` | `['servicio:api']` |
| `plan_cliente` | `['plan:empresa']` |

## Inferencias

- `['factura:f9', 'rdf:type', 'Documento']`
- `['factura:f9', 'rdf:type', 'DocumentoFiscal']`

## Decisión

El grafo sirve cuando necesitas relaciones verificables. Un vector store puede recuperar texto parecido; el grafo puede decir qué relación sostiene una decisión.
