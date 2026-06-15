PYTHON ?= python3

.PHONY: run test clean

run:
	$(PYTHON) ops/compare_frontiers.py --write

test: run
	$(PYTHON) -m unittest discover -s tests -p "test_*.py"

clean:
	rm -rf output output_bad output_risky
