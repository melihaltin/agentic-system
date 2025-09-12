---
applyTo: "backend/**/*.py"
---

You are an expert in Python, FastAPI, and scalable API development.

## Core Principles

- Write concise, technical responses with accurate Python examples
- Use functional programming; prefer functions over classes except for models
- Favor composition over inheritance
- Use descriptive variable names with auxiliary verbs (e.g., `is_active`, `has_permission`)
- Use lowercase with underscores for files/directories (e.g., `routers/user_routes.py`)
- Follow the Receive an Object, Return an Object (RORO) pattern
- Prioritize type safety and runtime validation

## Python/FastAPI Standards

### Function Definitions

- Use `def` for pure/sync functions, `async def` for I/O operations
- Always include type hints for parameters and return values
- Use Pydantic models for request/response validation

### File Structure

```
app/
├── main.py                 # FastAPI app setup
├── core/
│   ├── config.py          # Settings and configuration
│   ├── dependencies.py    # Common dependencies
│   └── security.py        # Auth utilities
├── routers/
│   └── user_routes.py     # Route definitions
├── services/
│   └── user_service.py    # Business logic
├── models/
│   └── user_models.py     # Pydantic models
└── utils/
    └── database.py        # DB utilities
```

### Error Handling

- Handle errors at function start with early returns
- Use guard clauses for preconditions
- Implement specific exception types
- Always log errors with context
- Return user-friendly error messages

Example:

```python
async def get_user(user_id: int) -> UserResponse:
    if user_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid user ID")

    user = await user_service.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse.from_orm(user)
```

## FastAPI Specific

### Feature Organization

Each feature should be self-contained with:

- **router.py**: FastAPI routes for the feature
- **service.py**: Business logic and data processing
- **models.py**: Pydantic request/response models
- **schemas.py**: Database models (SQLAlchemy)
- **dependencies.py**: Feature-specific dependencies
- **exceptions.py**: Feature-specific error handling

Example feature structure:

```python
# features/users/router.py
from fastapi import APIRouter, Depends
from .service import UserService
from .models import UserCreate, UserResponse
from .dependencies import get_user_service

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service)
) -> UserResponse:
    return await user_service.create_user(user_data)
```

### App Assembly

```python
# main.py
from fastapi import FastAPI
from features.users.router import router as users_router
from features.orders.router import router as orders_router

app = FastAPI()
app.include_router(users_router)
app.include_router(orders_router)
```

### Migration Setup (Alembic)

#### Alembic Configuration

```python
# alembic.ini
[alembic]
script_location = migrations
prepend_sys_path = .
version_path_separator = os
sqlalchemy.url = postgresql://user:password@localhost/dbname

[post_write_hooks]
hooks = black
black.type = console_scripts
black.entrypoint = black
```

```python
# migrations/env.py
import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
from core.config import settings

# Import all models for auto-generation
from features.users.schemas import User  # Import all schemas
from core.database import Base

config = context.config
config.set_main_option("sqlalchemy.url", settings.database_url_sync)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations():
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()

def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### App Setup with PostgreSQL

```python
# main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import engine, Base
from core.config import settings
from features.users.router import router as users_router
from features.orders.router import router as orders_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables if they don't exist
    if settings.environment == "development":
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    yield

    # Shutdown: Close database connections
    await engine.dispose()

app = FastAPI(
    title="My FastAPI App",
    description="FastAPI app with PostgreSQL",
    version="1.0.0",
    lifespan=lifespan
)

# Include routers
app.include_router(users_router, prefix="/api/v1")
app.include_router(orders_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "postgresql"}
```

### Dependencies

- Use dependency injection for shared resources
- Create reusable dependency functions
- Implement proper dependency scoping

### Middleware

```python
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    logger.info(f"{request.method} {request.url} - {duration:.2f}s")
    return response
```

## Performance & Security

### Async Operations

- Use async for all I/O operations (DB, HTTP calls, file operations)
- Implement connection pooling for databases
- Use caching for frequently accessed data

### Security

- Implement proper authentication and authorization
- Use OAuth2/JWT for token-based auth
- Validate all inputs with Pydantic
- Implement rate limiting
- Use HTTPS in production

### Database

- Use async database drivers (asyncpg, aiomysql)
- Implement proper connection management
- Use database migrations (Alembic)
- Optimize queries with indexes

## Testing

```python
import pytest
from fastapi.testclient import TestClient

@pytest.mark.asyncio
async def test_get_user():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/users/1")
        assert response.status_code == 200
```

## Dependencies

- **Core**: FastAPI, Pydantic v2, Python 3.11+
- **Database**: SQLAlchemy 2.0, asyncpg, alembic
- **Security**: python-jose[cryptography], passlib[bcrypt], python-multipart
- **Testing**: pytest, pytest-asyncio, httpx, pytest-postgresql
- **Monitoring**: structlog, prometheus-client
- **Development**: black, isort, mypy, pre-commit

## Key Conventions (Class-Based)

1. **Repository Pattern**: Each feature has a repository class inheriting from BaseRepository
2. **Service Layer**: Business logic encapsulated in service classes inheriting from BaseService
3. **Controller Pattern**: API endpoints handled by controller classes inheriting from BaseController
4. **Dependency Injection**: Use FastAPI's dependency system with provider classes
5. **Interface Segregation**: Define clear contracts with abstract base classes
6. **Single Responsibility**: Each class has one clear responsibility
7. **Type Safety**: Use generics and type hints extensively
8. **Error Handling**: Implement custom exception classes per feature
9. **Testing**: Unit test each layer independently with proper mocking
10. **Configuration**: Use nested Pydantic settings for organized config management

## Testing Strategy

```python
# tests/unit/test_user_service.py
import pytest
from unittest.mock import AsyncMock
from features.users.service import UserService
from features.users.models import UserCreate, UserResponse
from features.users.repository import UserRepository

class TestUserService:
    def setup_method(self):
        self.mock_repository = AsyncMock(spec=UserRepository)
        self.service = UserService(self.mock_repository)

    @pytest.mark.asyncio
    async def test_create_user_success(self):
        # Arrange
        user_data = UserCreate(email="test@test.com", username="testuser", password="password")
        self.mock_repository.get_by_email.return_value = None
        self.mock_repository.get_by_username.return_value = None
        self.mock_repository.create.return_value = Mock(id=1, email="test@test.com")

        # Act
        result = await self.service.create(user_data)

        # Assert
        assert isinstance(result, UserResponse)
        assert result.email == "test@test.com"
        self.mock_repository.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_user_email_exists(self):
        # Arrange
        user_data = UserCreate(email="test@test.com", username="testuser", password="password")
        self.mock_repository.get_by_email.return_value = Mock(id=1)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await self.service.create(user_data)
        assert exc_info.value.status_code == 400
```

Refer to FastAPI documentation and clean architecture principles for advanced patterns and best practices.
