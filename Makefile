# Makefile for F.A.R.F.A.N Project Code Quality Automation

.PHONY: help install format lint test security clean fix-all pre-commit audit

# Default target
help:
	@echo "F.A.R.F.A.N Code Quality Automation"
	@echo "===================================="
	@echo "Available commands:"
	@echo "  make install      - Install all dependencies and tools"
	@echo "  make format       - Format code with black and isort"
	@echo "  make lint         - Run linting checks"
	@echo "  make test         - Run tests with coverage"
	@echo "  make security     - Run security scans"
	@echo "  make fix-all      - Apply all automated fixes"
	@echo "  make pre-commit   - Run pre-commit hooks"
	@echo "  make audit        - Run full code audit"
	@echo "  make clean        - Clean cache and temp files"

# Install dependencies
install:
	pip install --upgrade pip
	pip install -r requirements.txt
	pip install black isort flake8 mypy pylint
	pip install flake8-docstrings flake8-bugbear flake8-comprehensions
	pip install bandit safety
	pip install pytest pytest-cov pytest-xdist
	pip install pre-commit
	pre-commit install

# Format code
format:
	@echo "Formatting code..."
	black --line-length=100 .
	isort --profile=black --line-length=100 .
	@echo "✓ Formatting complete"

# Linting
lint:
	@echo "Running linters..."
	flake8 . --max-line-length=100 --extend-ignore=E203,W503
	mypy . --ignore-missing-imports || true
	pylint **/*.py --max-line-length=100 || true
	@echo "✓ Linting complete"

# Run tests
test:
	@echo "Running tests..."
	pytest tests/ -v --cov=. --cov-report=term-missing --cov-report=html
	@echo "✓ Tests complete"

# Security checks
security:
	@echo "Running security scans..."
	bandit -r . -f json -o bandit-report.json
	safety check --json || true
	@echo "✓ Security scan complete"

# Apply all fixes
fix-all:
	@echo "Applying all automated fixes..."
	python scripts/apply_code_fixes.py
	@echo "✓ All fixes applied"

# Run pre-commit
pre-commit:
	@echo "Running pre-commit hooks..."
	pre-commit run --all-files
	@echo "✓ Pre-commit checks complete"

# Full audit
audit:
	@echo "Running full code audit..."
	@make format
	@make lint
	@make security
	@make test
	python scripts/generate_quality_report.py
	@echo "✓ Audit complete - see quality_report.html"

# Clean up
clean:
	@echo "Cleaning up..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".coverage" -delete
	rm -rf .pytest_cache .mypy_cache .coverage htmlcov
	rm -rf build dist *.egg-info
	@echo "✓ Cleanup complete"

# Quick fix for common issues
quick-fix:
	@echo "Quick fixing common issues..."
	# Remove trailing whitespace
	find . -name "*.py" -exec sed -i '' 's/[[:space:]]*$$//' {} \;
	# Fix imports
	isort --profile=black --line-length=100 .
	# Format
	black --line-length=100 .
	@echo "✓ Quick fixes applied"
