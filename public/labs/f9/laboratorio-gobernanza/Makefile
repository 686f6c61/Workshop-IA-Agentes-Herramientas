PYTHON ?= python3

.PHONY: run test clean

run:
	$(PYTHON) ops/run_governance_lab.py --write
	$(PYTHON) ops/run_governance_lab.py --findings data/governance_findings_remediated.csv --output-dir output/remediated --write
	$(PYTHON) ops/run_governance_lab.py --findings data/governance_findings_student.csv --output-dir output/student --write
	$(PYTHON) ops/run_governance_lab.py --findings data/governance_findings_mi_equipo.csv --output-dir output/mi_equipo --write
	$(PYTHON) ops/check_student_submission.py --submission-dir solutions/reference --write
	$(PYTHON) ops/check_student_submission.py --submission-dir solutions/mi-equipo --output output/mi_equipo/student_submission_report.md --write --fail-on-missing

test: run
	$(PYTHON) -m unittest discover -s tests -p "test_*.py"

clean:
	rm -rf output output_bad output_risky
