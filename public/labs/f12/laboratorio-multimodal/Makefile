.PHONY: run test clean

run:
	python3 ops/run_multimodal_release_lab.py

test:
	python3 ops/run_multimodal_release_lab.py
	python3 -m unittest discover -s tests

clean:
	rm -rf output/*.json output/*.md output/*.csv output/*.svg
