# Frustum Bucket Simulator - Makefile
# ======================================

# Configuration
PYTHON := python3
POETRY := poetry
PACKAGE := frustum_simulator
TIMESTAMP_DIR := .make
PYPI_REPO := pypi
TEST_PYPI_REPO := testpypi

# Colors for output
COLOR_RESET := \033[0m
COLOR_BOLD := \033[1m
COLOR_GREEN := \033[32m
COLOR_YELLOW := \033[33m

# ======================================
# Default target - show help
# ======================================

.DEFAULT_GOAL := help

# ======================================
# PHONY targets (targets that don't create files)
# ======================================

.PHONY: help dev check lint format build run pkg push-pypi push-test-pypi clean clean-all test version

# ======================================
# Main Targets
# ======================================

help: ## Show this help message
	@echo "$(COLOR_BOLD)Frustum Bucket Simulator - Available Make Targets$(COLOR_RESET)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(COLOR_GREEN)%-15s$(COLOR_RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(COLOR_YELLOW)Environment Variables:$(COLOR_RESET)"
	@echo "  PYPI_API_TOKEN      - Token for uploading to PyPI"
	@echo "  TEST_PYPI_API_TOKEN - Token for uploading to Test PyPI"
	@echo ""

dev: $(TIMESTAMP_DIR)/dev.timestamp ## Setup development environment with poetry install
	@echo "$(COLOR_GREEN)✓ Development environment ready$(COLOR_RESET)"

check: $(TIMESTAMP_DIR)/check.timestamp ## Run code quality checks (black + flake8)
	@echo "$(COLOR_GREEN)✓ Code quality checks passed$(COLOR_RESET)"

lint: $(TIMESTAMP_DIR)/lint.timestamp ## Run linting only (flake8)
	@echo "$(COLOR_GREEN)✓ Linting passed$(COLOR_RESET)"

format: $(TIMESTAMP_DIR)/format.timestamp ## Auto-format code with black
	@echo "$(COLOR_GREEN)✓ Code formatted$(COLOR_RESET)"

build: $(TIMESTAMP_DIR)/build.timestamp ## Build the package
	@echo "$(COLOR_GREEN)✓ Package built$(COLOR_RESET)"

run: $(TIMESTAMP_DIR)/dev.timestamp ## Run the frustum simulator
	@echo "$(COLOR_BOLD)Running Frustum Simulator...$(COLOR_RESET)"
	@$(POETRY) run frustum-sim

pkg: $(TIMESTAMP_DIR)/pkg.timestamp ## Build wheel and sdist packages for PyPI
	@echo "$(COLOR_GREEN)✓ PyPI packages created in dist/$(COLOR_RESET)"
	@ls -lh dist/

push-pypi: $(TIMESTAMP_DIR)/pkg.timestamp ## Push package to PyPI (requires PYPI_API_TOKEN)
	@if [ -z "$$PYPI_API_TOKEN" ]; then \
		echo "$(COLOR_YELLOW)Error: PYPI_API_TOKEN environment variable not set$(COLOR_RESET)"; \
		exit 1; \
	fi
	@echo "$(COLOR_BOLD)Publishing to PyPI...$(COLOR_RESET)"
	@$(POETRY) config pypi-token.pypi $$PYPI_API_TOKEN
	@$(POETRY) publish
	@echo "$(COLOR_GREEN)✓ Package published to PyPI$(COLOR_RESET)"

push-test-pypi: $(TIMESTAMP_DIR)/pkg.timestamp ## Push package to Test PyPI (requires TEST_PYPI_API_TOKEN)
	@if [ -z "$$TEST_PYPI_API_TOKEN" ]; then \
		echo "$(COLOR_YELLOW)Error: TEST_PYPI_API_TOKEN environment variable not set$(COLOR_RESET)"; \
		exit 1; \
	fi
	@echo "$(COLOR_BOLD)Publishing to Test PyPI...$(COLOR_RESET)"
	@$(POETRY) config repositories.testpypi https://test.pypi.org/legacy/
	@$(POETRY) config pypi-token.testpypi $$TEST_PYPI_API_TOKEN
	@$(POETRY) publish -r testpypi
	@echo "$(COLOR_GREEN)✓ Package published to Test PyPI$(COLOR_RESET)"

test: $(TIMESTAMP_DIR)/dev.timestamp ## Run tests (if available)
	@if [ -d "tests" ] || [ -f "test_*.py" ]; then \
		echo "$(COLOR_BOLD)Running tests...$(COLOR_RESET)"; \
		$(POETRY) run pytest -v; \
	else \
		echo "$(COLOR_YELLOW)No tests found. Run test_simulation.py manually if needed.$(COLOR_RESET)"; \
	fi

version: ## Show current package version
	@echo "$(COLOR_BOLD)Current version:$(COLOR_RESET) $$($(POETRY) version -s)"

update-deps: ## Update dependencies to latest versions
	@echo "$(COLOR_BOLD)Updating dependencies...$(COLOR_RESET)"
	@$(POETRY) update
	@rm -f $(TIMESTAMP_DIR)/dev.timestamp
	@echo "$(COLOR_GREEN)✓ Dependencies updated$(COLOR_RESET)"

clean: ## Clean build artifacts and cache files
	@echo "$(COLOR_BOLD)Cleaning build artifacts...$(COLOR_RESET)"
	@rm -rf dist/
	@rm -rf build/
	@rm -rf *.egg-info/
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type f -name "*.coverage" -delete
	@rm -rf .pytest_cache/
	@rm -rf $(TIMESTAMP_DIR)/build.timestamp $(TIMESTAMP_DIR)/pkg.timestamp
	@echo "$(COLOR_GREEN)✓ Cleaned$(COLOR_RESET)"

clean-all: clean ## Clean everything including dev environment
	@echo "$(COLOR_BOLD)Cleaning dev environment...$(COLOR_RESET)"
	@rm -rf $(TIMESTAMP_DIR)/
	@$(POETRY) env remove --all 2>/dev/null || true
	@echo "$(COLOR_GREEN)✓ All cleaned$(COLOR_RESET)"

# ======================================
# Timestamp-based Dependencies
# ======================================

# Create timestamp directory
$(TIMESTAMP_DIR):
	@mkdir -p $(TIMESTAMP_DIR)

# Development environment setup
$(TIMESTAMP_DIR)/dev.timestamp: pyproject.toml poetry.lock | $(TIMESTAMP_DIR)
	@echo "$(COLOR_BOLD)Setting up development environment...$(COLOR_RESET)"
	@$(POETRY) install
	@touch $@

# Code formatting
$(TIMESTAMP_DIR)/format.timestamp: $(TIMESTAMP_DIR)/dev.timestamp $(shell find $(PACKAGE) -name "*.py")
	@echo "$(COLOR_BOLD)Formatting code with black...$(COLOR_RESET)"
	@$(POETRY) run black $(PACKAGE)/
	@touch $@

# Linting
$(TIMESTAMP_DIR)/lint.timestamp: $(TIMESTAMP_DIR)/dev.timestamp $(shell find $(PACKAGE) -name "*.py")
	@echo "$(COLOR_BOLD)Running flake8...$(COLOR_RESET)"
	@$(POETRY) run flake8 $(PACKAGE)/
	@touch $@

# Full code check (format + lint)
$(TIMESTAMP_DIR)/check.timestamp: $(TIMESTAMP_DIR)/format.timestamp $(TIMESTAMP_DIR)/lint.timestamp
	@echo "$(COLOR_BOLD)Running code quality checks...$(COLOR_RESET)"
	@$(POETRY) run black $(PACKAGE)/ --check
	@$(POETRY) run flake8 $(PACKAGE)/
	@touch $@

# Build package
$(TIMESTAMP_DIR)/build.timestamp: $(TIMESTAMP_DIR)/dev.timestamp $(TIMESTAMP_DIR)/check.timestamp $(shell find $(PACKAGE) -name "*.py")
	@echo "$(COLOR_BOLD)Building package...$(COLOR_RESET)"
	@$(POETRY) build
	@touch $@

# Create PyPI packages
$(TIMESTAMP_DIR)/pkg.timestamp: $(TIMESTAMP_DIR)/build.timestamp pyproject.toml
	@echo "$(COLOR_BOLD)Creating PyPI distribution packages...$(COLOR_RESET)"
	@rm -rf dist/
	@$(POETRY) build
	@touch $@
	@echo ""
	@echo "$(COLOR_BOLD)Package contents:$(COLOR_RESET)"
	@ls -1 dist/
