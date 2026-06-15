.PHONY: run test clean

run:
	python3 ops/plan_train_infer.py --write

test:
	python3 -m unittest discover -s tests -p "test_*.py"

clean:
	rm -f output/train_infer_report.json output/train_infer_decision.md
