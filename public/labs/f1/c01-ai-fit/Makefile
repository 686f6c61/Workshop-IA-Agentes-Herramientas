.PHONY: run test clean

run:
	python3 ops/triage_ai_fit.py --write

test:
	python3 -m unittest discover -s tests -p "test_*.py"

clean:
	rm -f output/ai_fit_report.json output/ai_fit_decision.md
