"""MJ SEO - FastAPI Backend Server"""
from fastapi import FastAPI, APIRouter, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os
import logging
from pathlib import Path
from contextlib import asynccontextmanager
import time

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Import routes
from routes import auth, audits, plans, admin, chat, api_tokens, reports, themes, env_keys, llm_settings, seo_settings
from routes import payments_stripe, admin_payments
from routes import api_key_pool, integrations, competitors, content_opportunities, anomalies

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
    logger.info("🚀 Starting MJ SEO Backend...")
    logger.info("📊 Database: PostgreSQL")
    logger.info("🤖 AI Model: Multi-LLM (Groq, OpenAI, Anthropic, Gemini, Ollama)")
    logger.info("🔌 Integrations: DataForSEO, Lighthouse, Exa.ai")
    logger.info("🎯 Enhanced Orchestrator with 6 Sub-Agents")
    yield
    # Shutdown
    logger.info("Shutting down MJ SEO Backend...")


# Create FastAPI app
app = FastAPI(
    title="MJ SEO API",
    description="Production-ready SEO Audit Platform with AI-powered insights and 9 API integrations",
    version="2.0.0",
    lifespan=lifespan
)


# ============================================================================
# PRODUCTION SECURITY HEADERS MIDDLEWARE
# ============================================================================

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add production security headers to all responses"""
    response = await call_next(request)
    
    # Security Headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    
    # HSTS (HTTP Strict Transport Security) - Enable in production with HTTPS
    if os.getenv("ENABLE_HSTS", "false").lower() == "true":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    # Content Security Policy (CSP) - Customize as needed
    if os.getenv("ENABLE_CSP", "false").lower() == "true":
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' https:;"
        )
        response.headers["Content-Security-Policy"] = csp
    
    return response


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add request processing time to response headers"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.4f}"
    return response


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Resource not found", "path": request.url.path}
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please try again later."}
    )


# ============================================================================
# MIDDLEWARE
# ============================================================================

# GZIP compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Trusted hosts (optional - uncomment and configure for production)
# app.add_middleware(
#     TrustedHostMiddleware,
#     allowed_hosts=os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
# )


# Create API router with /api prefix
api_router = APIRouter(prefix="/api")

# Health check endpoint
@api_router.get("/")
async def root():
    return {
        "message": "MJ SEO API",
        "version": "2.0.0",
        "status": "operational",
        "features": [
            "135+ SEO Checks",
            "Multi-LLM Support",
            "DataForSEO Integration",
            "Lighthouse Performance",
            "Competitor Analysis",
            "Content Opportunities",
            "AI Sub-Agents"
        ]
    }


@api_router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "MJ SEO Backend",
        "version": "2.0.0",
        "database": "postgresql",
        "integrations": {
            "dataforseo": "configured",
            "lighthouse": "installed",
            "exa_ai": "configured",
            "multi_llm": "active"
        }
    }


# Include route modules
api_router.include_router(auth.router)
api_router.include_router(audits.router)
api_router.include_router(plans.router)
api_router.include_router(admin.router)
api_router.include_router(chat.router)
api_router.include_router(api_tokens.router)
api_router.include_router(reports.router)
api_router.include_router(payments_stripe.router)  # Stripe payment system
api_router.include_router(admin_payments.router)   # Admin payment management
api_router.include_router(themes.router)
api_router.include_router(env_keys.router)  # Environment keys management
api_router.include_router(llm_settings.router)  # LLM settings management
api_router.include_router(seo_settings.router)  # SEO settings management

# NEW: Production-grade routes
api_router.include_router(api_key_pool.router)  # API key pool management
api_router.include_router(integrations.router)  # Integration monitoring
api_router.include_router(competitors.router)  # Competitor analysis
api_router.include_router(content_opportunities.router)  # Content opportunities

# Include API router in main app
app.include_router(api_router)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Process-Time", "X-Request-ID"]
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )
