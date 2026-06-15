# Runbook de piloto: política bandit para routing de modelos

Este runbook describe cómo pasar de simulación a un piloto controlado. No sustituye la aprobación técnica del equipo: fuerza a que la decisión tenga flag, métricas, rollback y criterios de parada antes de mover tráfico real.

## Alcance

| Campo | Valor |
|---|---|
| Sistema | Routing de modelos para soporte |
| Política candidata | Se toma de `output/bandit_validation_report.json` |
| Variante estable | `stable` |
| Variante candidata | `bandit_candidate` |
| Feature flag | `rl_model_routing_policy` |
| Tráfico inicial | 5 % de slices permitidos |
| Slices sin exploración | Los definidos en `contracts/bandit_policy_contract.json` |

## Requisitos antes de activar

1. `output/bandit_validation_report.json` debe quedar en `status=pass`.
2. `output/shadow_replay_report.json` debe tener todos los `readiness_checks` en `true`.
3. La política estable debe estar disponible como fallback.
4. Cada ronda debe registrar `context`, `allowed_actions`, `action`, `action_probability`, `selection_reason`, `reward` y `policy_version`.
5. El dashboard debe separar métrica por política, acción, slice y ventana temporal.
6. Debe existir una persona responsable de revisar el piloto en cada ventana.

## Escalado propuesto

| Paso | Exposición | Duración mínima | Decisión |
|---|---:|---:|---|
| 1 | 5 % | 24 h | Revisar manualmente regret, coste, calidad y trazas. |
| 2 | 10 % | 48 h | Subir solo si no hay deriva ni faltan eventos. |
| 3 | 25 % | 72 h | Subir solo si el efecto sigue estable por slice. |
| 4 | 50 % | 7 días | Mantener reserva estable y revisión diaria. |

## Condiciones de parada

Para el piloto y vuelve a `stable` si ocurre cualquiera de estas condiciones:

| Condición | Cómo se detecta |
|---|---|
| Regret por encima del contrato | `regret_window > max_regret` |
| Coste medio por encima del contrato | `average_cost > max_average_cost` |
| Calidad por debajo del contrato | `quality_window < min_quality` |
| Falta reward o propensión | Eventos sin `reward.final_reward` o sin `action_probability` |
| Exploración fuera de slice permitido | `slice in no_exploration_slices` y `exploratory=true` |
| Cambio no versionado | Acción, prompt o modelo cambia sin nueva versión |

## Lectura del piloto

Una política no gana por tener nombre sofisticado. Gana si, por ventana, mejora recompensa sin romper coste, trazabilidad ni límites de exploración. Si `greedy` gana en este kit, la lectura correcta es: el contrato y el escenario penalizan explorar de más cuando el mejor brazo se identifica pronto. En otro dominio, con más incertidumbre o recompensas cambiantes, UCB o Thompson sampling podrían ser mejores.

## Entregable esperado

1. `bandit_validation_report.json` con política candidata.
2. `shadow_replay_report.json` con checks de preparación.
3. Captura o consulta del dashboard con reward, regret, coste y acción por slice.
4. Decisión escrita: activar, mantener en shadow o volver a simulación.
5. Cambio concreto de contrato si la decisión no pasa.
