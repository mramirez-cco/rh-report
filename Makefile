.PHONY: help install install-dev uninstall clean test lint format build publish run

# Variables
PYTHON := python3
PIP := pip3
PACKAGE_NAME := rh-report
SRC_DIR := src/rh_report

# Colores para output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
NC := \033[0m # No Color

help: ## Muestra esta ayuda
	@echo "$(BLUE)Makefile para $(PACKAGE_NAME)$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

install: ## Instala el paquete en modo editable
	@echo "$(BLUE)Instalando $(PACKAGE_NAME) en modo editable...$(NC)"
	$(PIP) install -e .
	@echo "$(GREEN)✓ Instalación completa. Usa: rh-report --help$(NC)"

install-dev: ## Instala el paquete con dependencias de desarrollo
	@echo "$(BLUE)Instalando $(PACKAGE_NAME) en modo desarrollo...$(NC)"
	$(PIP) install -e ".[dev]"
	@echo "$(GREEN)✓ Instalación de desarrollo completa$(NC)"

uninstall: ## Desinstala el paquete
	@echo "$(YELLOW)Desinstalando $(PACKAGE_NAME)...$(NC)"
	$(PIP) uninstall -y $(PACKAGE_NAME)
	@echo "$(GREEN)✓ Desinstalación completa$(NC)"

clean: ## Limpia archivos temporales y cache
	@echo "$(BLUE)Limpiando archivos temporales...$(NC)"
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	find . -type d -name '*.egg-info' -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ .pytest_cache/ .coverage htmlcov/
	rm -f cache_results.json full_image_report.csv
	@echo "$(GREEN)✓ Limpieza completa$(NC)"

test: ## Ejecuta los tests
	@echo "$(BLUE)Ejecutando tests...$(NC)"
	pytest tests/ -v --cov=$(SRC_DIR) --cov-report=term-missing
	@echo "$(GREEN)✓ Tests completados$(NC)"

lint: ## Ejecuta el linter (flake8)
	@echo "$(BLUE)Ejecutando linter...$(NC)"
	flake8 $(SRC_DIR) --max-line-length=100 --exclude=__pycache__
	@echo "$(GREEN)✓ Linting completo$(NC)"

format: ## Formatea el código con black
	@echo "$(BLUE)Formateando código...$(NC)"
	black $(SRC_DIR)
	@echo "$(GREEN)✓ Formateo completo$(NC)"

typecheck: ## Verifica tipos con mypy
	@echo "$(BLUE)Verificando tipos...$(NC)"
	mypy $(SRC_DIR)
	@echo "$(GREEN)✓ Type checking completo$(NC)"

build: clean ## Construye el paquete para distribución
	@echo "$(BLUE)Construyendo paquete...$(NC)"
	$(PYTHON) -m build
	@echo "$(GREEN)✓ Paquete construido en dist/$(NC)"

publish: build ## Publica el paquete a PyPI (requiere credenciales)
	@echo "$(YELLOW)Publicando a PyPI...$(NC)"
	$(PYTHON) -m twine upload dist/*
	@echo "$(GREEN)✓ Paquete publicado$(NC)"

publish-test: build ## Publica a TestPyPI para pruebas
	@echo "$(YELLOW)Publicando a TestPyPI...$(NC)"
	$(PYTHON) -m twine upload --repository testpypi dist/*
	@echo "$(GREEN)✓ Paquete publicado en TestPyPI$(NC)"

run: ## Ejecuta el comando con archivo de ejemplo
	@echo "$(BLUE)Ejecutando rh-report...$(NC)"
	@if [ -f "reporte_20260115.xlsx" ]; then \
		rh-report reporte_20260115.xlsx; \
	else \
		echo "$(YELLOW)⚠ No se encontró reporte_20260115.xlsx$(NC)"; \
		echo "Uso: make run FILE=tu_archivo.xlsx"; \
	fi

run-example: ## Ejecuta ejemplo con 5 workers y cache desactivado
	@echo "$(BLUE)Ejecutando ejemplo...$(NC)"
	rh-report --workers 5 --no-cache reporte_20260115.xlsx

check: lint typecheck ## Ejecuta todas las verificaciones (lint + typecheck)
	@echo "$(GREEN)✓ Todas las verificaciones pasaron$(NC)"

dev-setup: install-dev ## Configura el entorno de desarrollo completo
	@echo "$(BLUE)Configurando entorno de desarrollo...$(NC)"
	pre-commit install 2>/dev/null || echo "pre-commit no instalado, saltando..."
	@echo "$(GREEN)✓ Entorno de desarrollo listo$(NC)"

upgrade-deps: ## Actualiza las dependencias
	@echo "$(BLUE)Actualizando dependencias...$(NC)"
	$(PIP) install --upgrade pip setuptools wheel
	$(PIP) install --upgrade -r requirements.txt
	@echo "$(GREEN)✓ Dependencias actualizadas$(NC)"

venv: ## Crea un entorno virtual
	@echo "$(BLUE)Creando entorno virtual...$(NC)"
	$(PYTHON) -m venv venv
	@echo "$(GREEN)✓ Entorno virtual creado$(NC)"
	@echo "$(YELLOW)Actívalo con: source venv/bin/activate$(NC)"

stats: ## Muestra estadísticas del código
	@echo "$(BLUE)Estadísticas del código:$(NC)"
	@echo ""
	@echo "Líneas de código:"
	@find $(SRC_DIR) -name '*.py' | xargs wc -l | tail -1
	@echo ""
	@echo "Archivos Python:"
	@find $(SRC_DIR) -name '*.py' | wc -l
	@echo ""
	@echo "Funciones y clases:"
	@grep -r "^def \|^class " $(SRC_DIR) | wc -l

docker-build: ## Construye imagen Docker
	@echo "$(BLUE)Construyendo imagen Docker...$(NC)"
	docker build -t $(PACKAGE_NAME):latest .
	@echo "$(GREEN)✓ Imagen Docker construida$(NC)"

docker-run: ## Ejecuta en Docker
	@echo "$(BLUE)Ejecutando en Docker...$(NC)"
	docker run --rm -v $(PWD):/data $(PACKAGE_NAME):latest --help
