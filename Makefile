PYTHON ?= python3

.PHONY: test
test:
	$(PYTHON) -m unittest discover -s tests -p 'test_*.py'

.PHONY: compile
compile:
	$(PYTHON) -m compileall georesolve tests

.PHONY: smoke-live
smoke-live:
	GEORESOLVE_RUN_LIVE_TESTS=1 $(PYTHON) -m unittest tests.test_live_census_smoke
