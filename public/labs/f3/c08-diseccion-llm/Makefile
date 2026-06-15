run:
	python3 ops/dissect_llm_request.py --write

test:
	python3 ops/dissect_llm_request.py --write --fail-on-invalid
	python3 -m unittest discover -s tests -p "test_*.py"

