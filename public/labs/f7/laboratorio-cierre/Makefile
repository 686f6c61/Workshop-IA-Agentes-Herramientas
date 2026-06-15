PYTHON ?= python3

.PHONY: run test clean

run:
	$(PYTHON) ops/build_release_eval_pack.py --write
	$(PYTHON) ops/build_release_eval_pack.py --rag-report evidence/rag_eval_report_student.json --evaluator-report evidence/evaluator_metaeval_student.json --output-dir output/student --write
	$(PYTHON) ops/check_student_submission.py --submission-dir solutions/reference --write

test: run
	$(PYTHON) -m unittest discover -s tests -p "test_*.py"

clean:
	rm -rf output output_bad output_risky
