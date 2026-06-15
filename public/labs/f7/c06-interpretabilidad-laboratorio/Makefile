PYTHON ?= python3

.PHONY: run test clean

run:
	$(PYTHON) ops/ai/interpretability_audit.py --write
	$(PYTHON) ops/build_release_eval_pack.py --write
	$(PYTHON) ops/build_release_eval_pack.py --rag-report rag_eval_report.json --evaluator-report evaluator_metaeval.json --output-dir output/student --write

test: run
	$(PYTHON) -m unittest discover -s tests -p "test_*.py"

clean:
	rm -rf output output_bad output_risky
