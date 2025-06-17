# Wattstor API

A FastAPI-based API for managing energy monitoring devices and metrics.

## Features

- Site directory management
- Device CRUD operations
- Metric monitoring and history
- Subscription system for metrics
- User authentication and authorization
- Role-based access control

## Technology Stack

- Python 3.10+
- FastAPI
- SQLite
- SQLAlchemy
- Pydantic
- JWT Authentication
- Docker & Docker Composehttps://github.com/Blucas0707/SE_Task_Wattstor.git

## Quick Start with Docker

1. Clone the repository:
```bash
git clone https://github.com/Blucas0707/SE_Task_Wattstor.git
```

2. Start the services:
```bash
docker compose up -d
```

This will start:
- API server at http://localhost:8000
- PostgreSQL database at localhost:5432
- pgAdmin at http://localhost:5050

3. Access the services:
- API documentation: http://localhost:8000/docs
- pgAdmin: http://localhost:5050 (email: admin@admin.com, password: admin)

4. Stop the services:
```bash
docker compose down
```

## Development Environment Setup

1. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/wattstor"
export SECRET_KEY="your-secret-key-here"
export ALGORITHM="HS256"
export ACCESS_TOKEN_EXPIRE_MINUTES=30
```

4. Initialize the database:
```bash
python -m app.core.init_db
```

5. Run the development server:
```bash
uvicorn app.main:app --reload
```

## API Documentation

The API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

Run tests with pytest:
```bash
# Run all tests
pytest

# Run tests with coverage report
pytest --cov=app tests/

# Run specific test file
pytest tests/test_device.py
```

## Project Structure

```
wattstor-api/
├── app/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── config.py
│   │   ├── database.py
│   │   └── init_db.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── device.py
│   │   ├── metric.py
│   │   ├── site.py
│   │   ├── subscription.py
│   │   └── user.py
│   │   └── user_site.py
│   ├── routers/
│   │   ├── __init__.py
│   │   └── auth_router.py
│   │   ├── device_router.py
│   │   ├── metric_router.py
│   │   ├── site_router.py
│   │   ├── subscription_router.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── device.py
│   │   ├── metric.py
│   │   ├── site.py
│   │   ├── subscription.py
│   │   └── user.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── device_service.py
│   │   ├── metric_service.py
│   │   ├── site_service.py
│   │   ├── subscription_service.py
│   │   └── user_service.py
│   └── main.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_device.py
│   ├── test_metric_history.py
│   └── test_subscription.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Design Decisions

1. **Database Choice**: PostgreSQL is used for its robust support of JSON data types and time-series data.

2. **Authentication**: JWT-based authentication is implemented for secure API access.

3. **API Structure**: The API follows RESTful principles with clear separation of concerns:
   - Models: Database models
   - Schemas: Pydantic models for request/response validation
   - Services: Business logic
   - Routers: API endpoints

4. **Testing**: Comprehensive test suite using pytest with fixtures and mocks.

## API Usage Examples

### Authentication

```bash
# Login
curl -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin"

# Use token
curl http://localhost:8000/sites \
  -H "Authorization: Bearer <token>"
```

### Device Management

```bash
# Create device
curl -X POST http://localhost:8000/devices \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "Solar Panel 1", "site_id": 1}'

# Get device metrics
curl http://localhost:8000/devices/1/metrics \
  -H "Authorization: Bearer <token>"
```

### Subscription Management

```bash
# Create subscription
curl -X POST http://localhost:8000/subscriptions \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "Solar Metrics", "metric_ids": [1, 2, 3]}'

# Get subscription time series
curl "http://localhost:8000/subscriptions/1/time-series?start_time=2024-01-01T00:00:00Z&end_time=2024-01-02T00:00:00Z" \
  -H "Authorization: Bearer <token>"
```

## Deployment

### Docker Deployment

1. Build and push the Docker image:
```bash
docker build -t wattstor-api .
docker tag wattstor-api your-registry/wattstor-api:latest
docker push your-registry/wattstor-api:latest
```

2. Deploy using docker-compose:
```bash
docker compose up -d
```

### Production Considerations

1. Use environment variables for sensitive data
2. Set up proper logging
3. Configure SSL/TLS
4. Set up database backups
5. Monitor application health

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
