#!/bin/bash

# Team AI Backend Development Helper Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Team AI Backend Development Helper${NC}"
echo "=================================="

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

# Check if .env file exists
if [ ! -f .env ]; then
    print_warning ".env file not found. Creating from template..."
    cp .env.example .env
    print_status "Please edit .env file with your configuration before continuing."
    exit 1
fi

case "$1" in
    "install")
        print_status "Installing Python dependencies..."
        pip install -r requirements.txt
        print_status "Dependencies installed successfully!"
        ;;
    
    "migrate")
        print_status "Running database migrations..."
        alembic upgrade head
        print_status "Migrations completed!"
        ;;
    
    "makemigrations")
        if [ -z "$2" ]; then
            print_error "Please provide a migration message: ./dev.sh makemigrations 'your message'"
            exit 1
        fi
        print_status "Creating new migration: $2"
        alembic revision --autogenerate -m "$2"
        print_status "Migration created!"
        ;;
    
    "dev")
        print_status "Starting development server..."
        uvicorn main:app --reload --host 0.0.0.0 --port 8000
        ;;
    
    "docker")
        print_status "Starting development environment with Docker..."
        docker-compose up --build
        ;;
    
    "docker-down")
        print_status "Stopping Docker containers..."
        docker-compose down
        ;;
    
    "test")
        print_status "Running tests..."
        pytest
        ;;
    
    "test-cov")
        print_status "Running tests with coverage..."
        pytest --cov=. --cov-report=html --cov-report=term-missing
        print_status "Coverage report generated in htmlcov/"
        ;;
    
    "format")
        print_status "Formatting code with black..."
        black .
        print_status "Sorting imports with isort..."
        isort .
        print_status "Code formatted!"
        ;;
    
    "lint")
        print_status "Running linting with mypy..."
        mypy .
        ;;
    
    "clean")
        print_status "Cleaning up cache files..."
        find . -type d -name __pycache__ -delete
        find . -name "*.pyc" -delete
        rm -rf .pytest_cache
        rm -rf htmlcov
        rm -rf .coverage
        print_status "Cache cleaned!"
        ;;
    
    "setup")
        print_status "Setting up development environment..."
        pip install -r requirements.txt
        print_status "Creating database migrations..."
        alembic revision --autogenerate -m "Initial migration"
        print_status "Running migrations..."
        alembic upgrade head
        print_status "Setup completed! You can now run: ./dev.sh dev"
        ;;
    
    *)
        echo "Team AI Backend Development Helper"
        echo ""
        echo "Usage: $0 {command}"
        echo ""
        echo "Commands:"
        echo "  install                    Install Python dependencies"
        echo "  migrate                    Run database migrations"
        echo "  makemigrations 'message'   Create new migration"
        echo "  dev                        Start development server"
        echo "  docker                     Start with Docker Compose"
        echo "  docker-down               Stop Docker containers"
        echo "  test                      Run tests"
        echo "  test-cov                  Run tests with coverage"
        echo "  format                    Format code (black + isort)"
        echo "  lint                      Run type checking (mypy)"
        echo "  clean                     Clean cache files"
        echo "  setup                     Full development setup"
        echo ""
        echo "Examples:"
        echo "  $0 setup                          # Initial setup"
        echo "  $0 makemigrations 'add users'     # Create migration"
        echo "  $0 dev                            # Start dev server"
        echo "  $0 docker                         # Start with Docker"
        ;;
esac
