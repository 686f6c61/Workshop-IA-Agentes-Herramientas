// Borrador de autorización para portar a Cedar/Amazon Verified Permissions.
// La app debe modelar principal, action, resource y context con su esquema real.

permit (
  principal == MultimodalSystem::"risk-gate",
  action == Action::"SendArtifact",
  resource is Artifact
)
when {
  ["approved_ai_provider", "internal_support_tool", "internal_eval_store", "security_ticket"]
    .contains(context.destination)
  && context.risk_score < 0.45
  && context.missing_controls == 0
  && context.has_unredacted_secret == false
  && context.external_action == false
};

permit (
  principal == MultimodalSystem::"risk-gate",
  action == Action::"StoreEvalFixture",
  resource is Artifact
)
when {
  context.destination == "internal_eval_store"
  && context.has_unredacted_secret == false
  && context.external_action == false
};

forbid (
  principal,
  action,
  resource is Artifact
)
when {
  ["public_webhook", "personal_email", "unknown_domain"].contains(context.destination)
};

forbid (
  principal,
  action,
  resource is Artifact
)
when {
  context.has_unredacted_secret == true || context.external_action == true
};
