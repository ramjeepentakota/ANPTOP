"""
ANPTOP Backend - Health Check Endpoints
"""

from typing import Dict
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.db.session import get_db


router = APIRouter()


@router.get("/", response_model=Dict)
async def health_check():
    """
    Basic health check endpoint.
    Returns the service status and version information.
    """
    return {
        "status": "healthy",
        "service": "anptop-backend",
        "version": "2.0.0",
        "timestamp": "2024-02-06T00:00:00Z",
    }


@router.get("/detailed", response_model=Dict)
async def detailed_health_check(db: AsyncSession = Depends(get_db)):
    """
    Detailed health check including database connectivity.
    """
    db_status = "unknown"
    
    try:
        # Test database connection
        await db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "service": "anptop-backend",
        "version": "2.0.0",
        "timestamp": "2024-02-06T00:00:00Z",
        "components": {
            "database": db_status,
            "cache": "unknown",
            "storage": "unknown",
        },
    }


@router.get("/ready")
async def readiness_check():
    """
    Kubernetes readiness probe endpoint.
    """
    return {"ready": True}


@router.get("/live")
async def liveness_check():
    """
    Kubernetes liveness probe endpoint.
    """
    return {"alive": True}
