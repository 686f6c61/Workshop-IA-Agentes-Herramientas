PYTHON ?= python3

.PHONY: run test clean

run:
	$(PYTHON) ops/evaluate_classifier.py --write
	$(PYTHON) ops/run_semantic_search.py --write
	$(PYTHON) ops/evaluate_classifier.py --output-dir solutions/reference --write
	$(PYTHON) ops/run_semantic_search.py --output-dir solutions/reference --write
	$(PYTHON) ops/check_student_submission.py --submission-dir solutions/reference --write --fail-on-missing

test:
	$(PYTHON) -m unittest discover -s tests -p "test_*.py"

clean:
	rm -f output/classifier_metrics.json output/classifier_decision.md
	rm -f output/semantic_search_report.json output/semantic_search_decision.md output/semantic_search_traces.jsonl
	rm -f output/student_submission_report.md
	rm -f solutions/reference/classifier_metrics.json solutions/reference/classifier_decision.md
	rm -f solutions/reference/semantic_search_report.json solutions/reference/semantic_search_decision.md solutions/reference/semantic_search_traces.jsonl
