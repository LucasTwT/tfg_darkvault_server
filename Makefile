.PHONY: help dev-up dev-down dev-build dev-logs prod-up prod-down prod-build prod-logs logs test db-up db-down

PYTHON := python3

help:
	@echo "DarkVault Backend - Makefile"
	@echo ""
	@echo "Usage:"
	@echo ""
	@echo "  make dev-up           Start in development mode (hot reload)"
	@echo "  make dev-down         Stop development stack"
	@echo "  make dev-build        Rebuild + start dev"
	@echo "  make dev-logs         Tail dev logs"
	@echo ""
	@echo "  make prod-up          Start in production mode (optimized)"
	@echo "  make prod-down        Stop production stack"
	@echo "  make prod-build       Rebuild + start prod"
	@echo "  make prod-logs        Tail prod logs"
	@echo ""
	@echo "  make db-up            Start only db"
	@echo "  make db-down          Stop only db"
	@echo "  make test             Run tests"

# ─── Development ───────────────────────────────────────────────────────
dev-up:
	@$(PYTHON) scripts/up.py --env dev

dev-down:
	@$(PYTHON) scripts/down.py --env dev

dev-build:
	@$(PYTHON) scripts/up.py --env dev --build

dev-logs:
	docker compose -f docker-compose.base.yml -f docker-compose.dev.yml logs -f

# ─── Production ────────────────────────────────────────────────────────
prod-up:
	@$(PYTHON) scripts/up.py --env prod

prod-down:
	@$(PYTHON) scripts/down.py --env prod

prod-build:
	@$(PYTHON) scripts/up.py --env prod --build

prod-logs:
	docker compose -f docker-compose.base.yml -f docker-compose.prod.yml logs -f

# ─── Utilities ─────────────────────────────────────────────────────────
db-up:
	docker compose -f docker-compose.base.yml -f docker-compose.dev.yml up db -d

db-down:
	docker compose -f docker-compose.base.yml -f docker-compose.dev.yml down db

logs:
	docker compose -f docker-compose.base.yml -f docker-compose.dev.yml logs -f

test:
	python -m pytest tests/ -v
