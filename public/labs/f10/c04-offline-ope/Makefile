PYTHON ?= python3

.PHONY: run test clean

run:
	$(PYTHON) ops/evaluate_offline_policy.py --write
	$(PYTHON) ops/evaluate_offline_policy.py --events data/logged_policy_events_bad.jsonl --output output_bad --write

test: run
	$(PYTHON) -m unittest discover -s tests -p "test_*.py"

clean:
	rm -rf output output_bad output_risky
