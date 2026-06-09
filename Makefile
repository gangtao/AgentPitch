.PHONY: install test test-cov serve docker-build docker-build-no-cache docker-up docker-down docker-image docker-image-no-cache docker-run copy-to deploy-matches help

help:
	@echo "Available commands:"
	@echo "  make install      - Install Agent Pitch locally with all sandboxes (JS + Wasm)"
	@echo "  make test         - Run the test suite"
	@echo "  make test-cov     - Run the test suite with coverage reporting"
	@echo "  make serve        - Start the HTTP server and UI locally (port 8765)"
	@echo "  make docker-build - Build the Agent Pitch Docker image (via compose)"
	@echo "  make docker-up    - Run the application in a Docker container (via compose, port 8765)"
	@echo "  make docker-down  - Stop the compose Docker container"
	@echo "  make docker-image          - Build the standalone Docker image 'agent-pitch:latest'"
	@echo "  make docker-image-no-cache - Build the standalone Docker image without cache"
	@echo "  make docker-build-no-cache - Build the Agent Pitch Docker image without cache (via compose)"
	@echo "  make docker-run            - Run the standalone Docker image with local ./data volume mapped"
	@echo "  make deploy-matches        - Publish ./fifa2026/matches to Surge.sh"

install:
	pip install --upgrade pip
	pip install -e '.[all]'

test:
	pytest

test-cov:
	pytest --cov

serve:
	agent-pitch serve --data-dir ./data

docker-build:
	docker compose build

docker-build-no-cache:
	docker compose build --no-cache

docker-up:
	docker compose up -d

docker-down:
	docker compose down

docker-image:
	docker build -t agent-pitch:latest .

docker-image-no-cache:
	docker build --no-cache -t agent-pitch:latest .

docker-run:
	docker run -d -p 8765:8765 -v $(PWD)/data:/app/data --name agent-pitch agent-pitch:latest

deploy-matches:
	surge ./fifa2026/matches

