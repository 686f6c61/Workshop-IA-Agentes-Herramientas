PYTHON ?= python3

.PHONY: run test clean

run:
	$(PYTHON) ops/audit_preference_dataset.py --write
	$(PYTHON) ops/audit_preference_dataset.py --pairs data/preference_pairs_bad.jsonl --output output_bad --write

test: run
	$(PYTHON) -m unittest discover -s tests -p "test_*.py"

clean:
	rm -rf output output_bad output_risky
