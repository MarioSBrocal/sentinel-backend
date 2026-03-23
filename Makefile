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
ifeq ($(strip $(SERVICES)),)
	$(error The 'SERVICES' parameter is required. Usage: make up-services SERVICES='db redis')
endif
	docker compose up -d $(SERVICES)

down-services:
ifeq ($(strip $(SERVICES)),)
	$(error The 'SERVICES' parameter is required. Usage: make down-services SERVICES='db redis')
endif
	docker compose stop $(SERVICES)

api-shell:
	docker compose exec api /bin/bash

db-shell:
	docker compose exec db psql -U postgres -d mydb

redis-shell:
	docker compose exec redis redis-cli

migrate-up:
	uv run alembic upgrade head

migrate-down:
	uv run alembic downgrade -1

migrate-create:
ifeq ($(strip $(msg)),)
	$(error The 'msg' parameter is required. Usage: make migrate-create msg='Add new table')
endif
	uv run alembic revision --autogenerate -m "$(msg)"