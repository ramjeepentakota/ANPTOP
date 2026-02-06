"""
ANPTOP Backend - Approval Endpoints
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from datetime import datetime

from app.db.session import get_db
from app.models.user import User
from app.models.approval import Approval, ApprovalStatus, ApprovalType
from app.core.security import get_current_user, check_permission


router = APIRouter()


class ApprovalResponse(BaseModel):
    """Approval response schema."""
    id: int
    engagement_id: int
    approval_type: ApprovalType
    status: ApprovalStatus
    title: str
    description: str
    requested_by_id: int
    approver_id: int
    approved_at: datetime
    approval_notes: str
    priority: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ApprovalAction(BaseModel):
    """Approval action schema."""
    action: str = Field(..., pattern="^(approve|deny|cancel)$")
    notes: str = None


@router.get("/", response_model=List[ApprovalResponse])
async def list_approvals(
    engagement_id: int = Query(..., description="Engagement ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List approvals for an engagement."""
    return await Approval.get_by_engagement(db, engagement_id)


@router.get("/pending", response_model=List[ApprovalResponse])
async def list_pending_approvals(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List pending approvals for current user."""
    if not check_permission(current_user, "workflows:approve"):
        raise HTTPException(status_code=403, detail="Permission denied")
    return await Approval.get_pending(db)


@router.post("/{approval_id}/action", response_model=ApprovalResponse)
async def process_approval(
    approval_id: int,
    action_data: ApprovalAction,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Process an approval request (approve/deny)."""
    if not check_permission(current_user, "workflows:approve"):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    approval = await Approval.get_by_id(db, approval_id)
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")
    
    if approval.status != ApprovalStatus.PENDING:
        raise HTTPException(status_code=400, detail="Approval is not pending")
    
    if action_data.action == "approve":
        return await approval.approve(db, current_user.id, action_data.notes)
    elif action_data.action == "deny":
        return await approval.deny(db, current_user.id, action_data.notes)
    else:
        return await approval.cancel(db)
