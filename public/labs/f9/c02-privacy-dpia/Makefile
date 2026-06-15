PYTHON ?= python3

.PHONY: run test clean

run:
	$(PYTHON) ops/build_privacy_pack.py --write
	$(PYTHON) ops/privacy_ci_gate.py --write

test: run
	$(PYTHON) -m unittest discover -s tests -p "test_*.py"

clean:
	rm -rf output output_bad output_risky
