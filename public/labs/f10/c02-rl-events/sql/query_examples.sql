-- 1. Cobertura por estado y accion.
SELECT
  state_id,
  action,
  COUNT(*) AS events,
  COUNT(*) * 1.0 / SUM(COUNT(*)) OVER () AS share
FROM rl_events
GROUP BY state_id, action
ORDER BY events DESC, state_id, action;

-- 2. Eventos sin propensión útil.
SELECT
  event_id,
  episode_id,
  state_id,
  action,
  action_probability
FROM rl_events
WHERE action_probability IS NULL
   OR action_probability <= 0
   OR action_probability < 0.05;

-- 3. Recompensas tardías fuera de ventana de 72 horas.
SELECT
  event_id,
  episode_id,
  action,
  event_time,
  reward_time,
  EXTRACT(EPOCH FROM (reward_time - event_time)) / 3600 AS reward_delay_hours
FROM rl_events
WHERE reward_time IS NOT NULL
  AND EXTRACT(EPOCH FROM (reward_time - event_time)) / 3600 > 72;

-- 4. Episodios sin cierre terminal.
SELECT
  episode_id,
  COUNT(*) AS steps,
  SUM(CASE WHEN terminal THEN 1 ELSE 0 END) AS terminal_events
FROM rl_events
GROUP BY episode_id
HAVING SUM(CASE WHEN terminal THEN 1 ELSE 0 END) = 0;

-- 5. Retorno por version de politica.
SELECT
  e.policy_version,
  COUNT(DISTINCT e.episode_id) AS episodes,
  AVG(ep.discounted_return) AS avg_discounted_return
FROM rl_events e
JOIN rl_episodes ep ON ep.episode_id = e.episode_id
GROUP BY e.policy_version
ORDER BY avg_discounted_return DESC;

-- 6. Acciones tomadas que no deberían existir en el catálogo actual.
-- En un warehouse real, available_actions_json se parsearía con funciones JSON.
-- Esta consulta deja el contrato: compara contra una tabla de catálogo.
SELECT
  e.event_id,
  e.state_id,
  e.action
FROM rl_events e
LEFT JOIN allowed_actions_catalog a
  ON a.action = e.action
WHERE a.action IS NULL;

-- 7. Snapshots que no deberían alimentar entrenamiento.
SELECT
  snapshot_id,
  snapshot_hash,
  decision_status,
  event_count,
  episode_count,
  created_at
FROM rl_trajectory_snapshots
WHERE decision_status <> 'pass'
ORDER BY created_at DESC;
