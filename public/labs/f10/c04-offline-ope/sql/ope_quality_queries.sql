-- Consultas de calidad para decidir si una evaluación off-policy es defendible.

-- 1. Pesos extremos que pueden dominar IPS.
SELECT
  event_id,
  slice,
  action,
  behavior_probability,
  target_probability,
  importance_weight,
  reward
FROM rl_ope_importance_weights
WHERE run_id = 'run_2026_06_08_c04'
ORDER BY importance_weight DESC
LIMIT 20;

-- 2. Soporte por slice y accion.
SELECT
  slice,
  action,
  COUNT(*) AS observed_events,
  AVG(target_action_probability) AS avg_target_probability_on_logged_action
FROM rl_ope_events
WHERE dataset_snapshot_id = 'snapshot_c04_001'
GROUP BY slice, action
ORDER BY slice, action;

-- 3. Tamano efectivo de muestra aproximado por run.
SELECT
  run_id,
  POWER(SUM(importance_weight), 2) / NULLIF(SUM(importance_weight * importance_weight), 0) AS ess,
  COUNT(*) AS events,
  POWER(SUM(importance_weight), 2) / NULLIF(SUM(importance_weight * importance_weight), 0) / COUNT(*) AS ess_ratio
FROM rl_ope_importance_weights
WHERE run_id = 'run_2026_06_08_c04'
GROUP BY run_id;

-- 4. Runs que no deberían avanzar.
SELECT
  run_id,
  status,
  doubly_robust,
  bootstrap_ci_lower,
  ess_ratio,
  max_importance_weight
FROM rl_ope_runs
WHERE
  status <> 'pass'
  OR bootstrap_ci_lower < 0.68
  OR ess_ratio < 0.45
  OR max_importance_weight > 4.0
ORDER BY created_at DESC;
