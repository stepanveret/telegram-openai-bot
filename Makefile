.PHONY: help
help:              ## Show the help.
	@echo "Usage: make <target>"
	@echo ""
	@echo "Targets:"
	@fgrep "##" Makefile | fgrep -v fgrep

.PHONY: show
show:              ## Show the current environment.
	@echo "Current environment:"
	@python -V
	@python -m site

.PHONY: install-dev-tools
install-dev-tools: ## Install dev tools(linters, formatters etc.).
	@pip install isort black flake8

.PHONY: fmt
fmt:               ## Format code using black & isort.
	@isort .
	@black --preview --line-length=119 .

.PHONY: lint
lint:              ## Run flake8, black, isort checks.
	@flake8 --max-line-length 120 .
	@isort --check-only .
	@black --check --line-length=120 .

.PHONY: build-container
build-container:   ## Build arbitrary container with given name suffix and path to Dockerfile.
	@docker build -t telegram_openai_bot .

.PHONY: run-container
run-container:     ## Run arbitrary container by given name suffix with MLflow environment variables.
	@docker run --rm -it \
 	-e OPENAI_API_KEY=${OPENAI_API_KEY} \
 	-e GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/google_credentials.json \
	-e TELEGRAM_YJACDNX_API_KEY=${TELEGRAM_YJACDNX_API_KEY} \
	-e TELEGRAM_YJACDNX_PASSWORD=${TELEGRAM_YJACDNX_PASSWORD} \
	--name telegram_bot_instance \
	-v "/home/snveret/skilful-charmer-324709-97f19a3c3dfd.json:/app/credentials/google_credentials.json" \
  	telegram_openai_bot

# 	-e TELEGRAM_API_TOKEN=${TELEGRAM_API_TOKEN} \
