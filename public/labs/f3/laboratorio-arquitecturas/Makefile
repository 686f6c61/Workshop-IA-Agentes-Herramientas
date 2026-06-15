PYTHON ?= python3

.PHONY: run test clean

run:
	$(PYTHON) ops/score_architecture_strategy.py --write
	$(PYTHON) ops/estimate_inference_budget.py --write
	$(PYTHON) ops/score_architecture_strategy.py --output-dir solutions/reference --write
	$(PYTHON) ops/estimate_inference_budget.py --output-dir solutions/reference --write
	$(PYTHON) ops/check_student_submission.py --submission-dir solutions/reference --write --fail-on-missing

test: run
	$(PYTHON) -m unittest discover -s tests -p "test_*.py"

clean:
	rm -rf output output_bad output_risky
