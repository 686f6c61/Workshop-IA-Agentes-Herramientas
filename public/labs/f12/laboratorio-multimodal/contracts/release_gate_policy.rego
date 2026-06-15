package multimodal.release

default allow_release := false

allow_release if {
  input.global_decision == "ship"
  every case in input.cases {
    case.decision == "pass"
    count(case.missing_evidence) == 0
    count(case.missing_controls) == 0
    case.quality_score >= input.thresholds.pass_min_quality
    case.risk_score < input.thresholds.review_min_risk
    case.latency_ms <= input.thresholds.max_latency_ms
    case.cost_units <= input.thresholds.max_cost_units
    case.failure_rate <= input.thresholds.max_failure_rate
  }
}

deny[reason] if {
  case := input.cases[_]
  case.decision != "pass"
  reason := sprintf("%s no está en pass", [case.case_id])
}

deny[reason] if {
  case := input.cases[_]
  count(case.missing_evidence) > 0
  reason := sprintf("%s tiene evidencias faltantes", [case.case_id])
}

deny[reason] if {
  case := input.cases[_]
  count(case.missing_controls) > 0
  reason := sprintf("%s tiene controles faltantes", [case.case_id])
}
