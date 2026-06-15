PYTHON ?= python3

.PHONY: run test clean

run:
	$(PYTHON) ops/run_multimodal_eval.py

test:
	$(PYTHON) ops/run_multimodal_eval.py
	$(PYTHON) -m unittest discover -s tests

clean:
	rm -rf output/*.json output/*.md output/*.csv output/*.svg
