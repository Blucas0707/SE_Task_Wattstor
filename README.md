
## Getting Started

### 1. Prerequisites

- [Docker](https://www.docker.com/products/docker-desktop)
- [Python 3.11+](https://www.python.org/downloads/)

### 2. Clone the Repository

```bash
git clone https://github.com/Blucas0707/wattstor-energy-system.git
cd wattstor-energy-system
```

### 3. Configure Environment Variables

Copy `.env.example` to `.env` and adjust as needed:

```bash
cp .env.example .env
```

**Key variables:**
- `DATABASE_URL` (for main app, e.g. `postgresql://postgres:postgres@db:5432/wattstor`)
- `TEST_DATABASE_URL` (for tests, e.g. `postgresql://postgres:postgres@localhost:5433/test_db`)

### 4. Start Services with Docker Compose

```bash
docker-compose up -d
```

- **web**: FastAPI app (http://localhost:8000)
- **db**: Main PostgreSQL database (port 5432)
- **test_db**: Isolated test database (port 5433)
- **pgadmin**: Database admin UI (http://localhost:5050, default: admin@admin.com / admin)

### 5. Initialize Mock Data

Mock data is automatically initialized on app startup (see `app/mock_data.py`).

---

## Running Tests

Tests use a separate PostgreSQL database (`test_db`) to avoid polluting production data.

**Run tests:**

```bash
TEST_DATABASE_URL=postgresql://postgres:postgres@localhost:5433/test_db pytest
```

Or use the provided Makefile:

```bash
make test
```

---

## Good Practices

- **Never run tests against the production database.**
- **Always use environment variables for sensitive data.**
- **Keep your dependencies up to date.**
- **Write and maintain tests for all critical features.**

---

## Troubleshooting

- **Database connection errors:**
  Ensure `test_db` is running and accessible at `localhost:5433`.
- **DetachedInstanceError:**
  Convert ORM objects to Pydantic schemas before closing the session.
- **Permission/volume issues:**
  Try restarting Docker or resetting volumes.

---

## Further Reading

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

---

## License

MIT License
