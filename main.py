OmniCRM Ultimate Enterprise Edition v7.0.0
Main Application Entry Point

Advanced CRM System with:
- Multi-Provider AI Integration
- Real-time Analytics
- WhatsApp Integration
- Facebook Ads Management
- Enterprise Security

import os
import sys
import logging
from pathlib import Path
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.core.config import settings
from app.core.database import engine, create_tables
from app.api.dependencies import get_ws_current_user
from app.api.routes import api_router
from app.services.websocket_service import manager, handle_chat_message, handle_typing_indicator
from fastapi import WebSocket, WebSocketDisconnect
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="NeuroCRM - OmniCRM Ultimate Enterprise")

# Mount static files if frontend is served from backend (optional)
if Path("static").exists():
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates (optional)
if Path("templates").exists():
    templates = Jinja2Templates(directory="templates")
else:
    templates = None

# Middleware: GZip
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Configure CORS
# Read ALLOW_ORIGINS from environment, comma-separated. Default to allow all origins (not recommended for production).
allow_origins = os.getenv("ALLOW_ORIGINS")
if allow_origins:
    origins = [o.strip() for o in allow_origins.split(",") if o.strip()]
else:
    # If NEXT_PUBLIC_* is used by frontend, allow those by default using wildcard for dev convenience
    origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api")

# Health endpoint
@app.get("/health", tags=["health"])
async def health():
    """Simple health check endpoint"""
    try:
        # Optionally try a light DB check if create_tables / engine are available
        # Here we just return ok and server time
        return {"status": "ok", "time": datetime.utcnow().isoformat() + "Z"}
    except Exception as e:
        logger.exception("Health check failed")
        return JSONResponse(status_code=500, content={"status": "error", "detail": str(e)})

# WebSocket endpoints & manager were in original code; ensure they are included in api_router or defined elsewhere.
# For graceful startup/shutdown, keep startup events if present in original project

@app.on_event("startup")
async def on_startup():
    logger.info("Starting application - creating tables if needed")
    try:
        # If create_tables is a callable to initialize DB models, call it
        if callable(create_tables):
            create_tables()
    except Exception:
        logger.exception("Error while running create_tables")

@app.on_event("shutdown")
async def on_shutdown():
    logger.info("Shutting down application")

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)