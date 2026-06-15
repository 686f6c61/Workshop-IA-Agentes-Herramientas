PYTHON ?= python3

.PHONY: run test clean

run:
	$(PYTHON) ops/run_computer_use_harness.py
	$(PYTHON) ops/estimate_capacity.py

test:
	$(PYTHON) ops/run_computer_use_harness.py
	$(PYTHON) ops/estimate_capacity.py
	$(PYTHON) -m unittest discover -s tests

clean:
	rm -rf output/*.json output/*.md output/*.csv output/*.svg output/trace_cards
