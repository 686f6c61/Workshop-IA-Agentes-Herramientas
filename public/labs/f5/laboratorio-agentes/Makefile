PYTHON ?= python3

.PHONY: run test clean

run:
	$(PYTHON) ops/run_agent_runtime.py --write
	$(PYTHON) ops/evaluate_agent_routes.py --write
	$(PYTHON) ops/evaluate_agent_routes.py --runs data/agent_runs_regression.json --output-dir output/regression --write
	$(PYTHON) ops/check_student_submission.py --submission-dir solutions/reference --write

test: run
	$(PYTHON) -m unittest discover -s tests -p "test_*.py"

clean:
	rm -rf output output_bad output_risky
