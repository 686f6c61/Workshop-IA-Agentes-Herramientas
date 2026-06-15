.PHONY: run test clean

run:
	python3 ops/route_ai_principles.py --write

test:
	python3 -m unittest discover -s tests -p "test_*.py"

clean:
	rm -f output/principle_report.json output/principle_decision.md
