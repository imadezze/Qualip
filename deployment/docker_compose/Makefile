# Onyx Docker Compose Makefile
# This file provides convenient commands for managing the Onyx development environment

# Variables
PROJECT_NAME = onyx
COMPOSE_FILES_BASE = -f docker-compose.prod.yml
COMPOSE_FILES_DEV_BACKEND = $(COMPOSE_FILES_BASE) -f docker-compose.dev-local.yml
COMPOSE_FILES_DEV_FULL = $(COMPOSE_FILES_DEV_BACKEND) -f docker-compose.dev-web.yml
COMPOSE_FILES_DEV_PORTS = $(COMPOSE_FILES_DEV_BACKEND) -f docker-compose.dev.yml
COMPOSE_FILES_DEV_FULL_PORTS = $(COMPOSE_FILES_DEV_FULL) -f docker-compose.dev.yml
COMPOSE = docker compose -p $(PROJECT_NAME)

.PHONY: help
help: ## Show this help message
	@echo "Onyx Development Environment Commands"
	@echo "======================================"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Common Workflows:"
	@echo "  make dev-backend-fast    # Backend dev + Production frontend (FAST, recommended for testing)"
	@echo "  make dev-backend-hot     # Backend dev + Dev frontend (SLOW, hot reload for web)"
	@echo "  make dev-backend         # Backend dev only, no frontend exposed"
	@echo "  make prod                # Full production mode"

# ============================================================================
# Production Mode
# ============================================================================

.PHONY: prod
prod: ## Start full production mode (no hot reload)
	$(COMPOSE) $(COMPOSE_FILES_BASE) up -d --build

.PHONY: prod-up
prod-up: ## Start production without rebuilding
	$(COMPOSE) $(COMPOSE_FILES_BASE) up -d

.PHONY: prod-down
prod-down: ## Stop production mode
	$(COMPOSE) $(COMPOSE_FILES_BASE) down

# ============================================================================
# Development Mode - Backend Only (Fastest for backend development)
# ============================================================================

.PHONY: dev-backend
dev-backend: ## Start backend dev mode (Python hot reload, no frontend ports)
	$(COMPOSE) $(COMPOSE_FILES_DEV_BACKEND) up -d --build

.PHONY: dev-backend-up
dev-backend-up: ## Start backend dev without rebuilding
	$(COMPOSE) $(COMPOSE_FILES_DEV_BACKEND) up -d

# ============================================================================
# Development Mode - Backend Dev + Production Frontend (RECOMMENDED)
# ============================================================================

.PHONY: dev-backend-fast
dev-backend-fast: ## Start backend dev + production frontend (FAST, recommended)
	$(COMPOSE) $(COMPOSE_FILES_DEV_PORTS) up -d --build
	@echo ""
	@echo "✅ Started in FAST mode!"
	@echo "   - App: http://localhost:80 (access the app here)"
	@echo "   - Backend API: http://localhost:8080 (DEV mode with hot reload)"
	@echo "   - Frontend direct: http://localhost:3000 (no API proxy - don't use for testing)"
	@echo ""
	@echo "Python changes = instant reload"
	@echo "Web changes = need rebuild (make rebuild-web)"

.PHONY: dev-backend-fast-up
dev-backend-fast-up: ## Start backend dev + production frontend without rebuild
	$(COMPOSE) $(COMPOSE_FILES_DEV_PORTS) up -d

# ============================================================================
# Development Mode - Backend Dev + Frontend Dev (Hot Reload Everything)
# ============================================================================

.PHONY: dev-backend-hot
dev-backend-hot: ## Start full dev mode (backend + frontend hot reload, SLOW initial load)
	$(COMPOSE) $(COMPOSE_FILES_DEV_FULL_PORTS) up -d --build
	@echo ""
	@echo "✅ Started in HOT RELOAD mode!"
	@echo "   - Backend: http://localhost:8080 (DEV mode with hot reload)"
	@echo "   - Frontend: http://localhost:3000 (DEV mode with hot reload)"
	@echo ""
	@echo "⚠️  First page load will be SLOW (10-30s) - Next.js compiling on demand"
	@echo "✅ After first load, pages are cached and faster"
	@echo "✅ Any code change = instant browser update"

.PHONY: dev-backend-hot-up
dev-backend-hot-up: ## Start full dev mode without rebuild
	$(COMPOSE) $(COMPOSE_FILES_DEV_FULL_PORTS) up -d

# ============================================================================
# Stop Commands
# ============================================================================

.PHONY: down
down: ## Stop all containers (keeps volumes)
	$(COMPOSE) $(COMPOSE_FILES_DEV_FULL_PORTS) down

.PHONY: down-volumes
down-volumes: ## Stop all containers and remove volumes (DELETES DATA!)
	$(COMPOSE) $(COMPOSE_FILES_DEV_FULL_PORTS) down -v
	@echo "⚠️  All volumes removed - database data deleted!"

.PHONY: stop
stop: ## Stop all containers without removing them
	$(COMPOSE) $(COMPOSE_FILES_DEV_FULL_PORTS) stop

# ============================================================================
# Restart Commands
# ============================================================================

.PHONY: restart
restart: ## Restart all services
	$(COMPOSE) $(COMPOSE_FILES_DEV_FULL_PORTS) restart

.PHONY: restart-api
restart-api: ## Restart API server only
	$(COMPOSE) $(COMPOSE_FILES_DEV_FULL_PORTS) restart api_server

.PHONY: restart-web
restart-web: ## Restart web server only
	$(COMPOSE) $(COMPOSE_FILES_DEV_FULL_PORTS) restart web_server

.PHONY: restart-background
restart-background: ## Restart background worker
	$(COMPOSE) $(COMPOSE_FILES_DEV_FULL_PORTS) restart background

# ============================================================================
# Build Commands
# ============================================================================

.PHONY: build
build: ## Build all images
	$(COMPOSE) $(COMPOSE_FILES_DEV_FULL_PORTS) build

.PHONY: build-api
build-api: ## Build backend API image
	$(COMPOSE) $(COMPOSE_FILES_DEV_FULL_PORTS) build api_server background

.PHONY: build-web
build-web: ## Build web server image
	$(COMPOSE) $(COMPOSE_FILES_DEV_FULL_PORTS) build web_server

.PHONY: build-web-prod
build-web-prod: ## Build production web server
	$(COMPOSE) $(COMPOSE_FILES_DEV_PORTS) build web_server

.PHONY: build-models
build-models: ## Build model server images
	$(COMPOSE) $(COMPOSE_FILES_DEV_FULL_PORTS) build inference_model_server indexing_model_server

.PHONY: rebuild-web
rebuild-web: ## Rebuild and restart web server (production)
	$(COMPOSE) $(COMPOSE_FILES_DEV_PORTS) build web_server
	$(COMPOSE) $(COMPOSE_FILES_DEV_PORTS) up -d web_server
	@echo "✅ Web server rebuilt and restarted"

# ============================================================================
# Logs
# ============================================================================

.PHONY: logs
logs: ## Show logs from all services
	$(COMPOSE) $(COMPOSE_FILES_DEV_FULL_PORTS) logs -f

.PHONY: logs-api
logs-api: ## Show API server logs
	$(COMPOSE) $(COMPOSE_FILES_DEV_FULL_PORTS) logs -f api_server

.PHONY: logs-web
logs-web: ## Show web server logs
	$(COMPOSE) $(COMPOSE_FILES_DEV_FULL_PORTS) logs -f web_server

.PHONY: logs-background
logs-background: ## Show background worker logs
	$(COMPOSE) $(COMPOSE_FILES_DEV_FULL_PORTS) logs -f background

.PHONY: logs-nginx
logs-nginx: ## Show nginx logs
	$(COMPOSE) $(COMPOSE_FILES_DEV_FULL_PORTS) logs -f nginx

# ============================================================================
# Status & Info
# ============================================================================

.PHONY: ps
ps: ## Show running containers
	$(COMPOSE) $(COMPOSE_FILES_DEV_FULL_PORTS) ps

.PHONY: status
status: ps ## Alias for ps

.PHONY: info
info: ## Show current configuration
	@echo "Project: $(PROJECT_NAME)"
	@echo "Compose files: $(COMPOSE_FILES_DEV_FULL_PORTS)"
	@echo ""
	@echo "Services:"
	@$(COMPOSE) $(COMPOSE_FILES_DEV_FULL_PORTS) ps

# ============================================================================
# Shell Access
# ============================================================================

.PHONY: shell-api
shell-api: ## Open bash shell in API container
	docker exec -it onyx-api_server-1 bash

.PHONY: shell-web
shell-web: ## Open sh shell in web container
	docker exec -it onyx-web_server-1 sh

.PHONY: shell-db
shell-db: ## Open psql shell in database
	docker exec -it onyx-relational_db-1 psql -U postgres

# ============================================================================
# Database
# ============================================================================

.PHONY: db-migrate
db-migrate: ## Run database migrations
	docker exec onyx-api_server-1 alembic upgrade head

.PHONY: db-shell
db-shell: shell-db ## Alias for shell-db

# ============================================================================
# Cleanup
# ============================================================================

.PHONY: clean
clean: ## Remove stopped containers and dangling images
	docker compose -p $(PROJECT_NAME) down --remove-orphans
	docker system prune -f

.PHONY: clean-all
clean-all: ## Remove all containers, images, and volumes (NUCLEAR OPTION!)
	docker compose -p $(PROJECT_NAME) down -v --rmi all
	@echo "⚠️  Everything removed! Run 'make dev-backend-fast' to rebuild."

# ============================================================================
# Quick Switches
# ============================================================================

.PHONY: switch-to-fast
switch-to-fast: ## Switch from hot reload to fast mode (prod frontend)
	$(COMPOSE) $(COMPOSE_FILES_DEV_FULL_PORTS) stop web_server
	$(COMPOSE) $(COMPOSE_FILES_DEV_PORTS) up -d web_server
	@echo "✅ Switched to FAST mode (production frontend)"

.PHONY: switch-to-hot
switch-to-hot: ## Switch from fast to hot reload mode (dev frontend)
	$(COMPOSE) $(COMPOSE_FILES_DEV_PORTS) stop web_server
	$(COMPOSE) $(COMPOSE_FILES_DEV_FULL_PORTS) up -d web_server
	@echo "✅ Switched to HOT RELOAD mode (dev frontend)"
	@echo "⚠️  First page load will be slow"

# ============================================================================
# User Management
# ============================================================================

.PHONY: create-user
create-user: ## Create test user (email: test@example.com, password: test1234)
	@curl -X POST http://localhost:8080/auth/register \
	  -H "Content-Type: application/json" \
	  -d '{"email": "test@example.com", "password": "test1234"}' \
	  && echo "" && echo "✅ User created: test@example.com / test1234"

# ============================================================================
# Default target
# ============================================================================

.DEFAULT_GOAL := help
