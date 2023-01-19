.PHONY: check test build unittests

check:
	$(MAKE) unittests

test: check

unittests:
	python -m unittest discover tests

build:
	python -m build -w
