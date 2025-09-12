# Team AI Backend

A modern FastAPI backend application with PostgreSQL database, featuring user authentication, JWT tokens, and structured logging.

## Features

- **FastAPI** framework with async/await support
- **PostgreSQL** database with async SQLAlchemy 2.0
- **JWT Authentication** with secure password hashing
- **Alembic** database migrations
- **Structured logging** with structlog
- **CORS** configuration for frontend integration
- **Docker** containerization support
- **Comprehensive error handling** and validation
- **User management** with role-based permissions
- **API documentation** with automatic OpenAPI/Swagger

## Project Structure

```
backend/
├── main.py                     # FastAPI application entry point
├── requirements.txt            # Python dependencies
├── alembic.ini                # Alembic migration configuration
├── Dockerfile                 # Docker container configuration
├── docker-compose.yml         # Development environment
├── .env.example              # Environment variables template
├── core/                     # Core application components
│   ├── config.py            # Application settings
│   ├── database.py          # Database connection and base models
│   ├── dependencies.py      # Common FastAPI dependencies
│   └── security.py          # Authentication utilities
├── features/                 # Feature-based organization
│   ├── auth/                # Authentication feature
│   │   ├── models.py        # Pydantic models for auth
│   │   ├── service.py       # Business logic
│   │   ├── router.py        # API endpoints
│   │   └── dependencies.py  # Auth-specific dependencies
│   └── users/               # User management feature
│       ├── models.py        # Pydantic models
│       ├── schemas.py       # Database models
│       ├── repository.py    # Database operations
│       ├── service.py       # Business logic
│       ├── router.py        # API endpoints
│       └── dependencies.py  # User-specific dependencies
└── migrations/              # Database migration files
    ├── env.py              # Alembic environment
    └── script.py.mako      # Migration template
```

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis (optional, for caching)

### Option 1: Docker Development (Recommended)

1. Clone the repository and navigate to the backend directory:

```bash
cd backend
```

2. Copy the environment template:

```bash
cp .env.example .env
```

3. Start the development environment:

```bash
docker-compose up --build
```

The API will be available at `http://localhost:8000`

### Option 2: Local Development

1. Install Python dependencies:

```bash
pip install -r requirements.txt
```

2. Set up PostgreSQL database and create a `.env` file:

```bash
cp .env.example .env
# Edit .env with your database credentials
```

3. Run database migrations:

```bash
alembic upgrade head
```

4. Start the development server:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Environment Configuration

Create a `.env` file based on `.env.example`:

```env
# Environment Configuration
ENVIRONMENT=development
DEBUG=true

# Security
SECRET_KEY=your-secret-key-here-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database Configuration
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
POSTGRES_DB=team_ai_db

# CORS Configuration
ALLOWED_HOSTS=http://localhost:3000,http://localhost:8000
```

## Database Migrations

### Create a new migration:

```bash
alembic revision --autogenerate -m "Description of changes"
```

### Apply migrations:

```bash
alembic upgrade head
```

### Rollback migrations:

```bash
alembic downgrade -1
```

## API Documentation

When running in development mode, API documentation is available at:

- **Swagger UI**: `http://localhost:8000/api/docs`
- **ReDoc**: `http://localhost:8000/api/redoc`

## API Endpoints

### Authentication

- `POST /api/v1/auth/register` - Register a new user
- `POST /api/v1/auth/login` - Login with email/password
- `POST /api/v1/auth/logout` - Logout (client-side token removal)

### Users

- `GET /api/v1/users/` - Get paginated list of users
- `POST /api/v1/users/` - Create a new user (admin only)
- `GET /api/v1/users/me` - Get current user profile
- `PUT /api/v1/users/me` - Update current user profile
- `POST /api/v1/users/me/change-password` - Change password
- `DELETE /api/v1/users/me` - Deactivate account
- `GET /api/v1/users/{user_id}` - Get user by ID
- `GET /api/v1/users/username/{username}` - Get public user by username
- `PUT /api/v1/users/{user_id}` - Update user (admin or own profile)
- `DELETE /api/v1/users/{user_id}` - Deactivate user (admin or own)

### Health Check

- `GET /health` - Application health status

## Testing

Run the test suite:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=.
```

## Development Guidelines

### Code Style

- Follow PEP 8 conventions
- Use type hints for all function parameters and returns
- Use descriptive variable names with auxiliary verbs
- Prefer functions over classes except for models

### Architecture

- Follow the Repository pattern for database operations
- Use Service layer for business logic
- Implement proper error handling with FastAPI HTTPException
- Use dependency injection for shared resources

### Security

- Always hash passwords using bcrypt
- Validate all inputs with Pydantic models
- Use JWT tokens for authentication
- Implement proper CORS configuration
- Log security events

## Production Deployment

1. Set `ENVIRONMENT=production` in your environment
2. Use a strong `SECRET_KEY`
3. Configure proper database credentials
4. Set up SSL/HTTPS
5. Configure proper logging
6. Set up monitoring and health checks

## Contributing

1. Follow the existing code structure and patterns
2. Add tests for new functionality
3. Update documentation when adding new endpoints
4. Follow the commit message conventions
5. Ensure all tests pass before submitting

## License

This project is licensed under the MIT License.
