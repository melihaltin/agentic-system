from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from core.config import settings
from core.database import engine, Base
from features.users.router import router as users_router
from features.auth.router import router as auth_router
from features.auth.supabase_router import router as supabase_auth_router
from features.businesses.router import router as businesses_router
from features.services.router import router as services_router
from features.logs.router import router as logs_router
from core.supabase import supabase_client
import structlog
import time
from fastapi import Request

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    logger.info("Starting up FastAPI application")

    # Startup: Create tables if in development
    if settings.environment == "development":
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created")

    yield

    # Shutdown: Close database connections
    await engine.dispose()
    logger.info("Database connections closed")


app = FastAPI(
    title="Team AI Backend API",
    description="FastAPI backend with PostgreSQL for Team AI application",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs" if settings.environment != "production" else None,
    redoc_url="/api/redoc" if settings.environment != "production" else None,
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_hosts,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.add_middleware(
#     TrustedHostMiddleware,
#     allowed_hosts=settings.allowed_hosts,
# )


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests with timing information."""
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    logger.info(
        "HTTP request processed",
        method=request.method,
        url=str(request.url),
        status_code=response.status_code,
        duration_seconds=round(duration, 4),
        client_ip=request.client.host if request.client else "unknown",
    )
    return response


# Include routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(supabase_auth_router, prefix="/auth/supabase", tags=["Supabase Authentication"])
app.include_router(users_router, prefix="/users", tags=["Users"])
app.include_router(businesses_router, prefix="/businesses", tags=["Businesses"])
app.include_router(services_router, prefix="/services", tags=["Services"])
app.include_router(logs_router, prefix="/logs", tags=["Logs"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Team AI Backend API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    # Test Supabase connection if configured
    supabase_status = "not_configured"
    if hasattr(settings, 'supabase_url') and settings.supabase_url:
        try:
            supabase_healthy = await supabase_client.test_connection()
            supabase_status = "healthy" if supabase_healthy else "unhealthy"
        except Exception:
            supabase_status = "error"
    
    return {
        "status": "healthy",
        "database": "postgresql",
        "supabase": supabase_status,
        "environment": settings.environment,
    }
