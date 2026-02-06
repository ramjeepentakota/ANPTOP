"""
ANPTOP Backend - Cloud Security Endpoints
"""

from datetime import datetime
from typing import Optional, List, Dict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.db.session import get_db
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()


# Pydantic schemas
class CloudFindingCreate(BaseModel):
    """Cloud finding creation schema."""
    engagement_id: int
    provider: str  # aws, azure, gcp
    resource_type: str
    resource_name: str
    resource_id: Optional[str] = None
    region: Optional[str] = None
    finding_type: str  # misconfiguration, vulnerability, exposure
    severity: str
    title: str
    description: str
    remediation: Optional[str] = None
    evidence: Dict = {}


class CloudFindingResponse(BaseModel):
    """Cloud finding response schema."""
    id: int
    engagement_id: int
    provider: str
    resource_type: str
    resource_name: str
    resource_id: Optional[str]
    region: Optional[str]
    finding_type: str
    severity: str
    title: str
    description: str
    remediation: Optional[str]
    evidence: Dict
    created_at: datetime


class CloudVulnerabilityCreate(BaseModel):
    """Cloud vulnerability creation schema."""
    engagement_id: int
    finding_id: Optional[int] = None
    cve_id: Optional[str] = None
    provider: str
    service: str
    severity: str
    cvss_score: float
    title: str
    description: str
    affected_resources: List[str] = []
    remediation: Optional[str] = None


class CloudVulnerabilityResponse(BaseModel):
    """Cloud vulnerability response schema."""
    id: int
    engagement_id: int
    finding_id: Optional[int]
    cve_id: Optional[str]
    provider: str
    service: str
    severity: str
    cvss_score: float
    title: str
    description: str
    affected_resources: List[str]
    remediation: Optional[str]
    created_at: datetime


# In-memory storage
cloud_findings = []
cloud_vulnerabilities = []


@router.post("/findings", response_model=CloudFindingResponse)
async def create_cloud_finding(
    finding: CloudFindingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new cloud security finding.
    """
    new_finding = {
        'id': len(cloud_findings) + 1,
        **finding.dict(),
        'created_at': datetime.utcnow(),
    }
    cloud_findings.append(new_finding)
    return new_finding


@router.post("/findings/bulk")
async def create_cloud_findings_bulk(
    findings_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create multiple cloud findings in bulk.
    """
    findings_list = findings_data.get('findings', [])
    aggregated = findings_data.get('aggregated_findings', {})
    
    created = []
    for finding_data in findings_list:
        new_finding = {
            'id': len(cloud_findings) + 1,
            **finding_data,
            'created_at': datetime.utcnow(),
        }
        cloud_findings.append(new_finding)
        created.append(new_finding)
    
    return {
        'created': len(created),
        'aggregated_findings': aggregated,
    }


@router.get("/findings", response_model=List[CloudFindingResponse])
async def get_cloud_findings(
    engagement_id: Optional[int] = None,
    provider: Optional[str] = None,
    severity: Optional[str] = None,
    finding_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get cloud findings, optionally filtered.
    """
    result = cloud_findings
    
    if engagement_id:
        result = [f for f in result if f['engagement_id'] == engagement_id]
    
    if provider:
        result = [f for f in result if f['provider'] == provider]
    
    if severity:
        result = [f for f in result if f['severity'] == severity]
    
    if finding_type:
        result = [f for f in result if f['finding_type'] == finding_type]
    
    return result


@router.get("/findings/summary")
async def get_cloud_findings_summary(
    engagement_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get summary of cloud findings for an engagement.
    """
    findings = [f for f in cloud_findings if f['engagement_id'] == engagement_id]
    
    severity_counts = {
        'critical': len([f for f in findings if f['severity'] == 'critical']),
        'high': len([f for f in findings if f['severity'] == 'high']),
        'medium': len([f for f in findings if f['severity'] == 'medium']),
        'low': len([f for f in findings if f['severity'] == 'low']),
    }
    
    provider_counts = {}
    for finding in findings:
        provider = finding['provider']
        provider_counts[provider] = provider_counts.get(provider, 0) + 1
    
    return {
        'engagement_id': engagement_id,
        'total_findings': len(findings),
        'severity_counts': severity_counts,
        'provider_counts': provider_counts,
    }


@router.post("/vulnerabilities", response_model=CloudVulnerabilityResponse)
async def create_cloud_vulnerability(
    vulnerability: CloudVulnerabilityCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new cloud vulnerability.
    """
    new_vuln = {
        'id': len(cloud_vulnerabilities) + 1,
        **vulnerability.dict(),
        'created_at': datetime.utcnow(),
    }
    cloud_vulnerabilities.append(new_vuln)
    return new_vuln


@router.get("/vulnerabilities", response_model=List[CloudVulnerabilityResponse])
async def get_cloud_vulnerabilities(
    engagement_id: Optional[int] = None,
    provider: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get cloud vulnerabilities.
    """
    result = cloud_vulnerabilities
    
    if engagement_id:
        result = [v for v in result if v['engagement_id'] == engagement_id]
    
    if provider:
        result = [v for v in result if v['provider'] == provider]
    
    return result
