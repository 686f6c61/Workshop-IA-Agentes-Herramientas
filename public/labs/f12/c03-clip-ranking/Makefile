PYTHON ?= python3

.PHONY: run test clean

run:
	$(PYTHON) ops/run_contrastive_ranking.py --write --fail-on-invalid

test:
	$(PYTHON) -m unittest discover -s tests -p "test_*.py"

clean:
	rm -f output/clip_ranking_report.json output/clip_ranking_report.md output/similarity_matrix.csv output/retrieval_errors.csv output/contrastive_matrix.svg
