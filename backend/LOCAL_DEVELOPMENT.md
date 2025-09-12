# Local Development with Supabase

This guide explains how to set up and run the backend with local Supabase for development and testing without cloud dependencies.

## Prerequisites

- Docker and Docker Compose installed
- Node.js (for Supabase CLI)
- Python 3.11+

## Quick Start

### 1. Install Supabase CLI

```bash
# Run the installation script
chmod +x scripts/install-supabase-cli.sh
./scripts/install-supabase-cli.sh
```

### 2. Start Local Development Environment

```bash
# Full setup (installs dependencies, starts Supabase, runs migrations, starts server)
./dev.sh supabase-local

# Or step by step:
./supabase-local.sh full-start
./dev.sh dev-supabase
```

### 3. Access Services

- **FastAPI Backend**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Supabase Studio**: http://localhost:54323
- **PostgreSQL**: localhost:54322

## Available Commands

### Main Development Script (`./dev.sh`)

```bash
# Supabase specific commands
./dev.sh supabase-local    # Start local Supabase
./dev.sh supabase-stop     # Stop local Supabase
./dev.sh supabase-test     # Test local Supabase connection
./dev.sh dev-supabase      # Start server with local Supabase
```

### Supabase Local Management (`./supabase-local.sh`)

```bash
# Essential commands
./supabase-local.sh start           # Start Supabase services
./supabase-local.sh stop            # Stop all services
./supabase-local.sh status          # Check service status
./supabase-local.sh logs            # View logs

# Database operations
./supabase-local.sh reset           # Reset database
./supabase-local.sh migrate         # Run migrations
./supabase-local.sh seed            # Run seed data

# Development workflows
./supabase-local.sh full-start      # Complete setup
./supabase-local.sh restart         # Stop and start
./supabase-local.sh test            # Run connection tests
```

## Configuration

### Environment Variables

The system automatically uses local configuration when `ENVIRONMENT=local`:

```bash
# .env.local (automatically loaded)
SUPABASE_URL=http://localhost:54321
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here
DATABASE_URL=postgresql://postgres:postgres@localhost:54322/postgres
```

### Switching Between Backends

```bash
# Use local Supabase
export USE_SUPABASE=true
export ENVIRONMENT=local

# Use traditional PostgreSQL
export USE_SUPABASE=false
# or unset USE_SUPABASE
```

## Testing

### Run All Tests

```bash
# Test local Supabase connection and features
./supabase-local.sh test

# Run Python test suite
./dev.sh test

# Run tests with coverage
./dev.sh test-cov
```

### Specific Test Files

```bash
# Test local Supabase integration
python -m pytest tests/test_local_supabase.py -v

# Test authentication
python -m pytest tests/test_auth.py -v

# Test with local Supabase backend
ENVIRONMENT=local USE_SUPABASE=true python -m pytest tests/ -v
```

## Database Management

### Migrations

```bash
# Create new migration
./supabase-local.sh migrate

# Reset and apply all migrations
./supabase-local.sh reset
```

### Database Access

```bash
# Connect to PostgreSQL directly
psql -h localhost -p 54322 -U postgres -d postgres

# Or use Supabase Studio UI
open http://localhost:54323
```

### Seed Data

```bash
# Run seed scripts
./supabase-local.sh seed
```

## Troubleshooting

### Common Issues

1. **Port conflicts**: Check if ports 54321, 54322, 54323 are available
2. **Docker issues**: Ensure Docker is running and has sufficient resources
3. **Permission errors**: Make sure scripts are executable (`chmod +x`)

### Debug Commands

```bash
# Check service status
./supabase-local.sh status

# View logs
./supabase-local.sh logs

# Test connections
./supabase-local.sh test
```

### Reset Everything

```bash
# Stop services and clean up
./supabase-local.sh stop
docker system prune -f

# Start fresh
./supabase-local.sh full-start
```

## Development Workflow

### Typical Development Session

1. **Start services**:
   ```bash
   ./dev.sh supabase-local
   ```

2. **Develop and test**:
   ```bash
   # Make code changes...
   
   # Test changes
   ./dev.sh test
   ```

3. **Database changes**:
   ```bash
   # Create migration
   supabase migration new "add_new_table"
   
   # Apply migration
   ./supabase-local.sh migrate
   ```

4. **Stop when done**:
   ```bash
   ./dev.sh supabase-stop
   ```

### Hot Reloading

The FastAPI server runs with `--reload` flag, so code changes are automatically reflected. Database schema changes require migration application.

## Production Deployment

When ready for production, switch to cloud Supabase:

1. Create Supabase project at https://supabase.com
2. Update environment variables
3. Run migrations on production database
4. Deploy application

The same codebase works with both local and cloud Supabase!
