# Runbook DataOps para una ventana con drift

Este runbook acompana `monitoring_contract.json`. Se usa cuando `ops/monitor_dataops.py` genera `review` o `block`.

## 1. Confirmar la ventana

```text
Ventana:
Pipeline versión:
Model versión:
Data versión:
Owner:
```

No mezcles ventanas. Un problema de hoy puede no existir ayer.

## 2. Leer primero los bloqueos

1. Abre `output/alerts.md`.
2. Busca alertas `block`.
3. Identifica si vienen de datos, drift, latencia, trazabilidad o slices.
4. Localiza los `trace_id` ausentes o incompletos.

## 3. Diagnosticar causa probable

| Señal | Pregunta | Accion inicial |
|---|---|---|
| Drift alto en `language` | Ha cambiado el trafico o falta cobertura? | Comparar campana, canal, fuente y versión de datos. |
| `miss_rate` alto | Casos importantes pasan a flujo normal? | Revisar umbral, banda de revisión y etiquetas retrasadas. |
| Latencia p95 alta | Hay cola, dependencia externa o batch pesado? | Mirar trazas, logs y tiempos por paso. |
| `trace_id` faltante | Se rompio instrumentación? | Corregir logger/propagación antes de investigar a ciegas. |
| `review_rate` alto | La mitigación supera capacidad humana? | Medir cola diaria y ajustar SLO o política. |

## 4. Decidir

```text
Decisión: pass | review | block
Causa principal:
Accion:
Owner:
Fecha de revisión:
Artefactos revisados:
```

## 5. Criterio de salida

La ventana vuelve a `pass` solo si:

1. Hay trazabilidad completa.
2. El SLO que fallo vuelve a rango o tiene excepción documentada.
3. La causa queda escrita.
4. El mismo check queda automatizado para la siguiente ventana.
