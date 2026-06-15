.PHONY: run test clean

run:
	python3 ops/check_backprop.py --write

test:
	python3 -m unittest discover -s tests -p "test_*.py"

clean:
	rm -f output/backprop_report.json output/backprop_decision.md
