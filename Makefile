.PHONY: dev test lint docker clean bootstrap help

help:
	@echo "StoryForge AI Developer Commands:"
	@echo "  make dev       - Start local development servers across apps"
	@echo "  make test      - Run test suites across monorepo"
	@echo "  make lint      - Run linter checks (Node + Python)"
	@echo "  make docker    - Launch database & background containers"
	@echo "  make clean     - Clean build artifacts and cache"
	@echo "  make bootstrap - Run setup script for initial environment"

dev:
	pnpm dev

test:
	pnpm test
	pytest tests/unit

lint:
	pnpm lint
	ruff check .

docker:
	docker compose -f docker/docker-compose.yml up -d postgres mongodb redis qdrant

clean:
	pnpm reset

bootstrap:
	./scripts/bootstrap.sh
