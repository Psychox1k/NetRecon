# 🔍NetScan v1: Automated Infrastructure Scanning System

## 🛠 Tech Stack

![Python](https://img.shields.io/badge/Python-3.13-blue?style=flat&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=flat&logo=postgresql)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-red?style=flat)
![Celery](https://img.shields.io/badge/Celery-Task_Queue-orange?style=flat&logo=celery)
![Redis](https://img.shields.io/badge/Redis-Broker-red?style=flat&logo=redis)
![Docker](https://img.shields.io/badge/Docker-Container-blue?style=flat&logo=docker)
![Pytest](https://img.shields.io/badge/Pytest-Testing-yellow?style=flat&logo=pytest)
![Telegram](https://img.shields.io/badge/Telegram_Bot-aiogram-2CA5E0?style=flat&logo=telegram)
![Swagger](https://img.shields.io/badge/-Swagger-%23Clojure?style=flat&logo=swagger&logoColor=white&color=85EA2D)

## 📖 About the Project

**NetScan** is a comprehensive RESTful API and Telegram Bot designed for automated infrastructure scanning and asset management. 

Built with **FastAPI** for high performance, this project allows security teams and administrators to track targets, manage domains and IP addresses, and perform asynchronous scans (port discovery, SSL certificate parsing) using Celery and Redis.

## ✨ Key Features

* **🎯 Asset Management:** Complete CRUD operations for Targets, Domains, and IP addresses with cascading database relations.
* **🔍 Automated Scanning Engine:**
    * Port discovery and banner grabbing.
    * Automated SSL/TLS certificate parsing (Issuer, Expiration dates, etc.).
* **🤖 Telegram Bot Integration (`aiogram`):**
    * Manage scans and retrieve target information directly from Telegram.
    * Asynchronous polling tightly integrated with the FastAPI lifespan.
* **⚡ Background Tasks (Celery + Redis):**
    * Heavy scanning operations are offloaded to background workers to ensure the API remains blazing fast.
* **🛡️ Bulletproof Data Validation:** Strict Pydantic schemas and database constraints to prevent data duplication.
* **🐳 Fully Dockerized:** Ready for deployment with isolated containers for the Web API, DB, Redis, and Celery Worker.

---

## 📂 Project Structure

A quick overview of the core application structure:

```plaintext
.
├── .env
├── .env_sample
├── .gitignore
├── Dockerfile
├── README.md
├── alembic.ini
├── app/
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   ├── dependencies.py
│   │   └── settings.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── domain.py
│   │   │   ├── ip_address.py
│   │   │   ├── port.py
│   │   │   ├── ssl_cert.py
│   │   │   └── target.py
│   │   └── session_postgresql.py
│   ├── main.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── api.py
│   │   ├── domain.py
│   │   ├── ip.py
│   │   ├── port.py
│   │   ├── ssl_certificate.py
│   │   └── target.py
│   ├── scanner/
│   │   ├── __init__.py
│   │   ├── banner_port.py
│   │   ├── core.py
│   │   ├── dns_resolver.py
│   │   ├── port_scanner.py
│   │   └── ssl_parser.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── domain.py
│   │   ├── ip.py
│   │   ├── port.py
│   │   ├── ssl_certificate.py
│   │   └── target.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── scanner_service.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── api/
│   │   │   ├── test_certificates.py
│   │   │   ├── test_domains.py
│   │   │   ├── test_ips.py
│   │   │   ├── test_port.py
│   │   │   └── test_target.py
│   │   ├── bot/
│   │   │   └── test_validators.py
│   │   ├── conftest.py
│   │   ├── models/
│   │   │   ├── test_domain.py
│   │   │   ├── test_ips.py
│   │   │   ├── test_queries.py
│   │   │   ├── test_relations.py
│   │   │   ├── test_services.py
│   │   │   └── test_target.py
│   │   └── test_schemas.py
│   ├── tg_bot/
│   │   ├── __init__.py
│   │   ├── handlers/
│   │   │   ├── base.py
│   │   │   └── targets.py
│   │   ├── keyboards/
│   │   │   ├── inline.py
│   │   │   └── reply.py
│   │   ├── main.py
│   │   ├── middlewares/
│   │   │   └── __init__.py
│   │   ├── states.py
│   │   └── utils/
│   │       ├── formatters.py
│   │       └── validators.py
│   └── worker/
│       ├── __init__.py
│       ├── celery_app.py
│       └── tasks.py
├── celerybeat-schedule
├── docker-compose.yml
├── migrations/
│   ├── README
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── f7c91d8e156f_init_db.py
├── pytest.ini
├── requirements.txt
└── test_main.http
21 directories, 83 files
```


## 🚀 Getting Started
### Prerequisites
- Docker & Docker Compose
- Git

### 1. Clone the repository

```bash
git clone [https://github.com/Psychox1k/NetRecon.git](https://github.com/Psychox1k/NetRecon.git)
cd NetRecon
```

### 2. Environment Configuration
Create a .env file in the project root directory and add the following variables:

### Code snippet
### Database Settings
```
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=NetScan_db
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

### Redis & Celery
```
REDIS_URL=redis://redis:6379/0
```
### Telegram Bot
```
BOT_TOKEN=your_telegram_bot_token
BOT_MODE=polling
```

### Application
LOG_LEVEL=INFO
### 3. Build and Run (Docker)
Start the application suite (FastAPI, PostgreSQL, Redis, Celery) with Docker Compose:

```Bash
docker compose up -d --build
```
### 4. Apply Database Migrations
Initialize the database schema using Alembic:

```Bash
docker compose exec web alembic upgrade head
```
(Note: Replace web with the name of your FastAPI service in docker-compose.yml if different).

### 📚 API Documentation
The project includes auto-generated interactive API documentation powered by OpenAPI (Swagger). Once the server is running, access it here:

#### Swagger UI: http://127.0.0.1:8000/docs

#### ReDoc: http://127.0.0.1:8000/redoc

## 🧪 Testing
The project is covered by a comprehensive test suite using Pytest. Tests run in an isolated in-memory SQLite database to ensure the production data remains untouched.

To run the tests locally or inside the Docker container:

```Bash
docker compose exec web pytest -v
```

## 👨‍💻 Developed By
- [Kyrylo Zhyhariev](https://github.com/Psychox1k)