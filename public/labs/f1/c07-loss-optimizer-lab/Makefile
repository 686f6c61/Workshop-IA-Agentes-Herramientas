.PHONY: run test clean

run:
	python3 ops/run_training_grid.py --write

test:
	python3 -m unittest discover -s tests -p "test_*.py"

clean:
	rm -f output/training_report.json output/training_decision.md
