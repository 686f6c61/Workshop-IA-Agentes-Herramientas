PYTHON ?= python3

.PHONY: run test clean

run:
	$(PYTHON) ops/data/audit_dataset_contract.py --write
	$(PYTHON) ops/data/compare_drift.py --write

test: run
	$(PYTHON) -m unittest discover -s tests -p "test_*.py"

clean:
	rm -rf output output_bad output_risky
