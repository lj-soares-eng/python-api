# Python Users REST API

A scalable RESTful Web API for managing user data, built with Python and Django.

This project demonstrates core engineering practices layered architecture, REST conventions, validation, and clean persistence boundaries applied in the Python/Django ecosystem.

## Features

- RESTful CRUD operations for a `users` resource
- Data persistence with Django ORM and MySQL
- BCrypt password hashing (plain-text passwords never returned)
- Automatic `created_at` timestamp on user creation
- Role-based user model (`USER`, `ADMIN`)
- OpenAPI documentation via drf-spectacular
- Docker Compose for one-command local setup

## Tech Stack

| Layer | Technology |
|-------|------------|
| Language | Python 3.12+ |
| Framework | Django 6 + Django REST Framework |
| Persistence | Django ORM + migrations |
| Database | MySQL 8.4 |
| API Docs | drf-spectacular (OpenAPI 3) |
| Containers | Docker Compose |

## Data Model

Table: `users`

| Column | Type | Notes |
|--------|------|-------|
| `id` | INT, PK, AI | Auto-increment primary key |
| `name` | VARCHAR(255) | User display name |
| `email` | VARCHAR(255) | Unique email |
| `password` | VARCHAR(128) | BCrypt hash; exposed as `passwordHash` in JSON |
| `role` | VARCHAR(10) | `USER` or `ADMIN` |
| `created_at` | TIMESTAMP | Set at creation time |

## Prerequisites

- Docker installed and running (`docker info` succeeds)
- Git

Optional (for running without Docker):

- Python 3.12+
- MySQL 8+ (local instance or Docker for DB only)

## Getting Started

### 1. Clone the repository

```bash
git clone <repo-url> python-api
cd python-api
```

### 2. Configure environment

```bash
cp .env.example .env
```

Default values work for local Docker development. Edit `.env` to change the MySQL
password or Django secret key.

### 3. Start the stack

```bash
docker compose up --build
```

This will:

1. Start MySQL 8.4 and create the `PythonApi` database
2. Build the Django API image
3. Wait for MySQL to become healthy
4. Run Django migrations (creates the `users` table)
5. Start the API on port **8080**

The API is available at **http://localhost:8080**.

> **Note:** MySQL runs inside Docker and is not exposed on the host by default.
> The API connects to it via the internal `db` service name.

### 4. Stop the stack

```bash
docker compose down        # stop containers (data persists in volume)
docker compose down -v     # stop and remove database volume
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/users` | List all users |
| GET | `/api/users/{id}` | Get user by ID |
| POST | `/api/users` | Create a new user |
| PUT | `/api/users/{id}` | Update a user |
| DELETE | `/api/users/{id}` | Delete a user |

## Examples

### Create user

```bash
curl -X POST http://localhost:8080/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Doe",
    "email": "jane@example.com",
    "password": "your-secure-password",
    "role": "USER"
  }'
```

Example response:

```json
{
  "id": 1,
  "name": "Jane Doe",
  "email": "jane@example.com",
  "passwordHash": "$2b$12$...",
  "role": "USER",
  "created_at": "2026-07-03T18:03:47.142723Z"
}
```

### List users

```bash
curl http://localhost:8080/api/users
```

### Get user by ID

```bash
curl http://localhost:8080/api/users/1
```

### Update user

`password` is optional on update; omit it to keep the existing hash.

```bash
curl -X PUT http://localhost:8080/api/users/1 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Smith",
    "email": "jane.smith@example.com",
    "password": "new-password",
    "role": "ADMIN"
  }'
```

### Delete user

```bash
curl -X DELETE http://localhost:8080/api/users/1
```

Returns HTTP 204 with no body.

## API Documentation

- Swagger UI: http://localhost:8080/api/docs/
- OpenAPI schema: http://localhost:8080/api/schema/
- Design contract: `specs/001-users-api-docker/contracts/users-api.openapi.yaml`

## Configuration

Settings are driven by environment variables (see `.env.example`).

| Variable | Default (Docker) | Description |
|----------|------------------|-------------|
| `DB_HOST` | `db` | MySQL hostname |
| `DB_PORT` | `3306` | MySQL port |
| `DB_NAME` | `PythonApi` | Database name |
| `DB_USERNAME` | `root` | MySQL user |
| `DB_PASSWORD` | `secret` | MySQL password |
| `DJANGO_SECRET_KEY` | `dev-only-change-me` | Django secret key |
| `DJANGO_DEBUG` | `true` | Debug mode |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1,api` | Comma-separated allowed hosts |

For production, set `DJANGO_DEBUG=false`, use a strong `DJANGO_SECRET_KEY`, and
deploy behind HTTPS.

## Running without Docker

Requires a local MySQL instance with the database created:

```sql
CREATE DATABASE IF NOT EXISTS PythonApi;
```

Then:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

export DB_HOST=localhost
export DB_PASSWORD=your_password
export DB_NAME=PythonApi

python manage.py migrate
python manage.py runserver 8080
```

## Testing

Tests use **pytest** with an in-memory SQLite database (`core/settings_test.py`) — no MySQL or Docker required.

```bash
source venv/bin/activate
pip install -r requirements.txt
pytest
```

With coverage:

```bash
pytest --cov=users --cov-report=term-missing
```

Test suites:

| File | Covers |
|------|--------|
| `users/tests/test_services.py` | Business logic, password hashing, duplicate email |
| `users/tests/test_serializers.py` | Input validation, response shape |
| `users/tests/test_api.py` | Full CRUD HTTP endpoints |

## Project Structure

```text
python-api/
├── core/                        # Django project (settings, root URLs)
│   ├── settings.py
│   └── urls.py
├── users/                       # Users app
│   ├── models.py                # User entity (ORM)
│   ├── serializers.py           # Request/response DTOs
│   ├── services.py              # Business logic, password hashing
│   ├── views.py                 # REST controllers (ViewSet)
│   ├── urls.py
│   ├── migrations/
│   └── tests/
├── specs/001-users-api-docker/  # Spec Kit feature artifacts
├── Dockerfile
├── docker-compose.yml
├── entrypoint.sh                # Wait for DB, migrate, start server
├── requirements.txt
├── manage.py
└── .env.example
```

Layered architecture:

| Layer | Python | Java (reference) |
|-------|--------|------------------|
| HTTP | `views.py` | `controller/` |
| Business logic | `services.py` | `service/` |
| Data access | `models.py` | `repository/` + JPA entity |
| DTOs | `serializers.py` | `dto/` |

## Security Notes

- Passwords are hashed with BCrypt before being saved to the database
- `GET /api/users` and `GET /api/users/{id}` may include `passwordHash` in responses (demo/debug)
- `POST` and `PUT` success responses never echo plain-text `password`
- The `password` field is only accepted in POST/PUT request bodies
- Input validation is enforced on all write operations
- No authentication on endpoints in v1 (matches Java demo)
- Use HTTPS in production

## License

MIT License.

**Author:** Lucas Soares
