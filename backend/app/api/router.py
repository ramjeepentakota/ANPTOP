"""
ANPTOP Backend - API Router
"""

from fastapi import APIRouter
from app.api.endpoints import auth, users, engagements, targets, workflows, vulnerabilities, evidence, approvals, health

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(engagements.router, prefix="/engagements", tags=["Engagements"])
api_router.include_router(targets.router, prefix="/targets", tags=["Targets"])
api_router.include_router(workflows.router, prefix="/workflows", tags=["Workflows"])
api_router.include_router(vulnerabilities.router, prefix="/vulnerabilities", tags=["Vulnerabilities"])
api_router.include_router(evidence.router, prefix="/evidence", tags=["Evidence"])
api_router.include_router(approvals.router, prefix="/approvals", tags=["Approvals"])
api_router.include_router(health.router, prefix="/health", tags=["Health"])
