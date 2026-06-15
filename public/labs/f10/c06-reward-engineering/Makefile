PYTHON ?= python3

.PHONY: run test clean

run:
	$(PYTHON) ops/audit_reward_card.py --write
	$(PYTHON) ops/calibrate_thresholds.py --write
	$(PYTHON) ops/validate_trace.py --write
	$(PYTHON) ops/audit_reward_card.py --spec data/reward_spec_bad.json --output output_bad --write
	$(PYTHON) ops/validate_trace.py --trace data/reward_run_trace_bad.json --output output_bad/trace_validation_report.json --write

test: run
	$(PYTHON) -m unittest discover -s tests -p "test_*.py"

clean:
	rm -rf output output_bad output_risky
