PYTHON ?= python3

.PHONY: run test clean

run:
	$(PYTHON) ops/run_final_review.py --write
	$(PYTHON) ops/run_final_review.py --data data/final_project_events_student.csv --output-dir output/student --write
	$(PYTHON) ops/check_student_submission.py --submission-dir solutions/reference --write

test: run
	$(PYTHON) -m unittest discover -s tests -p "test_*.py"

clean:
	rm -rf output output_bad output_risky
