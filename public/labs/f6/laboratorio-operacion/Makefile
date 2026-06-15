PYTHON ?= python3

.PHONY: run test clean

run:
	$(PYTHON) ops/operational_readiness.py --write
	$(PYTHON) ops/operational_readiness.py --manifest contracts/readiness_manifest_complete.json --output output/complete/operational_readiness.json --decision-output output/complete/readiness_decision.md --write
	$(PYTHON) ops/run_continuity_drill.py --write
	$(PYTHON) ops/run_continuity_drill.py --events data/continuity_events_recovered.jsonl --output-dir output/recovered --write
	$(PYTHON) ops/check_student_submission.py --submission-dir solutions/reference --write

test: run
	$(PYTHON) -m unittest discover -s tests -p "test_*.py"

clean:
	rm -rf output output_bad output_risky
