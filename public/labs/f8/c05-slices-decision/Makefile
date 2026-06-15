PYTHON ?= python3

.PHONY: run test clean

run:
	$(PYTHON) ops/audit_decision_slices.py --write
	$(PYTHON) ops/compare_mitigation.py --write
	$(PYTHON) ops/audit_with_fairlearn.py --field access_need --write

test: run
	$(PYTHON) -m unittest discover -s tests -p "test_*.py"

clean:
	rm -rf output output_bad output_risky
