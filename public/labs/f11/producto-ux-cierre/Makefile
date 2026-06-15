PYTHON ?= python3

.PHONY: run test clean

run:
	$(PYTHON) ops/score_product_readiness.py --write
	$(PYTHON) ops/review_ux_flows.py --write
	cp templates/ai_product_decision.md output/nota_de_decision.md
	cp templates/ux_contract.md output/ux_contract.md
	$(PYTHON) ops/check_student_submission.py --submission-dir solutions/reference --write --fail-on-missing

test: run
	$(PYTHON) -m unittest discover -s tests -p "test_*.py"

clean:
	rm -rf output output_bad output_risky
