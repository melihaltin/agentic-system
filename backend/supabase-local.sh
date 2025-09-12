#!/bin/bash

# Local Supabase Management Script for Team AI Backend

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}Team AI Local Supabase Manager${NC}"
echo "====================================="

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_blue() {
    echo -e "${BLUE}[SUPABASE]${NC} $1"
}

# Check if Supabase CLI is installed
check_supabase_cli() {
    if ! command -v supabase &> /dev/null; then
        print_error "Supabase CLI is not installed!"
        echo "Please install it first:"
        echo "  curl -o- https://raw.githubusercontent.com/supabase/cli/main/install.sh | bash"
        echo "  or: brew install supabase/tap/supabase"
        echo "  or: npm install -g @supabase/cli"
        exit 1
    fi
    print_status "Supabase CLI found: $(supabase --version)"
}

# Check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running! Please start Docker first."
        exit 1
    fi
    print_status "Docker is running"
}

case "$1" in
    "init")
        print_blue "Initializing local Supabase project..."
        check_supabase_cli
        check_docker
        
        # Initialize Supabase if not already done
        if [ ! -f "supabase/config.toml" ]; then
            supabase init
            print_status "Supabase project initialized"
        else
            print_status "Supabase project already initialized"
        fi
        
        # Copy our custom config
        if [ -f "supabase/config.toml.backup" ]; then
            cp supabase/config.toml.backup supabase/config.toml
            print_status "Custom configuration restored"
        fi
        ;;
    
    "start")
        print_blue "Starting local Supabase..."
        check_supabase_cli
        check_docker
        
        # Start Supabase
        supabase start
        
        print_status "Local Supabase is running!"
        print_status "Dashboard: http://localhost:54323"
        print_status "API URL: http://localhost:54321"
        print_status "Database URL: postgresql://postgres:postgres@localhost:54322/postgres"
        
        # Show connection details
        echo ""
        echo -e "${BLUE}Connection Details:${NC}"
        echo "API URL: http://localhost:54321"
        echo "GraphQL URL: http://localhost:54321/graphql/v1"
        echo "DB URL: postgresql://postgres:postgres@localhost:54322/postgres"
        echo "Studio URL: http://localhost:54323"
        echo "Inbucket URL: http://localhost:54324"
        echo "JWT secret: super-secret-jwt-token-with-at-least-32-characters-long"
        echo "anon key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0"
        echo "service_role key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImV4cCI6MTk4MzgxMjk5Nn0.EGIM96RAZx35lJzdJsyH-qQwv8Hdp7fsn3W0YpN81IU"
        ;;
    
    "stop")
        print_blue "Stopping local Supabase..."
        supabase stop
        print_status "Local Supabase stopped"
        ;;
    
    "restart")
        print_blue "Restarting local Supabase..."
        supabase stop
        supabase start
        print_status "Local Supabase restarted"
        ;;
    
    "reset")
        print_blue "Resetting local Supabase (this will delete all data)..."
        read -p "Are you sure? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            supabase db reset
            print_status "Local Supabase reset completed"
        else
            print_status "Reset cancelled"
        fi
        ;;
    
    "status")
        print_blue "Checking local Supabase status..."
        supabase status
        ;;
    
    "logs")
        print_blue "Showing local Supabase logs..."
        supabase logs
        ;;
    
    "migrate")
        print_blue "Running database migrations..."
        supabase db reset
        print_status "Migrations applied"
        ;;
    
    "studio")
        print_blue "Opening Supabase Studio..."
        open "http://localhost:54323" || echo "Please open http://localhost:54323 in your browser"
        ;;
    
    "test-connection")
        print_blue "Testing connection to local Supabase..."
        
        # Test API endpoint
        if curl -s -o /dev/null -w "%{http_code}" http://localhost:54321/rest/v1/ | grep -q "200"; then
            print_status "✅ API connection successful"
        else
            print_error "❌ API connection failed"
        fi
        
        # Test database connection
        if pg_isready -h localhost -p 54322 >/dev/null 2>&1; then
            print_status "✅ Database connection successful"
        else
            print_error "❌ Database connection failed"
        fi
        
        # Test Studio
        if curl -s -o /dev/null -w "%{http_code}" http://localhost:54323 | grep -q "200"; then
            print_status "✅ Studio connection successful"
        else
            print_error "❌ Studio connection failed"
        fi
        ;;
    
    "backend")
        print_blue "Starting backend with local Supabase..."
        
        # Copy local environment
        if [ -f ".env.local" ]; then
            cp .env.local .env
            print_status "Local environment configuration loaded"
        fi
        
        # Start the backend
        uvicorn main:app --reload --host 0.0.0.0 --port 8000
        ;;
    
    "docker-backend")
        print_blue "Starting backend with Docker and local Supabase..."
        docker-compose -f docker-compose.local.yml up --build
        ;;
    
    "seed")
        print_blue "Seeding database with test data..."
        
        # Apply seed data
        if [ -f "supabase/seed.sql" ]; then
            psql -h localhost -p 54322 -U postgres -d postgres -f supabase/seed.sql
            print_status "Seed data applied"
        else
            print_warning "No seed.sql file found"
        fi
        ;;
    
    "backup")
        print_blue "Creating database backup..."
        mkdir -p backups
        pg_dump -h localhost -p 54322 -U postgres -d postgres > "backups/supabase_backup_$(date +%Y%m%d_%H%M%S).sql"
        print_status "Backup created in backups/ directory"
        ;;
    
    "full-start")
        print_blue "Full setup: Starting Supabase and backend..."
        check_supabase_cli
        check_docker
        
        # Start Supabase
        supabase start
        
        # Wait a bit for Supabase to be ready
        sleep 5
        
        # Copy local environment
        if [ -f ".env.local" ]; then
            cp .env.local .env
            print_status "Local environment configuration loaded"
        fi
        
        print_status "Local Supabase started successfully!"
        print_status "You can now start the backend with: ./supabase-local.sh backend"
        print_status "Or visit the dashboard at: http://localhost:54323"
        ;;
    
    *)
        echo "Local Supabase Management Script"
        echo ""
        echo "Usage: $0 {command}"
        echo ""
        echo "Setup Commands:"
        echo "  init           Initialize local Supabase project"
        echo "  start          Start local Supabase services"
        echo "  stop           Stop local Supabase services"
        echo "  restart        Restart local Supabase services"
        echo "  full-start     Start Supabase and prepare environment"
        echo ""
        echo "Development Commands:"
        echo "  backend        Start FastAPI backend with local Supabase"
        echo "  docker-backend Start backend with Docker"
        echo "  studio         Open Supabase Studio in browser"
        echo ""
        echo "Database Commands:"
        echo "  migrate        Run database migrations"
        echo "  reset          Reset database (deletes all data)"
        echo "  seed           Apply seed data"
        echo "  backup         Create database backup"
        echo ""
        echo "Utility Commands:"
        echo "  status         Show service status"
        echo "  logs           Show service logs"
        echo "  test-connection Test all connections"
        echo ""
        echo "Examples:"
        echo "  $0 full-start     # Complete setup"
        echo "  $0 backend        # Start backend only"
        echo "  $0 studio         # Open dashboard"
        echo "  $0 reset          # Reset everything"
        ;;
esac
