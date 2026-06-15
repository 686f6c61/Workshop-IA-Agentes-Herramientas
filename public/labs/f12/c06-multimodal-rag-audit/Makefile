PYTHON ?= python3

.PHONY: run test clean

run:
	$(PYTHON) ops/run_multimodal_rag_audit.py

test:
	$(PYTHON) -m unittest discover -s tests

clean:
	rm -rf output/*.json output/*.md output/*.csv output/*.svg output/answer_cards
