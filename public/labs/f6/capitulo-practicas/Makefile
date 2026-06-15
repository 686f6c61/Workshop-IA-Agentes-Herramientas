PYTHON ?= python3

.PHONY: run test clean

run:
	$(PYTHON) ops/run_f6_practices.py --all --write
	$(PYTHON) ops/ai/handoff_queue.py
	$(PYTHON) ops/ai/incident_review.py

test: run
	$(PYTHON) -m unittest discover -s tests -p "test_*.py"

clean:
	rm -rf output output_bad output_risky
