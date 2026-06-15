-- Esquema mínimo para auditar evaluación off-policy en un warehouse.
-- Ajusta tipos y sintaxis a BigQuery, Snowflake, Postgres o Databricks según tu entorno.

CREATE TABLE rl_ope_events (
  event_id TEXT PRIMARY KEY,
  occurred_at TIMESTAMP,
  slice TEXT NOT NULL,
  complexity DOUBLE PRECISION,
  behavior_policy_id TEXT NOT NULL,
  target_policy_id TEXT NOT NULL,
  action TEXT NOT NULL,
  allowed_actions_json TEXT NOT NULL,
  behavior_action_probability DOUBLE PRECISION NOT NULL,
  target_action_probability DOUBLE PRECISION NOT NULL,
  reward DOUBLE PRECISION NOT NULL,
  reward_version TEXT NOT NULL,
  q_model_version TEXT NOT NULL,
  q_model_reward_by_action_json TEXT NOT NULL,
  target_policy_probability_by_action_json TEXT NOT NULL,
  dataset_snapshot_id TEXT NOT NULL,
  created_at TIMESTAMP NOT NULL
);

CREATE TABLE rl_ope_importance_weights (
  event_id TEXT NOT NULL,
  slice TEXT NOT NULL,
  action TEXT NOT NULL,
  behavior_probability DOUBLE PRECISION NOT NULL,
  target_probability DOUBLE PRECISION NOT NULL,
  importance_weight DOUBLE PRECISION NOT NULL,
  reward DOUBLE PRECISION NOT NULL,
  run_id TEXT NOT NULL,
  created_at TIMESTAMP NOT NULL
);

CREATE TABLE rl_ope_runs (
  run_id TEXT PRIMARY KEY,
  dataset_snapshot_id TEXT NOT NULL,
  behavior_policy_id TEXT NOT NULL,
  target_policy_id TEXT NOT NULL,
  contract_version TEXT NOT NULL,
  status TEXT NOT NULL,
  direct_method DOUBLE PRECISION,
  ips DOUBLE PRECISION,
  wis DOUBLE PRECISION,
  doubly_robust DOUBLE PRECISION,
  bootstrap_ci_lower DOUBLE PRECISION,
  bootstrap_ci_upper DOUBLE PRECISION,
  ess_ratio DOUBLE PRECISION,
  max_importance_weight DOUBLE PRECISION,
  created_at TIMESTAMP NOT NULL
);
