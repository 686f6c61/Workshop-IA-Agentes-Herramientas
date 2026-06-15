package multimodal.egress

default allow := false
default review := false

approved_destinations := {
  "approved_ai_provider",
  "internal_support_tool",
  "internal_eval_store",
  "security_ticket",
}

blocked_destinations := {
  "public_webhook",
  "personal_email",
  "unknown_domain",
}

allow if {
  approved_destinations[input.destination]
  input.risk_score < 0.45
  input.missing_controls == 0
  not input.has_unredacted_secret
  not input.external_action
}

review if {
  approved_destinations[input.destination]
  input.risk_score >= 0.45
  not input.has_unredacted_secret
  not input.external_action
}

review if {
  approved_destinations[input.destination]
  input.missing_controls > 0
  not input.has_unredacted_secret
  not input.external_action
}

deny_reason contains "blocked_destination" if {
  blocked_destinations[input.destination]
}

deny_reason contains "unredacted_secret" if {
  input.has_unredacted_secret
}

deny_reason contains "external_action_requires_approval" if {
  input.external_action
}
