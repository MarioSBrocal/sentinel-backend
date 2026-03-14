.PHONY: dev build down

dev:
	docker compose up

build:
	docker compose up --build

down:
	docker compose down