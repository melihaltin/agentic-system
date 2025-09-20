from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.features.auth.router import router as auth_router
from src.features.agents.router import voice_router, agent_router

app = FastAPI(
    title="Team AI Backend API",
    description="Backend API for Team AI business registration and management",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(voice_router)
app.include_router(agent_router)


@app.get("/")
async def root():
    return {"message": "Team AI Backend API is running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}
