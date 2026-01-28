# Makefile para automatización de calidad de código del proyecto F.A.R.F.A.N

.PHONY: help install format lint test security clean fix-all pre-commit audit quick-fix

# Target por defecto
help:
	@echo "F.A.R.F.A.N - Automatización de Calidad de Código"
	@echo "================================================="
	@echo "Comandos disponibles:"
	@echo "  make install      - Instalar todas las dependencias y herramientas"
	@echo "  make format       - Formatear código con black e isort"
	@echo "  make lint         - Ejecutar verificaciones de linting"
	@echo "  make test         - Ejecutar tests con cobertura"
	@echo "  make security     - Ejecutar escaneos de seguridad"
	@echo "  make fix-all      - Aplicar todos los fixes automáticos"
	@echo "  make pre-commit   - Ejecutar pre-commit hooks"
	@echo "  make audit        - Ejecutar auditoría completa de código"
	@echo "  make clean        - Limpiar archivos cache y temporales"
	@echo "  make quick-fix    - Fixes rápidos para problemas comunes"

# Instalar dependencias
install:
	pip install --upgrade pip
	pip install black isort flake8 mypy pylint ruff
	pip install flake8-docstrings flake8-bugbear flake8-comprehensions
	pip install bandit safety pip-audit
	pip install pytest pytest-cov pytest-xdist
	pip install pre-commit radon
	pre-commit install
	@echo "✓ Instalación completada"

# Formatear código
format:
	@echo "Formateando código..."
	black --line-length=100 .
	isort --profile=black --line-length=100 .
	@echo "✓ Formateo completado"

# Linting
lint:
	@echo "Ejecutando linters..."
	ruff check .
	flake8 . --max-line-length=100 --extend-ignore=E203,W503
	mypy . --ignore-missing-imports || true
	pylint **/*.py --max-line-length=100 || true
	@echo "✓ Linting completado"

# Ejecutar tests
test:
	@echo "Ejecutando tests..."
	pytest tests/ -v --cov=. --cov-report=term-missing --cov-report=html || true
	@echo "✓ Tests completados"

# Verificaciones de seguridad
security:
	@echo "Ejecutando escaneos de seguridad..."
	bandit -r . -f json -o bandit-report.json
	safety check --json || true
	pip-audit || true
	@echo "✓ Escaneo de seguridad completado"

# Aplicar todos los fixes
fix-all:
	@echo "Aplicando todos los fixes automáticos..."
	python scripts/apply_code_fixes.py
	@echo "✓ Todos los fixes aplicados"

# Ejecutar pre-commit
pre-commit:
	@echo "Ejecutando pre-commit hooks..."
	pre-commit run --all-files
	@echo "✓ Pre-commit checks completados"

# Auditoría completa
audit:
	@echo "Ejecutando auditoría completa de código..."
	@make format
	@make lint
	@make security
	@make test
	python scripts/generate_quality_report.py || true
	@echo "✓ Auditoría completada - ver quality_report.html"

# Limpiar archivos
clean:
	@echo "Limpiando..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".coverage" -delete
	rm -rf .pytest_cache .mypy_cache .coverage htmlcov
	rm -rf build dist *.egg-info
	rm -rf .ruff_cache
	@echo "✓ Limpieza completada"

# Fix rápido para problemas comunes
quick-fix:
	@echo "Aplicando fixes rápidos..."
	# Eliminar espacios en blanco al final
	find . -name "*.py" -type f -exec sed -i 's/[[:space:]]*$$//' {} \; 2>/dev/null || true
	# Eliminar imports no usados
	autoflake --remove-all-unused-imports --remove-unused-variables --in-place --recursive .
	# Ordenar imports
	isort --profile=black --line-length=100 .
	# Formatear
	black --line-length=100 .
	# Aplicar fixes de Ruff
	ruff check --fix .
	@echo "✓ Fixes rápidos aplicados"

# Verificar calidad antes de commit
check:
	@echo "Verificando calidad de código..."
	black --check --diff .
	isort --check-only --diff .
	ruff check .
	flake8 . --count --statistics
	@echo "✓ Verificación completada"

# Actualizar herramientas
update-tools:
	@echo "Actualizando herramientas..."
	pip install --upgrade black isort flake8 mypy pylint ruff bandit safety pre-commit
	pre-commit autoupdate
	@echo "✓ Herramientas actualizadas"
