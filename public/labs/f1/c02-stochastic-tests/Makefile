.PHONY: run test clean

run:
	python3 ops/run_stochastic_eval.py --write

test:
	python3 -m unittest discover -s tests -p "test_*.py"

clean:
	rm -f output/stochastic_eval_report.json output/stochastic_eval_decision.md
