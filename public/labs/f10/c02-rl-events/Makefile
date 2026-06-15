PYTHON ?= python3

.PHONY: run test clean

run:
	$(PYTHON) ops/validate_rl_events.py --write
	$(PYTHON) ops/validate_rl_events.py --events data/events_bad.jsonl --output output_bad --write
	$(PYTHON) ops/validate_rl_events.py --events data/events.jsonl --contract contracts/rl_event_contract.json --output output --write

test: run
	$(PYTHON) -m unittest discover -s tests -p "test_*.py"

clean:
	rm -rf output output_bad output_risky
