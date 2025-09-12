@echo off
setlocal enabledelayedexpansion

echo Team AI Local Supabase Manager (Windows)
echo ========================================

if "%1"=="" (
    goto :show_help
) else if "%1"=="start" (
    goto :start
) else if "%1"=="stop" (
    goto :stop
) else if "%1"=="status" (
    goto :status
) else if "%1"=="reset" (
    goto :reset
) else if "%1"=="logs" (
    goto :logs
) else (
    echo Unknown command: %1
    goto :show_help
)

:start
echo [INFO] Starting local Supabase...
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not installed or not in PATH!
    goto :end
)
docker ps >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running! Please start Docker Desktop first.
    goto :end
)

echo [INFO] Initializing Supabase...
supabase init --force
echo [INFO] Starting Supabase services...
supabase start
goto :end

:stop
echo [INFO] Stopping Supabase services...
supabase stop
goto :end

:status
echo [INFO] Checking Supabase status...
supabase status
goto :end

:reset
echo [INFO] Resetting Supabase database...
supabase db reset
goto :end

:logs
echo [INFO] Showing Supabase logs...
supabase logs
goto :end

:show_help
echo.
echo Available commands:
echo   start    Start local Supabase services
echo   stop     Stop local Supabase services
echo   status   Check service status
echo   reset    Reset database
echo   logs     Show logs
echo.
goto :end

:end