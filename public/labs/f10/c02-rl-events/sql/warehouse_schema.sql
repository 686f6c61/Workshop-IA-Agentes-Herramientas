-- Esquema mínimo para auditar datos de interacción RL.
-- Sintaxis compatible con Postgres/DuckDB con ajustes menores.

CREATE TABLE rl_events (
  event_id TEXT PRIMARY KEY,
  schema_version TEXT NOT NULL,
  episode_id TEXT NOT NULL,
  t INTEGER NOT NULL,
  event_time TIMESTAMP NOT NULL,
  ingestion_time TIMESTAMP NOT NULL,
  reward_time TIMESTAMP,
  state_id TEXT NOT NULL,
  state_features_json TEXT NOT NULL,
  available_actions_json TEXT NOT NULL,
  action TEXT NOT NULL,
  action_probability DOUBLE PRECISION NOT NULL,
  policy_id TEXT NOT NULL,
  policy_version TEXT NOT NULL,
  reward DOUBLE PRECISION NOT NULL,
  reward_version TEXT NOT NULL,
  reward_terms_json TEXT NOT NULL,
  next_state_id TEXT NOT NULL,
  terminal BOOLEAN NOT NULL,
  trace_id TEXT NOT NULL,
  environment_version TEXT NOT NULL,
  contains_personal_data BOOLEAN NOT NULL DEFAULT FALSE,
  redaction_policy TEXT NOT NULL,
  inserted_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE rl_episodes (
  episode_id TEXT PRIMARY KEY,
  first_event_time TIMESTAMP NOT NULL,
  last_event_time TIMESTAMP NOT NULL,
  steps INTEGER NOT NULL,
  terminal BOOLEAN NOT NULL,
  discounted_return DOUBLE PRECISION NOT NULL,
  policy_versions_json TEXT NOT NULL,
  reward_versions_json TEXT NOT NULL,
  snapshot_id TEXT
);

CREATE TABLE rl_policy_versions (
  policy_version TEXT PRIMARY KEY,
  policy_id TEXT NOT NULL,
  created_at TIMESTAMP NOT NULL,
  policy_type TEXT NOT NULL,
  exploration_strategy TEXT,
  owner TEXT NOT NULL,
  config_hash TEXT NOT NULL
);

CREATE TABLE rl_reward_versions (
  reward_version TEXT PRIMARY KEY,
  created_at TIMESTAMP NOT NULL,
  attribution_window_hours INTEGER NOT NULL,
  terms_json TEXT NOT NULL,
  owner TEXT NOT NULL,
  config_hash TEXT NOT NULL
);

CREATE TABLE rl_trajectory_snapshots (
  snapshot_id TEXT PRIMARY KEY,
  snapshot_hash TEXT NOT NULL,
  contract_version TEXT NOT NULL,
  schema_version TEXT NOT NULL,
  gamma DOUBLE PRECISION NOT NULL,
  event_count INTEGER NOT NULL,
  episode_count INTEGER NOT NULL,
  min_event_time TIMESTAMP NOT NULL,
  max_event_time TIMESTAMP NOT NULL,
  decision_status TEXT NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE rl_data_quality_runs (
  run_id TEXT PRIMARY KEY,
  snapshot_id TEXT,
  contract_version TEXT NOT NULL,
  status TEXT NOT NULL,
  shape_ok BOOLEAN NOT NULL,
  episodes_ok BOOLEAN NOT NULL,
  coverage_ok BOOLEAN NOT NULL,
  warnings_ok BOOLEAN NOT NULL,
  report_json TEXT NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
