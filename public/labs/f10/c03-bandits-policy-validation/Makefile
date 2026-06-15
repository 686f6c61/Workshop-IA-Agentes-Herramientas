PYTHON ?= python3

.PHONY: run test clean

run:
	$(PYTHON) ops/simulate_policy_gate.py --write
	$(PYTHON) ops/simulate_policy_gate.py --scenario data/routing_scenario_risky.json --output output_risky --write

test: run
	$(PYTHON) -m unittest discover -s tests -p "test_*.py"

clean:
	rm -rf output output_bad output_risky
