PYTHON ?= python3

.PHONY: run test clean

run:
	$(PYTHON) ops/run_realtime_voice_audit.py

test:
	$(PYTHON) -m unittest discover -s tests

clean:
	rm -rf output/*.json output/*.md output/*.csv output/*.svg output/audio output/turn_cards
