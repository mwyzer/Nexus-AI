from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import models  # noqa: F401 - populates Base.metadata as a side effect
from .config import settings
from .api.v1.router import api_router

app = FastAPI(
    title="Nexus AI Backend",
    description="AI-powered knowledge and agent platform",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API router
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "service": "nexus-ai-backend",
        "version": "0.1.0",
        "status": "running",
    }
