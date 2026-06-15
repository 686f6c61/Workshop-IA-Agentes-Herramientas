.PHONY: run test clean

run:
	python3 ops/inspect_tokens_embeddings.py --write

test:
	python3 -m unittest discover -s tests -p "test_*.py"

clean:
	rm -f output/token_embedding_report.json output/token_embedding_decision.md
