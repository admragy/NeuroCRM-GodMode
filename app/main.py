"""
OmniCRM God Mode - Main Application Entry Point
FastAPI Application for AI-Powered Sales OS
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import logging
import sys
from pathlib import Path

# Import routers
from app.api.v1 import router as api_v1_router
from app.core.config import settings
from app.middleware.error_handler import error_handler_middleware
from app.middleware.logging_middleware import logging_middleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="OmniCRM God Mode",
    description="AI-Powered Sales Operating System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # في الإنتاج، استخدم قائمة محددة
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Middleware
app.middleware("http")(error_handler_middleware)
app.middleware("http")(logging_middleware)

# Mount static files (if exists)
static_path = Path(__file__).parent.parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")


# Health check endpoint
@app.get("/")
async def root():
    """Root endpoint - Health check"""
    return {
        "status": "operational",
        "service": "OmniCRM God Mode",
        "version": "1.0.0",
        "message": "AI-Powered Sales OS is running! 🚀"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": "omnicrm-godmode",
        "timestamp": "2026-01-06T00:00:00Z"
    }


@app.get("/api/v1/status")
async def api_status():
    """API status endpoint"""
    return {
        "api_version": "v1",
        "status": "operational",
        "features": [
            "AI Sales Agents",
            "Voice AI (<1s latency)",
            "WhatsApp Integration",
            "Predictive Analytics",
            "Real-Time Dashboard"
        ]
    }


# Include API routers (when available)
try:
    app.include_router(api_v1_router, prefix="/api/v1")
    logger.info("API v1 router included successfully")
except Exception as e:
    logger.warning(f"Could not include API v1 router: {e}")
    logger.warning("Running in minimal mode with health checks only")


# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup tasks"""
    logger.info("🚀 OmniCRM God Mode is starting...")
    logger.info(f"Environment: {getattr(settings, 'ENVIRONMENT', 'production')}")
    logger.info("✅ Application started successfully!")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown tasks"""
    logger.info("🛑 OmniCRM God Mode is shutting down...")
    logger.info("✅ Shutdown completed successfully!")


# Exception handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Custom 404 handler"""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": f"The path {request.url.path} does not exist",
            "suggestion": "Check /docs for available endpoints"
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Custom 500 handler"""
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "Something went wrong on our end",
            "support": "Please contact support if the issue persists"
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
