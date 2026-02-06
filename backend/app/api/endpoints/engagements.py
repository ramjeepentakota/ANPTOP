"""
ANPTOP Backend - Engagement Endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from datetime import datetime

from app.db.session import get_db
from app.models.user import User
from app.models.engagement import Engagement, EngagementStatus, EngagementType
from app.core.security import get_current_user, audit_log


router = APIRouter()


# Pydantic schemas
class EngagementCreate(BaseModel):
    """Engagement creation schema."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    engagement_type: EngagementType = EngagementType.EXTERNAL
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    target_scope: List[str] = Field(default_factory=list)
    blacklisted_ips: List[str] = Field(default_factory=list)
    rules_of_engagement: Optional[str] = None
    compliance_standards: List[str] = Field(default_factory=list)
    client_name: Optional[str] = None
    client_contact: Optional[str] = None
    client_email: Optional[str] = None
    team_members: List[int] = Field(default_factory=list)
    auto_approve_workflows: bool = False
    require_evidence: bool = True
    metadata: Optional[dict] = None
    notes: Optional[str] = None


class EngagementUpdate(BaseModel):
    """Engagement update schema."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    engagement_type: Optional[EngagementType] = None
    status: Optional[EngagementStatus] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    target_scope: Optional[List[str]] = None
    blacklisted_ips: Optional[List[str]] = None
    rules_of_engagement: Optional[str] = None
    compliance_standards: Optional[List[str]] = None
    client_name: Optional[str] = None
    client_contact: Optional[str] = None
    client_email: Optional[str] = None
    team_members: Optional[List[int]] = None
    auto_approve_workflows: Optional[bool] = None
    require_evidence: Optional[bool] = None
    metadata: Optional[dict] = None
    notes: Optional[str] = None


class EngagementResponse(BaseModel):
    """Engagement response schema."""
    id: int
    name: str
    description: Optional[str]
    engagement_type: EngagementType
    status: EngagementStatus
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    target_scope: List[str]
    blacklisted_ips: List[str]
    rules_of_engagement: Optional[str]
    compliance_standards: List[str]
    client_name: Optional[str]
    client_contact: Optional[str]
    client_email: Optional[str]
    owner_id: int
    team_members: List[int]
    auto_approve_workflows: bool
    require_evidence: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


@router.get("/", response_model=List[EngagementResponse])
async def list_engagements(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status_filter: Optional[EngagementStatus] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List all engagements.
    
    Users can only see engagements they have access to based on their role.
    """
    # Admins and leads see all engagements
    if current_user.role in [User.Role.ADMIN, User.Role.LEAD]:
        engagements = await Engagement.get_all(db, skip=skip, limit=limit, status=status_filter)
    else:
        # Other users only see engagements they're part of
        engagements = await Engagement.get_by_owner(db, current_user.id, skip=skip, limit=limit)
    
    return engagements


@router.get("/{engagement_id}", response_model=EngagementResponse)
async def get_engagement(
    engagement_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get engagement by ID.
    """
    engagement = await Engagement.get_by_id(db, engagement_id)
    
    if not engagement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Engagement not found",
        )
    
    # Check access
    if current_user.role not in [User.Role.ADMIN, User.Role.LEAD]:
        if engagement.owner_id != current_user.id and current_user.id not in engagement.team_members:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this engagement",
            )
    
    return engagement


@router.post("/", response_model=EngagementResponse, status_code=status.HTTP_201_CREATED)
async def create_engagement(
    engagement_data: EngagementCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new engagement.
    
    Requires: admin, lead, or senior role.
    """
    if not current_user.has_permission("engagements:create"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to create engagements",
        )
    
    # Create engagement
    engagement = Engagement(
        name=engagement_data.name,
        description=engagement_data.description,
        engagement_type=engagement_data.engagement_type,
        start_date=engagement_data.start_date,
        end_date=engagement_data.end_date,
        target_scope=engagement_data.target_scope,
        blacklisted_ips=engagement_data.blacklisted_ips,
        rules_of_engagement=engagement_data.rules_of_engagement,
        compliance_standards=engagement_data.compliance_standards,
        client_name=engagement_data.client_name,
        client_contact=engagement_data.client_contact,
        client_email=engagement_data.client_email,
        owner_id=current_user.id,
        team_members=engagement_data.team_members,
        auto_approve_workflows=engagement_data.auto_approve_workflows,
        require_evidence=engagement_data.require_evidence,
        metadata=engagement_data.metadata,
        notes=engagement_data.notes,
    )
    
    await engagement.save(db)
    
    # Audit log
    await audit_log(
        action="engagement:create",
        user_id=current_user.id,
        resource="engagement",
        details={"engagement_id": engagement.id, "name": engagement.name},
        db=db,
    )
    
    return engagement


@router.put("/{engagement_id}", response_model=EngagementResponse)
async def update_engagement(
    engagement_id: int,
    engagement_data: EngagementUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update an engagement.
    
    Requires: admin, lead, or ownership.
    """
    engagement = await Engagement.get_by_id(db, engagement_id)
    
    if not engagement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Engagement not found",
        )
    
    # Check permissions
    if current_user.role not in [User.Role.ADMIN, User.Role.LEAD]:
        if engagement.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this engagement",
            )
    
    # Update fields
    update_data = engagement_data.model_dump(exclude_unset=True)
    engagement = await engagement.update(db, **update_data)
    
    # Audit log
    await audit_log(
        action="engagement:update",
        user_id=current_user.id,
        resource="engagement",
        details={"engagement_id": engagement.id, "updates": list(update_data.keys())},
        db=db,
    )
    
    return engagement


@router.delete("/{engagement_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_engagement(
    engagement_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete an engagement.
    
    Requires: admin or lead role.
    """
    if not current_user.has_permission("engagements:delete"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete engagements",
        )
    
    engagement = await Engagement.get_by_id(db, engagement_id)
    
    if not engagement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Engagement not found",
        )
    
    await engagement.delete(db)
    
    # Audit log
    await audit_log(
        action="engagement:delete",
        user_id=current_user.id,
        resource="engagement",
        details={"engagement_id": engagement_id},
        db=db,
    )


@router.post("/{engagement_id}/start")
async def start_engagement(
    engagement_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Start an engagement (change status to active).
    """
    engagement = await Engagement.get_by_id(db, engagement_id)
    
    if not engagement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Engagement not found",
        )
    
    if engagement.status != EngagementStatus.PLANNING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Engagement can only be started from planning status",
        )
    
    engagement.status = EngagementStatus.ACTIVE
    engagement.start_date = datetime.utcnow()
    await engagement.update(db)
    
    return {"message": "Engagement started successfully", "engagement": engagement}


@router.post("/{engagement_id}/complete")
async def complete_engagement(
    engagement_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Complete an engagement.
    """
    engagement = await Engagement.get_by_id(db, engagement_id)
    
    if not engagement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Engagement not found",
        )
    
    engagement.status = EngagementStatus.COMPLETED
    engagement.end_date = datetime.utcnow()
    await engagement.update(db)
    
    return {"message": "Engagement completed successfully", "engagement": engagement}
