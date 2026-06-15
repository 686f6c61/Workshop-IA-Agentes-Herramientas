# Decisión de mini buscador semántico

Decisión: `publicar_piloto`.

## Métricas

- Hit@1: `1.0`.
- MRR: `1.0`.
- Cobertura de trazas: `1.0`.

## Resultados por consulta

| Caso | Consulta | Esperado | Primer resultado |
|---|---|---|---|
| `q_access` | No puedo entrar en mi perfil | `doc_access_password` | `doc_access_password` · 0.9962 |
| `q_invoice` | Necesito el recibo del mes | `doc_invoice_monthly` | `doc_invoice_monthly` · 0.9996 |

## Lectura

El buscador funciona en esta maqueta porque los vectores separan acceso y facturas. En un sistema real habría que ampliar casos, medir errores por categoría y versionar el vocabulario o el modelo de embeddings.
