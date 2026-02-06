"""
ANPTOP Backend - Audit Log Endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from datetime import datetime

from app.db.session import get_db
from app.models.user import User
from app.models.audit import AuditLog
from app.core.security import get_current_user, check_permission


router = APIRouter()


class AuditLogResponse(BaseModel):
    """Audit log response schema."""
    id: int
    user_id: int
    action: str
    resource: str
    resource_id: str
    details: dict
    ip_address: str
    timestamp: datetime
    success: bool
    error_message: str
    
    class Config:
        from_attributes = True


@router.get("/", response_model=List[AuditLogResponse])
async def list_audit_logs(
    engagement_id: int = Query(..., description="Engagement ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List audit logs."""
    if not check_permission(current_user, "audit:read"):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    # Get audit logs for engagement-related resources
    logs = await AuditLog.get_by_resource(db, "engagement", str(engagement_id))
    return logs[offset:limit] if (offset := skip) else logs[:limit]


@router.get("/user/{user_id}", response_model=List[AuditLogResponse])
async def get_user_audit_logs(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get audit logs for a specific user."""
    if current_user.role != User.Role.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can view user audit logs")
    return await AuditLog.get_by_user(db, user_id, skip=skip, limit=limit)
