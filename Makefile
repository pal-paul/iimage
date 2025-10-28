.PHONY: help install dev-install test coverage lint format type-check clean run docker-build docker-up docker-down deploy

# Default target
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "Image Object Detection API - Make Commands"
	@echo "==========================================="
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	pip install -r requirements.txt

dev-install: ## Install development dependencies
	pip install -r requirements.txt
	pip install pytest pytest-asyncio pytest-cov httpx faker mypy black flake8 isort

test: ## Run tests
	pytest tests/ -v

coverage: ## Run tests with coverage report
	pytest --cov=lib --cov=api --cov-report=html --cov-report=term-missing tests/
	@echo "Coverage report generated in htmlcov/index.html"

lint: ## Run linting checks
	flake8 lib/ api/ tests/ --max-line-length=100
	@echo "✓ Linting passed"

format: ## Format code with black and isort
	black lib/ api/ tests/
	isort lib/ api/ tests/
	@echo "✓ Code formatted"

type-check: ## Run type checking with mypy
	mypy lib/ api/
	@echo "✓ Type checking passed"

check: lint type-check ## Run all code quality checks
	@echo "✓ All checks passed"

clean: ## Clean up generated files
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov/ .coverage .pytest_cache/ dist/ build/
	@echo "✓ Cleaned up generated files"

run: ## Run the API server locally
	python run.py

dev: ## Run the API in development mode with auto-reload
	uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

docker-build: ## Build Docker image
	docker build -t image-detection-api:latest .

docker-build-prod: ## Build production Docker image
	docker build -f Dockerfile.prod -t image-detection-api:prod .

docker-up: ## Start services with docker-compose
	docker-compose up -d

docker-down: ## Stop services with docker-compose
	docker-compose down

docker-logs: ## View docker-compose logs
	docker-compose logs -f

docker-ps: ## Show running containers
	docker-compose ps

setup: ## Run initial setup
	chmod +x setup.sh deploy.sh
	./setup.sh

deploy: ## Deploy to production
	./deploy.sh production

monitoring-up: ## Start with monitoring stack
	docker-compose --profile monitoring up -d

test-api: ## Test API endpoints
	@echo "Testing API endpoints..."
	@curl -s http://localhost:8000/health | python -m json.tool
	@echo "\n✓ API is healthy"

benchmark: ## Run basic performance benchmark
	@echo "Running performance benchmark..."
	@ab -n 100 -c 10 http://localhost:8000/health
	@echo "✓ Benchmark complete"

init: setup install ## Initialize project (setup + install)
	@echo "✓ Project initialized successfully"

all: clean install check test ## Run full CI pipeline
	@echo "✓ All tasks completed successfully"
