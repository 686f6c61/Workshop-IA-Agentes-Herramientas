.PHONY: run test clean

run:
	python3 ops/run_neuron_contract.py --write

test:
	python3 -m unittest discover -s tests -p "test_*.py"

clean:
	rm -f output/neuron_report.json output/neuron_decision.md
