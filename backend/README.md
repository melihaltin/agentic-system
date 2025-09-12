# Team AI Backend

A modern FastAPI backend application with PostgreSQL database, featuring user authentication, JWT tokens, and structured logging.

## Features

- **FastAPI** framework with async/await support
- **PostgreSQL** database with async SQLAlchemy 2.0
- **Supabase Integration** with authentication, database, and storage
- **Hybrid Authentication** - Choose between custom JWT or Supabase Auth
- **JWT Authentication** with secure password hashing
- **Alembic** database migrations
- **Structured logging** with structlog
- **CORS** configuration for frontend integration
- **Docker** containerization support
- **Comprehensive error handling** and validation
- **User management** with role-based permissions
- **File storage** with Supabase Storage
- **Real-time capabilities** via Supabase
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
- PostgreSQL 15+ (or use local Supabase)
- Docker and Docker Compose
- Node.js (for Supabase CLI)
- Redis (optional, for caching)

### Platform-Specific Guides

- **🐧 macOS/Linux**: Follow the instructions below
- **🪟 Windows**: See [WINDOWS_SETUP.md](WINDOWS_SETUP.md) for detailed Windows installation guide

### Option 0: Local Supabase Development (Recommended for Testing)

For development without cloud dependencies:

1. **Setup local Supabase environment:**

```bash
cd backend
chmod +x scripts/install-supabase-cli.sh dev.sh supabase-local.sh
./dev.sh supabase-local
```

2. **Access your services:**
   - FastAPI Backend: http://localhost:8000
   - Supabase Studio: http://localhost:54323
   - PostgreSQL: localhost:54322

📖 **Detailed guide**: See [LOCAL_DEVELOPMENT.md](LOCAL_DEVELOPMENT.md) for comprehensive local setup instructions.

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

# Supabase Configuration (optional)
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_KEY=your-service-role-key-here
USE_SUPABASE_AUTH=false  # Set to true to use Supabase Auth instead of custom JWT
```

## Supabase Setup (Optional)

### 1. Create a Supabase Project

1. Go to [supabase.com](https://supabase.com) and create a new project
2. Get your project URL and API keys from the project settings
3. Add the keys to your `.env` file

### 2. Set up the Database Schema

1. Go to the SQL Editor in your Supabase dashboard
2. Run the SQL script from `sql/supabase_setup.sql`
3. This will create the necessary tables, RLS policies, and functions

### 3. Configure Authentication Mode

Set `USE_SUPABASE_AUTH=true` in your `.env` file to use Supabase authentication, or keep it `false` to use the custom JWT implementation.

### 4. Supabase Features Available

- **Authentication**: User signup, login, logout with Supabase Auth
- **Database**: User profiles stored in Supabase PostgreSQL
- **Storage**: Avatar uploads to Supabase Storage
- **Real-time**: Real-time subscriptions (can be extended)
- **Row Level Security**: Automatic security policies```

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

### Authentication (Traditional)

- `POST /api/v1/auth/register` - Register a new user
- `POST /api/v1/auth/login` - Login with email/password
- `POST /api/v1/auth/logout` - Logout (client-side token removal)

### Authentication (Supabase)

- `POST /api/v1/auth/supabase/register` - Register with Supabase Auth
- `POST /api/v1/auth/supabase/login` - Login with Supabase Auth
- `POST /api/v1/auth/supabase/refresh` - Refresh Supabase token
- `POST /api/v1/auth/supabase/logout` - Logout from Supabase
- `GET /api/v1/auth/supabase/me` - Get current Supabase user
- `PUT /api/v1/auth/supabase/profile` - Update Supabase profile

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
