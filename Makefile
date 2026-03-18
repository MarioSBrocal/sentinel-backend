.PHONY: \
    up up-build down restart ps logs \
    up-core down-core up-app down-app \
    up-db down-db up-redis down-redis up-api down-api up-worker down-worker up-scheduler down-scheduler \
    up-services down-services \
    migrate-up migrate-down migrate-create \
    api-shell db-shell redis-shell test lint

test:
	uv run pytest tests/

lint:
	uvx ruff check . --fix
	uvx ruff format . 

up:
	docker compose up

up-detached:
	docker compose up -d

up-build:
	docker compose up --build

down:
	docker compose down

restart:
	docker compose restart

ps:
	docker compose ps

logs:
	docker compose logs -f

stats:
	docker compose stats

up-core:
	docker compose up -d db redis

down-core:
	docker compose stop db redis

up-app:
	docker compose up -d api worker scheduler

down-app:
	docker compose stop api worker scheduler

up-db:
	docker compose up -d db

down-db:
	docker compose stop db

up-redis:
	docker compose up -d redis

down-redis:
	docker compose stop redis

up-api:
	docker compose up -d api

down-api:
	docker compose stop api

up-worker:
	docker compose up -d worker

down-worker:
	docker compose stop worker

up-scheduler:
	docker compose up -d scheduler

down-scheduler:
	docker compose stop scheduler

up-services:
	@if [ -z "$(SERVICES)" ]; then echo "Usage: make up-services SERVICES='db redis'"; exit 1; fi
	docker compose up -d $(SERVICES)

down-services:
	@if [ -z "$(SERVICES)" ]; then echo "Usage: make down-services SERVICES='db redis'"; exit 1; fi
	docker compose stop $(SERVICES)

api-shell:
	docker compose exec api /bin/bash

db-shell:
	docker compose exec db psql -U postgres -d mydb

redis-shell:
	docker compose exec redis redis-cli

migrate-up:
	docker compose exec api alembic upgrade head

migrate-down:
	docker compose exec api alembic downgrade -1

migrate-create:
	@if [ -z "$(msg)" ]; then echo "Usage: make migrate-create msg='Add new table'"; exit 1; fi
	docker compose exec api alembic revision --autogenerate -m "$(msg)"