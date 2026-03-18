# Sentinel Backend

![python badge] [![github badge][]][github] [![license badge][]][LICENSE]

[English](README.md) | [Español](README.es.md)

---

## Índice

- [Características Principales](#caracteristicas-principales)
- [Stack Tecnológico](#stack-tecnologico)
- [Inicio Rápido (Quickstart)](#inicio-rapido-quickstart)
- [Desarrollo Local](#desarrollo-local)
- [Roadmap](#hoja-de-ruta)
- [Licencia](#licencia)

---

**Sentinel** es un sistema de monitorización de Uptime (disponibilidad) de código abierto, diseñado para ser rápido, ligero y altamente escalable. Construido sobre un stack moderno y asíncrono, está pensado para equipos y empresas que necesitan controlar la salud de sus servicios sin complicaciones.

---

<a id="caracteristicas-principales"></a>

## Características Principales

* **Alto Rendimiento:** Core asíncrono impulsado por FastAPI y SQLAlchemy 2.0.
* **Multi-Tenant (Organizaciones):** Soporte nativo para equipos. Los usuarios pueden crear organizaciones, invitar a miembros (Roles: Owner, Admin, Viewer) y compartir monitores.
* **Motor de Pings Asíncrono:** Utiliza Taskiq y Redis para distribuir la carga de comprobación de URLs en múltiples *workers* sin bloquear la API principal.
* **Agregación Inteligente:** Procesamiento de datos en diferido (Batch Processing) nativo en PostgreSQL para calcular promedios horarios de latencia y uptime sin sobrecargar el servidor.
* **Docker-Ready:** Orquestación completa lista para desarrollo y producción con un solo comando.

---

<a id="stack-tecnologico"></a>

## Stack Tecnológico

* **Lenguaje:** Python 3.14+ (Gestionado con [uv])
* **Framework Web:** FastAPI
* **Base de Datos:** PostgreSQL 16 (con `asyncpg` y Alembic para migraciones)
* **Broker & Caché:** Redis 7
* **Task Queue & Scheduler:** Taskiq

---

<a id="inicio-rapido-quickstart"></a>

## Inicio Rápido (Quickstart)

La forma más fácil de levantar Sentinel es utilizando Docker Compose. Toda la infraestructura (Base de datos, Caché, API, Workers y Scheduler) se levantará automáticamente.

### Prerrequisitos
* [Docker] y Docker Compose instalados.
* Git.

### Instalación

1. **Clona el repositorio:**
   ```bash
   git clone https://github.com/MarioSBrocal/sentinel-backend.git
   cd sentinel-backend
   ```

2. **Configura las variables de entorno:**
   Copia el archivo de ejemplo y configúralo (los valores por defecto funcionan para desarrollo local con Docker):
   ```bash
   cp .env.example .env
   ```

3. **Levanta la infraestructura:**
   Ejecuta el siguiente comando para construir las imágenes y levantar todos los servicios:
   ```bash
   make up-build
   # O si no tienes make: docker compose up --build
   ```

4. **Aplica las migraciones de la base de datos:**
   En otra terminal, mientras los contenedores están corriendo, ejecuta:
   ```bash
   make migrate-up
   # O equivalente: docker compose exec api alembic upgrade head
   ```

¡Listo! La API estará disponible en `http://localhost:8000`.
Puedes explorar la documentación interactiva (Swagger) en `http://localhost:8000/docs`.

---

<a id="desarrollo-local"></a>

## Desarrollo Local

Si deseas contribuir o modificar el código, utilizamos `uv` para una gestión ultrarrápida de dependencias.

1. Instala dependencias y crea el entorno virtual:
   ```bash
   uv sync
   ```
2. Para levantar el entorno de desarrollo con *hot-reload* activado:
   ```bash
   make up
   # O equivalente: docker compose up
   ```
3. Para crear una nueva migración de base de datos después de modificar un modelo:
   ```bash
   make migrate-create msg="Nombre de tu cambio"
   # O equivalente: docker compose exec api alembic revision --autogenerate -m "msg"
   ```

---

<a id="hoja-de-ruta"></a>

## Hoja de Ruta

- [ ] Implementación de Rate Limiting (SlowAPI) para protección de endpoints.
- [ ] Autenticación mediante API Keys para integraciones CI/CD y scripts.
- [ ] Sistema de Canales de Alerta (Email, Slack, Discord, Webhooks).
- [ ] Interfaz gráfica (Frontend).

---

<a id="licencia"></a>

## Licencia

Este proyecto está bajo la Licencia MIT - mira el archivo [LICENSE](LICENSE) para más detalles.


[Docker]: https://docs.docker.com/get-docker/
[github]: https://github.com/MarioSBrocal
[github badge]: https://img.shields.io/badge/github-MarioSBrocal-a19d2b.svg?style=for-the-badge&logo=github
[LICENSE]: https://github.com/MarioSBrocal/sentinel-backend/blob/main/LICENSE
[license badge]: https://img.shields.io/badge/license-MIT-blue.svg?style=for-the-badge&logo=pastebin
[python badge]: https://img.shields.io/badge/python-3.14+-4584b6.svg?style=for-the-badge&logo=python
[uv]: https://github.com/astral-sh/uv