PYTHON ?= python3

.PHONY: run test clean

run:
	$(PYTHON) ops/build_temporal_index.py
	$(PYTHON) ops/run_video_temporal_audit.py

test:
	$(PYTHON) -m unittest discover -s tests

clean:
	rm -rf output/*.json output/*.md output/*.csv output/*.svg output/case_cards output/storyboards
