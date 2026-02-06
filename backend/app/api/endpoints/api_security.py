"""
ANPTOP Backend - API Security Endpoints
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
class APIVulnerabilityCreate(BaseModel):
    """API vulnerability creation schema."""
    engagement_id: int
    target_url: str
    endpoint: Optional[str] = None
    http_method: Optional[str] = None
    vulnerability_type: str  # sqli, xss, idor, auth_bypass, etc.
    severity: str
    title: str
    description: str
    evidence: Dict = {}
    remediation: Optional[str] = None
    curl_poc: Optional[str] = None


class APIVulnerabilityResponse(BaseModel):
    """API vulnerability response schema."""
    id: int
    engagement_id: int
    target_url: str
    endpoint: Optional[str]
    http_method: Optional[str]
    vulnerability_type: str
    severity: str
    title: str
    description: str
    evidence: Dict
    remediation: Optional[str]
    curl_poc: Optional[str]
    created_at: datetime


# In-memory storage
api_vulnerabilities = []


@router.post("/vulnerabilities", response_model=APIVulnerabilityResponse)
async def create_api_vulnerability(
    vulnerability: APIVulnerabilityCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new API security vulnerability.
    """
    new_vuln = {
        'id': len(api_vulnerabilities) + 1,
        **vulnerability.dict(),
        'created_at': datetime.utcnow(),
    }
    api_vulnerabilities.append(new_vuln)
    return new_vuln


@router.post("/vulnerabilities/bulk")
async def create_api_vulnerabilities_bulk(
    vulnerabilities_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create multiple API vulnerabilities in bulk.
    """
    vulnerabilities_list = vulnerabilities_data.get('vulnerabilities', [])
    
    created = []
    for vuln_data in vulnerabilities_list:
        new_vuln = {
            'id': len(api_vulnerabilities) + 1,
            **vuln_data,
            'created_at': datetime.utcnow(),
        }
        api_vulnerabilities.append(new_vuln)
        created.append(new_vuln)
    
    return {
        'created': len(created),
        'vulnerabilities': created,
    }


@router.get("/vulnerabilities", response_model=List[APIVulnerabilityResponse])
async def get_api_vulnerabilities(
    engagement_id: Optional[int] = None,
    vulnerability_type: Optional[str] = None,
    severity: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get API vulnerabilities, optionally filtered.
    """
    result = api_vulnerabilities
    
    if engagement_id:
        result = [v for v in result if v['engagement_id'] == engagement_id]
    
    if vulnerability_type:
        result = [v for v in result if v['vulnerability_type'] == vulnerability_type]
    
    if severity:
        result = [v for v in result if v['severity'] == severity]
    
    return result


@router.get("/vulnerabilities/summary")
async def get_api_vulnerabilities_summary(
    engagement_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get summary of API vulnerabilities.
    """
    vulnerabilities = [v for v in api_vulnerabilities if v['engagement_id'] == engagement_id]
    
    severity_counts = {
        'critical': len([v for v in vulnerabilities if v['severity'] == 'critical']),
        'high': len([v for v in vulnerabilities if v['severity'] == 'high']),
        'medium': len([v for v in vulnerabilities if v['severity'] == 'medium']),
        'low': len([v for v in vulnerabilities if v['severity'] == 'low']),
    }
    
    type_counts = {}
    for vuln in vulnerabilities:
        vt = vuln['vulnerability_type']
        type_counts[vt] = type_counts.get(vt, 0) + 1
    
    return {
        'engagement_id': engagement_id,
        'total_vulnerabilities': len(vulnerabilities),
        'severity_counts': severity_counts,
        'type_counts': type_counts,
    }
