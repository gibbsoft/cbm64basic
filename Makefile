# CBM64 BASIC Makefile

.PHONY: help install test docs clean lint run

help:
	@echo "CBM64 BASIC - Available targets:"
	@echo "  make install  - Install package in development mode"
	@echo "  make test     - Run all tests"
	@echo "  make docs     - Generate pydoc documentation"
	@echo "  make lint     - Check code style (if ruff installed)"
	@echo "  make run      - Start the BASIC editor"
	@echo "  make clean    - Remove generated files"

install:
	pip install -e .

test:
	pytest tests/test_basic.py -v

docs:
	@echo "Generating documentation..."
	pdoc -o docs src
	@echo "Documentation generated in docs/"

clean:
	rm -rf docs/*.html
	rm -rf __pycache__ src/__pycache__ tests/__pycache__
	rm -rf .pytest_cache
	rm -rf *.egg-info
	find . -name "*.pyc" -delete

lint:
	@which ruff > /dev/null && ruff check src/ || echo "ruff not installed, skipping lint"

run:
	python3 -m src.cbm64_editor
