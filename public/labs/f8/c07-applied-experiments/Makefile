PYTHON ?= python3

.PHONY: run test clean

run:
	$(PYTHON) ops/analyze_ab_experiment.py --write
	$(PYTHON) ops/validate_experiment_design.py --write
	$(PYTHON) ops/simulate_feature_flag_assignment.py --write
	$(PYTHON) ops/analyze_rag_experiment.py --write
	$(PYTHON) ops/summarize_metric_maturation.py --write
	$(PYTHON) ops/ci_experiment_gate.py --write
	$(PYTHON) ops/analyze_cluster_interference.py --write
	$(PYTHON) ops/audit_observational_effect.py --write

test: run
	$(PYTHON) -m unittest discover -s tests -p "test_*.py"

clean:
	rm -rf output output_bad output_risky
