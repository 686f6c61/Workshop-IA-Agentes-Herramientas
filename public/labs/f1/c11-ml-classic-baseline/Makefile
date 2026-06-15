.PHONY: run test clean

run:
	python3 ops/run_ml_classic_baseline.py --write

test:
	python3 -m unittest discover -s tests -p "test_*.py"

clean:
	rm -f output/ml_classic_report.json output/ml_classic_decision.md
