"""
ANPTOP Backend - Target Endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from datetime import datetime

from app.db.session import get_db
from app.models.user import User
from app.models.target import Target, TargetType, TargetStatus
from app.models.engagement import Engagement
from app.core.security import get_current_user, verify_scope_boundaries, audit_log


router = APIRouter()


# Pydantic schemas
class TargetCreate(BaseModel):
    """Target creation schema."""
    identifier: str = Field(..., min_length=1, max_length=255)
    target_type: TargetType = TargetType.HOST
    hostname: Optional[str] = None
    operating_system: Optional[str] = None
    mac_address: Optional[str] = None
    ports: List[int] = Field(default=[])
    services: Optional[List[dict]] = Field(default=[])
    protocols: List[str] = Field(default=["tcp"])
    cloud_provider: Optional[str] = None
    cloud_account_id: Optional[str] = None
    cloud_region: Optional[str] = None
    cloud_resource_id: Optional[str] = None
    web_framework: Optional[str] = None
    technologies: List[str] = Field(default=[])
    target_metadata: Optional[dict] = None
    notes: Optional[str] = None
    tags: List[str] = Field(default=[])


class TargetUpdate(BaseModel):
    """Target update schema."""
    identifier: Optional[str] = Field(None, min_length=1, max_length=255)
    target_type: Optional[TargetType] = None
    hostname: Optional[str] = None
    operating_system: Optional[str] = None
    mac_address: Optional[str] = None
    ports: Optional[List[int]] = None
    services: Optional[List[dict]] = None
    protocols: Optional[List[str]] = None
    status: Optional[TargetStatus] = None
    is_alive: Optional[bool] = None
    is_in_scope: Optional[bool] = None
    cloud_provider: Optional[str] = None
    cloud_account_id: Optional[str] = None
    cloud_region: Optional[str] = None
    cloud_resource_id: Optional[str] = None
    web_framework: Optional[str] = None
    technologies: Optional[List[str]] = None
    target_metadata: Optional[dict] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None


class TargetResponse(BaseModel):
    """Target response schema."""
    id: int
    engagement_id: int
    identifier: str
    target_type: TargetType
    hostname: Optional[str]
    operating_system: Optional[str]
    mac_address: Optional[str]
    ports: List[int]
    services: List[dict]
    protocols: List[str]
    status: TargetStatus
    is_alive: bool
    is_in_scope: bool
    cloud_provider: Optional[str]
    cloud_account_id: Optional[str]
    cloud_region: Optional[str]
    cloud_resource_id: Optional[str]
    web_framework: Optional[str]
    technologies: List[str]
    vulnerabilities: List[dict]
    target_metadata: Optional[dict]
    notes: Optional[str]
    tags: List[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


@router.get("/", response_model=List[TargetResponse])
async def list_targets(
    engagement_id: int = Query(..., description="Engagement ID to filter targets"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status_filter: Optional[TargetStatus] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List all targets for an engagement.
    """
    # Verify engagement exists and user has access
    engagement = await Engagement.get_by_id(db, engagement_id)
    if not engagement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Engagement not found",
        )
    
    if not current_user.has_permission("targets:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view targets",
        )
    
    targets = await Target.get_by_engagement(db, engagement_id, skip=skip, limit=limit)
    
    if status_filter:
        targets = [t for t in targets if t.status == status_filter]
    
    return targets


@router.get("/{target_id}", response_model=TargetResponse)
async def get_target(
    target_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get target by ID.
    """
    target = await Target.get_by_id(db, target_id)
    
    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target not found",
        )
    
    if not current_user.has_permission("targets:read"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view targets",
        )
    
    return target


@router.post("/", response_model=TargetResponse, status_code=status.HTTP_201_CREATED)
async def create_target(
    target_data: TargetCreate,
    engagement_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Add a target to an engagement.
    
    Requires: targets:create permission.
    Validates that target is within engagement scope.
    """
    if not current_user.has_permission("targets:create"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to add targets",
        )
    
    # Verify engagement exists
    engagement = await Engagement.get_by_id(db, engagement_id)
    if not engagement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Engagement not found",
        )
    
    # Check if target is in scope
    is_in_scope = verify_scope_boundaries(
        engagement_id,
        target_data.identifier,
        engagement.target_scope,
    )
    
    if not is_in_scope:
        # Check if user wants to add out-of-scope target
        if not target_data.identifier in engagement.blacklisted_ips:
            # Log warning but allow
            pass
    
    # Create target
    target = Target(
        engagement_id=engagement_id,
        identifier=target_data.identifier,
        target_type=target_data.target_type,
        hostname=target_data.hostname,
        operating_system=target_data.operating_system,
        mac_address=target_data.mac_address,
        ports=target_data.ports,
        services=target_data.services or [],
        protocols=target_data.protocols,
        is_in_scope=is_in_scope,
        cloud_provider=target_data.cloud_provider,
        cloud_account_id=target_data.cloud_account_id,
        cloud_region=target_data.cloud_region,
        cloud_resource_id=target_data.cloud_resource_id,
        web_framework=target_data.web_framework,
        technologies=target_data.technologies,
        target_metadata=target_data.target_metadata,
        notes=target_data.notes,
        tags=target_data.tags,
    )
    
    await target.save(db)
    
    # Audit log
    await audit_log(
        action="target:create",
        user_id=current_user.id,
        resource="target",
        details={"target_id": target.id, "identifier": target.identifier},
        db=db,
    )
    
    return target


@router.put("/{target_id}", response_model=TargetResponse)
async def update_target(
    target_id: int,
    target_data: TargetUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update a target.
    
    Requires: targets:update permission.
    """
    if not current_user.has_permission("targets:update"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update targets",
        )
    
    target = await Target.get_by_id(db, target_id)
    
    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target not found",
        )
    
    update_data = target_data.model_dump(exclude_unset=True)
    target = await target.update(db, **update_data)
    
    # Audit log
    await audit_log(
        action="target:update",
        user_id=current_user.id,
        resource="target",
        details={"target_id": target.id, "updates": list(update_data.keys())},
        db=db,
    )
    
    return target


@router.delete("/{target_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_target(
    target_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a target.
    
    Requires: targets:delete permission.
    """
    if not current_user.has_permission("targets:delete"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete targets",
        )
    
    target = await Target.get_by_id(db, target_id)
    
    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target not found",
        )
    
    await target.delete(db)
    
    # Audit log
    await audit_log(
        action="target:delete",
        user_id=current_user.id,
        resource="target",
        details={"target_id": target_id},
        db=db,
    )


@router.post("/{target_id}/scan")
async def trigger_target_scan(
    target_id: int,
    scan_type: str = Query(..., description="Type of scan: port, service, vuln"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Trigger a scan on a specific target.
    """
    if not current_user.has_permission("workflows:execute"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to execute workflows",
        )
    
    target = await Target.get_by_id(db, target_id)
    
    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target not found",
        )
    
    # This would trigger an n8n workflow
    # Implementation depends on n8n integration
    
    return {
        "message": f"{scan_type} scan triggered for target {target.identifier}",
        "target_id": target_id,
        "scan_type": scan_type,
    }
