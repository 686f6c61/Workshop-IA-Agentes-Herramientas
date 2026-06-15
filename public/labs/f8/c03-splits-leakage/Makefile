PYTHON ?= python3

.PHONY: run test clean

run:
	$(PYTHON) ops/split_audit.py --write
	$(PYTHON) ops/preprocessing_fit_audit.py --write
	$(PYTHON) ops/evaluate_test_slices.py --write

test: run
	$(PYTHON) -m unittest discover -s tests -p "test_*.py"

clean:
	rm -rf output output_bad output_risky
