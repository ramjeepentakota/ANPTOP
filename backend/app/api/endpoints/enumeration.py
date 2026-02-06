"""
ANPTOP Backend - Enumeration Endpoints
"""

from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.db.session import get_db
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()


# Pydantic schemas
class EnumerationResultCreate(BaseModel):
    """Enumeration result creation schema."""
    engagement_id: int
    service_id: int
    host_id: int
    ip: str
    port: int
    enum_type: str
    findings: dict = {}
    raw_output: Optional[str] = None


class EnumerationResultResponse(BaseModel):
    """Enumeration result response schema."""
    id: int
    engagement_id: int
    service_id: int
    host_id: int
    ip: str
    port: int
    enum_type: str
    findings: dict
    raw_output: Optional[str]
    created_at: datetime


class ServiceCreate(BaseModel):
    """Service creation schema."""
    engagement_id: int
    host_id: int
    ip: str
    hostname: Optional[str] = None
    port: int
    protocol: str = "tcp"
    service_name: str
    service_version: Optional[str] = None
    service_product: Optional[str] = None
    confidence: float = 0.0


class ServiceResponse(BaseModel):
    """Service response schema."""
    id: int
    engagement_id: int
    host_id: int
    ip: str
    hostname: Optional[str]
    port: int
    protocol: str
    service_name: str
    service_version: Optional[str]
    service_product: Optional[str]
    confidence: float
    created_at: datetime


# In-memory storage
enumeration_results = []
services = []


@router.post("/services", response_model=ServiceResponse)
async def create_service(
    service: ServiceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new discovered service.
    """
    new_service = {
        'id': len(services) + 1,
        **service.dict(),
        'created_at': datetime.utcnow(),
    }
    services.append(new_service)
    return new_service


@router.post("/services/bulk")
async def create_services_bulk(
    services_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create multiple services in bulk.
    """
    services_list = services_data.get('services', [])
    created = []
    
    for service_data in services_list:
        new_service = {
            'id': len(services) + 1,
            **service_data,
            'created_at': datetime.utcnow(),
        }
        services.append(new_service)
        created.append(new_service)
    
    return {
        'created': len(created),
        'services': created,
    }


@router.get("/services", response_model=List[ServiceResponse])
async def get_services(
    engagement_id: Optional[int] = None,
    host_id: Optional[int] = None,
    has_version: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get discovered services, optionally filtered.
    """
    result = services
    
    if engagement_id:
        result = [s for s in result if s['engagement_id'] == engagement_id]
    
    if host_id:
        result = [s for s in result if s['host_id'] == host_id]
    
    if has_version:
        result = [s for s in result if s.get('service_version')]
    
    return result


@router.get("/services/{service_id}", response_model=ServiceResponse)
async def get_service(
    service_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a specific service by ID.
    """
    service = next((s for s in services if s['id'] == service_id), None)
    
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    return service


@router.post("/results", response_model=EnumerationResultResponse)
async def create_enumeration_result(
    result: EnumerationResultCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create an enumeration result.
    """
    new_result = {
        'id': len(enumeration_results) + 1,
        **result.dict(),
        'created_at': datetime.utcnow(),
    }
    enumeration_results.append(new_result)
    return new_result


@router.get("/results", response_model=List[EnumerationResultResponse])
async def get_enumeration_results(
    engagement_id: Optional[int] = None,
    host_id: Optional[int] = None,
    enum_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get enumeration results, optionally filtered.
    """
    result = enumeration_results
    
    if engagement_id:
        result = [r for r in result if r['engagement_id'] == engagement_id]
    
    if host_id:
        result = [r for r in result if r['host_id'] == host_id]
    
    if enum_type:
        result = [r for r in result if r['enum_type'] == enum_type]
    
    return result
