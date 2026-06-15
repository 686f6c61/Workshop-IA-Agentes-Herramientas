PYTHON ?= python3

.PHONY: run test clean

run:
	$(PYTHON) ops/simulate_bandit_policy.py --write
	$(PYTHON) ops/audit_reward_spec.py --write
	cp evidence/ope_decision.md output/ope_decision.md
	cp evidence/ope_quality_card.md output/ope_quality_card.md
	cp evidence/slice_diagnostics.csv output/slice_diagnostics.csv
	cp evidence/support_matrix.csv output/support_matrix.csv
	cp evidence/serving_decision.md output/serving_decision.md
	cp evidence/serving_runbook.md output/serving_runbook.md
	$(PYTHON) ops/simulate_bandit_policy.py --output-dir solutions/reference --write
	$(PYTHON) ops/audit_reward_spec.py --output-dir solutions/reference --write
	cp evidence/ope_decision.md solutions/reference/ope_decision.md
	cp evidence/ope_quality_card.md solutions/reference/ope_quality_card.md
	cp evidence/slice_diagnostics.csv solutions/reference/slice_diagnostics.csv
	cp evidence/support_matrix.csv solutions/reference/support_matrix.csv
	cp evidence/serving_decision.md solutions/reference/serving_decision.md
	cp evidence/serving_runbook.md solutions/reference/serving_runbook.md
	$(PYTHON) ops/check_student_submission.py --submission-dir solutions/reference --write --fail-on-missing

test: run
	$(PYTHON) -m unittest discover -s tests -p "test_*.py"

clean:
	rm -rf output output_bad output_risky
