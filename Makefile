ENV_FILE ?= .env.lelab

.PHONY: help lelab install sync lock clean

help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'

lelab: ## Run LeLab with the project env file
	uv run --env-file $(ENV_FILE) lelab

install: ## Install all dependencies (including dev group)
	uv sync --all-groups

sync: install ## Alias for install

lock: ## Refresh uv.lock
	uv lock

clean: ## Remove caches and build artifacts
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	rm -rf .pytest_cache .ruff_cache .mypy_cache build dist *.egg-info
