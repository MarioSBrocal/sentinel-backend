.PHONY: api worker scheduler services

services:
	docker compose up -d

api:
	uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

worker:
	uv run taskiq worker app.worker.broker:broker app.worker.tasks

scheduler:
	uv run taskiq scheduler app.worker.scheduler:scheduler