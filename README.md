# Sentinel Backend

![python badge] [![github badge][]][github] [![license badge][]][LICENSE]

[English](README.md) | [Español](README.es.md)

---

## Table of Contents

- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [Quickstart](#quickstart)
- [Local Development](#local-development)
- [Roadmap](#roadmap)
- [License](#license)

---

**Sentinel** is an open-source Uptime (availability) monitoring system, designed to be fast, lightweight, and highly scalable. Built on a modern asynchronous stack, it is intended for teams and companies that need to monitor the health of their services without complications.

---

<a id="key-features"></a>

## Key Features

* **High Performance:** Asynchronous core powered by FastAPI and SQLAlchemy 2.0.
* **Multi-Tenant (Organizations):** Native support for teams. Users can create organizations, invite members (Roles: Owner, Admin, Viewer), and share monitors.
* **Asynchronous Ping Engine:** Uses Taskiq and Redis to distribute URL checking load across multiple *workers* without blocking the main API.
* **Smart Aggregation:** Deferred data processing (Batch Processing) natively in PostgreSQL to calculate hourly latency and uptime averages without overloading the server.
* **Docker-Ready:** Full orchestration ready for development and production with a single command.

---

<a id="tech-stack"></a>

## Tech Stack

* **Language:** Python 3.14+ (Managed with [uv])
* **Web Framework:** FastAPI
* **Database:** PostgreSQL 16 (with `asyncpg` and Alembic for migrations)
* **Broker & Cache:** Redis 7
* **Task Queue & Scheduler:** Taskiq

---

<a id="quickstart"></a>

## Quickstart

The easiest way to run Sentinel is by using Docker Compose. The entire infrastructure (Database, Cache, API, Workers, and Scheduler) will start automatically.

### Prerequisites
* [Docker] and Docker Compose installed.
* Git.

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/MarioSBrocal/sentinel-backend.git
   cd sentinel-backend
   ```

2. **Configure environment variables:**
   Copy the example file and configure it (default values work for local development with Docker):
   ```bash
   cp .env.example .env
   ```

3. **Start the infrastructure:**
   Run the following command to build images and start all services:
   ```bash
   make up-build
   # Or if you don't have make: docker compose up --build
   ```

4. **Apply database migrations:**
   In another terminal, while containers are running, execute:
   ```bash
   make migrate-up
   # Or equivalent: uv run alembic upgrade head
   ```

Done! The API will be available at `http://localhost:8000`.
You can explore the interactive documentation (Swagger) at `http://localhost:8000/docs`.

---

<a id="local-development"></a>

## Local Development

If you want to contribute or modify the code, we use `uv` for ultra-fast dependency management.

1. Install dependencies and create the virtual environment:
   ```bash
   uv sync
   ```
2. To start the development environment with *hot-reload* enabled:
   ```bash
   make up
   # Or equivalent: docker compose up
   ```
3. To create a new database migration after modifying a model:
   ```bash
   make migrate-create msg="Name of your change"
   # Or equivalent: uv run alembic revision --autogenerate -m "msg"
   ```

---

<a id="roadmap"></a>

## Roadmap (Coming Soon)

- [ ] Rate Limiting (SlowAPI) implementation for endpoint protection.
- [ ] API Key authentication for CI/CD integrations and scripts.
- [ ] Alert Channels system (Email, Slack, Discord, Webhooks).
- [ ] Graphical Interface (Frontend).

---

<a id="license"></a>

## License

This project is licensed under the MIT License - see the [LICENSE] file for more details.


[Docker]: https://docs.docker.com/get-docker/
[github]: https://github.com/MarioSBrocal
[github badge]: https://img.shields.io/badge/github-MarioSBrocal-a19d2b.svg?style=for-the-badge&logo=github
[LICENSE]: https://github.com/MarioSBrocal/sentinel-backend/blob/main/LICENSE
[license badge]: https://img.shields.io/badge/license-MIT-blue.svg?style=for-the-badge&logo=pastebin
[python badge]: https://img.shields.io/badge/python-3.14+-4584b6.svg?style=for-the-badge&logo=python
[uv]: https://github.com/astral-sh/uv