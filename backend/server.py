"""MJ SEO - FastAPI Backend Server"""
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import logging
from pathlib import Path
from contextlib import asynccontextmanager

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Import routes
from routes import auth, audits, plans, admin, chat, api_tokens, reports

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting MJ SEO Backend...")
    logger.info("Database: PostgreSQL")
    logger.info("AI Model: Groq (Llama 3.3 70B)")
    yield
    # Shutdown
    logger.info("Shutting down MJ SEO Backend...")


# Create FastAPI app
app = FastAPI(
    title="MJ SEO API",
    description="Production-ready SEO Audit Platform with AI-powered insights",
    version="1.0.0",
    lifespan=lifespan
)

# Create API router with /api prefix
api_router = APIRouter(prefix="/api")

# Health check endpoint
@api_router.get("/")
async def root():
    return {
        "message": "MJ SEO API",
        "version": "1.0.0",
        "status": "operational"
    }


@api_router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "MJ SEO Backend",
        "database": "postgresql"
    }


# Include route modules
api_router.include_router(auth.router)
api_router.include_router(audits.router)
api_router.include_router(plans.router)
api_router.include_router(admin.router)
api_router.include_router(chat.router)
api_router.include_router(api_tokens.router)
api_router.include_router(reports.router)

# Include API router in main app
app.include_router(api_router)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )
