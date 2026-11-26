PYTHON ?= python3
.PHONY: check test build
check:
	$(PYTHON) scripts/build.py --check
test:
	$(PYTHON) -m unittest discover -s tests -p 'test_*.py' -v
build: test
	$(PYTHON) scripts/build.py

.PHONY: test-uno
test-uno:
	$(PYTHON) scripts/test_uno.py
