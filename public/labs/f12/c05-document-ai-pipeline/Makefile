PYTHON ?= python3

.PHONY: run test clean

run:
	$(PYTHON) ops/run_document_ai_pipeline.py --write --fail-on-invalid

test:
	$(PYTHON) -m unittest discover -s tests -p "test_*.py"

clean:
	rm -f output/document_ai_report.json output/document_ai_report.md output/document_pipeline.svg output/table_cells.csv
	rm -rf output/extractions
