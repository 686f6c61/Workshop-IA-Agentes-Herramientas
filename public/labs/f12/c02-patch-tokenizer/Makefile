.PHONY: run test clean

run:
	python3 ops/inspect_patches.py --write --fail-on-invalid

test:
	python3 -m unittest discover -s tests -p "test_*.py"

clean:
	rm -f output/patch_report.json output/patch_report.md output/patch_grid.svg
