-- Schema minimo para experimentos de IA.
-- La idea es separar asignacion, exposicion, metricas y decision.

create table experiment_units (
  experiment_id text not null,
  unit_id text not null,
  assignment_unit text not null,
  variant text not null,
  assigned_at timestamp not null,
  flag_key text not null,
  flag_version text not null,
  context_hash text not null,
  primary key (experiment_id, unit_id)
);

create table exposure_events (
  experiment_id text not null,
  unit_id text not null,
  exposure_id text not null,
  flag_key text not null,
  variant text not null,
  exposed_at timestamp not null,
  prompt_version text,
  model_version text,
  retrieval_version text,
  fallback_used boolean not null default false,
  trace_id text,
  primary key (experiment_id, exposure_id)
);

create table metric_events (
  experiment_id text not null,
  unit_id text not null,
  metric_name text not null,
  metric_value numeric not null,
  metric_window text not null,
  observed_at timestamp not null,
  source_table text not null,
  trace_id text
);

create table experiment_decisions (
  experiment_id text not null,
  decided_at timestamp not null,
  status text not null,
  primary_metric text not null,
  effect numeric,
  ci95_low numeric,
  ci95_high numeric,
  decision_doc text not null,
  owner text not null,
  primary key (experiment_id, decided_at)
);

-- Consultas que deberian vivir en CI:
-- 1. Toda unidad analizada debe tener una exposicion.
-- 2. Ninguna unidad debe tener dos variantes en el mismo experimento.
-- 3. Toda decision debe apuntar a un contrato y a una ventana de metricas.
