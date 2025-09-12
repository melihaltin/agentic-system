@echo off
setlocal enabledelayedexpansion

echo Team AI Backend Development Helper (Windows)
echo =============================================

if "%1"=="" (
    goto :show_help
) else if "%1"=="install" (
    goto :install
) else if "%1"=="dev" (
    goto :dev
) else if "%1"=="test" (
    goto :test
) else if "%1"=="supabase-local" (
    goto :supabase_local
) else if "%1"=="supabase-stop" (
    goto :supabase_stop
) else if "%1"=="dev-supabase" (
    goto :dev_supabase
) else (
    echo Unknown command: %1
    goto :show_help
)

:install
echo 📦 Installing Python dependencies...
call venv\Scripts\activate.bat
pip install -r requirements.txt
goto :end

:dev
echo 🚀 Starting development server...
call venv\Scripts\activate.bat
uvicorn main:app --reload --host 0.0.0.0 --port 8000
goto :end

:test
echo 🧪 Running tests...
call venv\Scripts\activate.bat
python -m pytest tests/ -v
goto :end

:supabase_local
echo 🚀 Starting local Supabase...
call supabase-local.bat start
goto :end

:supabase_stop
echo 🛑 Stopping local Supabase...
call supabase-local.bat stop
goto :end

:dev_supabase
echo 🔥 Starting development server with local Supabase...
set USE_SUPABASE=true
set ENVIRONMENT=local
call venv\Scripts\activate.bat
uvicorn main:app --reload --host 0.0.0.0 --port 8000
goto :end

:show_help
echo.
echo Available commands:
echo   install         Install Python dependencies
echo   dev             Start development server
echo   test            Run tests
echo   supabase-local  Start local Supabase
echo   supabase-stop   Stop local Supabase
echo   dev-supabase    Start server with local Supabase
echo.
goto :end

:end