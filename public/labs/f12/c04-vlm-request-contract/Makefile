PYTHON ?= python3

.PHONY: run test clean

run:
	$(PYTHON) ops/audit_vlm_requests.py --write --fail-on-invalid

test:
	$(PYTHON) -m unittest discover -s tests -p "test_*.py"

clean:
	rm -f output/vlm_request_report.json output/vlm_request_report.md output/vlm_architecture_contract.svg
	rm -rf output/request_contracts
