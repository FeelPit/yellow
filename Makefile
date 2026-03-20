.PHONY: up down api-test web-test test lint install-api install-web install

# Start all services
up:
	cd infra && docker-compose up -d

# Stop all services
down:
	cd infra && docker-compose down

# Run backend tests
api-test:
	cd apps/api && pytest -v

# Run frontend tests
web-test:
	cd apps/web && npm test

# Run all tests
test: api-test web-test

# Lint (placeholder for future linting setup)
lint:
	@echo "Linting not configured yet"

# Install backend dependencies
install-api:
	cd apps/api && pip install -r requirements.txt

# Install frontend dependencies
install-web:
	cd apps/web && npm install

# Install all dependencies
install: install-api install-web

# Run migrations
migrate:
	cd apps/api && alembic upgrade head

# Create new migration
migration:
	cd apps/api && alembic revision --autogenerate -m "$(message)"

# View logs
logs:
	cd infra && docker-compose logs -f

# Restart services
restart: down up

# Clean up everything
clean: down
	cd infra && docker-compose down -v
	rm -rf apps/api/__pycache__
	rm -rf apps/api/.pytest_cache
	rm -rf apps/web/node_modules
	rm -rf apps/web/.next
