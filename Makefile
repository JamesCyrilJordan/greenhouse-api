.PHONY: test test-cov test-html clean install

install:
	pip install -r requirements.txt

test:
	pytest

test-cov:
	pytest --cov=app --cov-report=term-missing

test-html:
	pytest --cov=app --cov-report=html
	@echo "Coverage report generated in htmlcov/index.html"

test-watch:
	pytest-watch

clean:
	find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} + 2>/dev/null || true
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf .tox
	rm -rf dist
	rm -rf build

