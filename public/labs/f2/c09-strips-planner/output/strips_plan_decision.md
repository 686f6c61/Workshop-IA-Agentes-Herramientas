# Plan STRIPS mínimo

Plan encontrado: `['validar_factura', 'enviar_factura', 'registrar_envio']`.
Estado final: `['cliente_identificado', 'email_confirmado', 'email_enviado', 'factura_validada', 'importe_calculado', 'log_creado']`.
Expansiones BFS: `4`.

## Planes candidatos

| Plan | Válido | Motivo |
|---|---:|---|
| `['validar_factura', 'enviar_factura', 'registrar_envio']` | sí | `ok` |
| `['enviar_factura', 'validar_factura', 'registrar_envio']` | no | `precondiciones_no_satisfechas:enviar_factura:factura_validada` |
| `['validar_factura', 'registrar_envio', 'enviar_factura']` | no | `precondiciones_no_satisfechas:registrar_envio:email_enviado` |

## Decisión

Un plan no se valida por sonar razonable. Se valida porque cada acción es aplicable en el estado donde aparece y porque el estado final contiene el objetivo.
