PYTHON ?= python3

.PHONY: run test clean

run:
	$(PYTHON) ops/audit_game_search.py --write

test: run
	$(PYTHON) -m unittest discover -s tests -p "test_*.py"

clean:
	rm -rf output output_bad output_risky
