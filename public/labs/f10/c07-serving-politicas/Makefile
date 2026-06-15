PYTHON ?= python3

.PHONY: run test clean

run:
	$(PYTHON) ops/audit_policy_serving.py --write
	$(PYTHON) ops/audit_policy_serving.py --current data/current_window_bad.json --plan data/release_plan_bad.json --output output_bad --write

test: run
	$(PYTHON) -m unittest discover -s tests -p "test_*.py"

clean:
	rm -rf output output_bad output_risky
