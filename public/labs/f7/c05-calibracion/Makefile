PYTHON ?= python3

.PHONY: run test clean

run:
	$(PYTHON) ops/ai/calibrate_policy.py --write
	$(PYTHON) ops/ai/calibrate_policy.py --cases evals/calibration_cases.csv --policy policies/calibration_policy.json --write

test: run
	$(PYTHON) -m unittest discover -s tests -p "test_*.py"

clean:
	rm -rf output output_bad output_risky
