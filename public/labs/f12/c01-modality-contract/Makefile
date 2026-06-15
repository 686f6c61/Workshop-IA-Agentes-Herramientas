.PHONY: run test clean

run:
	python3 ops/evaluate_modality_manifest.py --write --fail-on-invalid

test:
	python3 -m unittest discover -s tests -p "test_*.py"

clean:
	rm -f output/modality_contract_report.json output/modality_contract_report.md
