"""
ANPTOP Backend - Main FastAPI Application
Automated Network Penetration Testing Orchestration Platform
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from app.core.config import settings
from app.api.router import api_router
from app.db.session import engine, Base
from app.core.security import (
    verify_scope_boundaries,
    kill_switch_active,
    audit_log
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("anptop.log"),
    ],
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan events."""
    # Startup
    logger.info("🚀 Starting ANPTOP Backend...")
    logger.info(f"📋 Environment: {settings.APP_ENV}")
    logger.info(f"🔐 MFA Enabled: {settings.MFA_ENABLED}")
    
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("✅ Database tables created")
    logger.info("✅ ANPTOP Backend started successfully")
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down ANPTOP Backend...")
    await engine.dispose()
    logger.info("✅ Cleanup complete")


# Create FastAPI application
app = FastAPI(
    title="ANPTOP - Automated Network Penetration Testing Orchestration Platform",
    description="""
    ## 🚀 ANPTOP API

    Semi-automated network penetration testing orchestration platform for fintech red teaming.

    ### Features
    - **Engagement Management**: Create and manage pentest engagements
    - **Target Discovery**: Automated host and service discovery
    - **Vulnerability Assessment**: Integration with OpenVAS, Nuclei, and custom scanners
    - **Exploitation Framework**: Metasploit integration with approval workflows
    - **Reporting**: Executive and technical reports with evidence
    - **Security**: RBAC, MFA, and comprehensive audit logging

    ### Authentication
    All endpoints require JWT authentication. Use the `/api/v1/auth/login` endpoint to obtain tokens.

    ### Authorization
    Role-Based Access Control (RBAC) is enforced on all endpoints.

    ## 🔐 Security Notice
    This platform is designed for authorized security testing only.
    Ensure you have proper authorization before conducting any security assessments.
    """,
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle uncaught exceptions."""
    logger.error(f"❌ Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal error occurred. Please contact the administrator.",
            "type": type(exc).__name__,
        },
    )


# Kill switch middleware
@app.middleware("http")
async def kill_switch_middleware(request: Request, call_next):
    """Check if kill switch is active."""
    if kill_switch_active():
        logger.warning("🛑 Kill switch is active - blocking request")
        return JSONResponse(
            status_code=503,
            content={
                "detail": "Platform is in maintenance mode. All operations have been halted.",
                "code": "KILL_SWITCH_ACTIVE",
            },
        )
    
    response = await call_next(request)
    return response


# Scope validation middleware
@app.middleware("http")
async def scope_validation_middleware(request: Request, call_next):
    """Validate that targets are within engagement scope."""
    # Skip for non-target endpoints
    if "/targets" not in request.url.path:
        return await call_next(request)
    
    # Check scope for target operations
    if request.method in ["POST", "PUT"]:
        # Will validate in endpoint handler
        pass
    
    response = await call_next(request)
    return response


# Audit logging middleware
@app.middleware("http")
async def audit_middleware(request: Request, call_next):
    """Log all API requests for audit purposes."""
    # Skip health checks
    if request.url.path in ["/health", "/metrics"]:
        return await call_next(request)
    
    # Log request
    logger.info(f"📝 API Request: {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    # Log response status
    logger.info(f"📝 Response: {response.status_code}")
    
    # Audit log
    await audit_log(
        action=f"{request.method} {request.url.path}",
        user_id=None,  # Will be set by auth middleware
        resource=request.url.path,
        details={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
        },
    )
    
    return response


# Metrics endpoint
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    from fastapi.responses import Response
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "service": "anptop-backend",
    }


# Include API router
app.include_router(api_router, prefix="/api/v1")


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "ANPTOP - Automated Network Penetration Testing Orchestration Platform",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health",
        "status": "operational",
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info",
    )
