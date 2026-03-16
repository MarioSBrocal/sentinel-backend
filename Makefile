.PHONY: \
	up up-build down restart ps logs \
	up-core down-core up-app down-app \
	up-db down-db up-redis down-redis up-api down-api up-worker down-worker up-scheduler down-scheduler \
	up-services down-services

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