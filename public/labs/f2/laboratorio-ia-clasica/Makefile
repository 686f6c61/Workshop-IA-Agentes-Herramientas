PYTHON ?= python3

.PHONY: run test clean

run:
	$(PYTHON) ops/solve_csp_schedule.py --write
	$(PYTHON) ops/evaluate_symbolic_plan.py --write
	$(PYTHON) ops/solve_csp_schedule.py --output-dir solutions/reference --write
	$(PYTHON) ops/evaluate_symbolic_plan.py --output-dir solutions/reference --write

test: run
	$(PYTHON) -m unittest discover -s tests -p "test_*.py"

clean:
	rm -rf output output_bad output_risky
