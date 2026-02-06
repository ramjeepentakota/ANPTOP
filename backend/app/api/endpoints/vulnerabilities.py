"""
ANPTOP Backend - Vulnerability Endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from datetime import datetime

from app.db.session import get_db
from app.models.user import User
from app.models.vulnerability import Vulnerability, Severity, VulnerabilityStatus
from app.core.security import get_current_user, check_permission


router = APIRouter()


class VulnerabilityCreate(BaseModel):
    """Vulnerability creation schema."""
    engagement_id: int
    target_id: Optional[int] = None
    cve_id: Optional[str] = None
    cwe_id: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=255)
    severity: Severity
    cvss_score: Optional[float] = Field(None, ge=0, le=10)
    cvss_vector: Optional[str] = None
    description: str
    impact: Optional[str] = None
    remediation: Optional[str] = None
    proof_of_concept: Optional[str] = None
    affected_component: Optional[str] = None
    affected_version: Optional[str] = None
    fixed_version: Optional[str] = None
    references: Optional[List[str]] = Field(default=[])


class VulnerabilityUpdate(BaseModel):
    """Vulnerability update schema."""
    status: Optional[VulnerabilityStatus] = None
    severity: Optional[Severity] = None
    cvss_score: Optional[float] = Field(None, ge=0, le=10)
    description: Optional[str] = None
    impact: Optional[str] = None
    remediation: Optional[str] = None
    proof_of_concept: Optional[str] = None
    business_impact: Optional[str] = None
    likelihood: Optional[str] = None
    references: Optional[List[str]] = None


class VulnerabilityResponse(BaseModel):
    """Vulnerability response schema."""
    id: int
    target_id: Optional[int]
    engagement_id: int
    cve_id: Optional[str]
    cwe_id: Optional[str]
    name: str
    severity: Severity
    cvss_score: Optional[float]
    cvss_vector: Optional[str]
    description: str
    impact: Optional[str]
    remediation: Optional[str]
    proof_of_concept: Optional[str]
    status: VulnerabilityStatus
    references: List[str]
    exploit_available: bool
    exploit_in_metasploit: bool
    affected_component: Optional[str]
    affected_version: Optional[str]
    fixed_version: Optional[str]
    discovered_by: Optional[str]
    discovery_method: Optional[str]
    tool_used: Optional[str]
    business_impact: Optional[str]
    likelihood: Optional[str]
    risk_rating: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


@router.get("/", response_model=List[VulnerabilityResponse])
async def list_vulnerabilities(
    engagement_id: int = Query(..., description="Engagement ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    severity: Optional[Severity] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List vulnerabilities for an engagement."""
    if not check_permission(current_user, "vulnerabilities:read"):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    if severity:
        return await Vulnerability.get_by_severity(db, engagement_id, severity)
    return await Vulnerability.get_by_engagement(db, engagement_id, skip=skip, limit=limit)


@router.get("/{vuln_id}", response_model=VulnerabilityResponse)
async def get_vulnerability(vuln_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Get vulnerability by ID."""
    vuln = await Vulnerability.get_by_id(db, vuln_id)
    if not vuln:
        raise HTTPException(status_code=404, detail="Vulnerability not found")
    return vuln


@router.post("/", response_model=VulnerabilityResponse, status_code=201)
async def create_vulnerability(data: VulnerabilityCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Create a new vulnerability/finding."""
    if not check_permission(current_user, "findings:create"):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    vuln = Vulnerability(
        engagement_id=data.engagement_id,
        target_id=data.target_id,
        cve_id=data.cve_id,
        cwe_id=data.cwe_id,
        name=data.name,
        severity=data.severity,
        cvss_score=data.cvss_score,
        cvss_vector=data.cvss_vector,
        description=data.description,
        impact=data.impact,
        remediation=data.remediation,
        proof_of_concept=data.proof_of_concept,
        affected_component=data.affected_component,
        affected_version=data.affected_version,
        fixed_version=data.fixed_version,
        references=data.references or [],
    )
    await vuln.save(db)
    return vuln


@router.put("/{vuln_id}", response_model=VulnerabilityResponse)
async def update_vulnerability(vuln_id: int, data: VulnerabilityUpdate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Update a vulnerability."""
    vuln = await Vulnerability.get_by_id(db, vuln_id)
    if not vuln:
        raise HTTPException(status_code=404, detail="Vulnerability not found")
    update_data = data.model_dump(exclude_unset=True)
    return await vuln.update(db, **update_data)
