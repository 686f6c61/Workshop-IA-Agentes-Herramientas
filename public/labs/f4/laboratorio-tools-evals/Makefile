PYTHON ?= python3

.PHONY: run test clean

run:
	$(PYTHON) ops/evaluate_mini_rag.py --write
	$(PYTHON) ops/evaluate_router.py --write
	$(PYTHON) ops/check_student_submission.py --submission-dir solutions/reference --write

test: run
	$(PYTHON) -m unittest discover -s tests -p "test_*.py"

clean:
	rm -rf output output_bad output_risky
