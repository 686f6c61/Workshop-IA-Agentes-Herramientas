.PHONY: run test clean

run:
	python3 ops/audit_architectures.py --write

test:
	python3 -m unittest discover -s tests -p "test_*.py"

clean:
	rm -f output/architecture_report.json output/architecture_decision.md
