"""
ANPTOP Backend - CVE Endpoints
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.db.session import get_db
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()


# Pydantic schemas
class CVESearchRequest(BaseModel):
    """CVE search request schema."""
    services: List[dict]


class CVEInfo(BaseModel):
    """CVE information schema."""
    cve_id: str
    description: str
    cvss_score: float
    cvss_vector: Optional[str] = None
    severity: str
    published_date: Optional[str] = None
    modified_date: Optional[str] = None
    exploit_available: bool = False
    exploit_status: Optional[str] = None
    references: List[str] = []


class CVECorrelationResult(BaseModel):
    """CVE correlation result schema."""
    service_id: int
    host_id: int
    host_ip: str
    cve_id: str
    cvss_score: float
    severity: str
    exploit_available: bool
    description: str
    solution: Optional[str] = None
    confidence: float = 0.8


class CVESearchResponse(BaseModel):
    """CVE search response schema."""
    correlations: List[CVECorrelationResult]
    total_found: int


class CVEBase(BaseModel):
    """Base CVE schema."""
    cve_id: str
    description: str
    cvss_score: float
    cvss_vector: Optional[str] = None
    severity: str
    published_date: Optional[str] = None
    modified_date: Optional[str] = None
    exploit_available: bool = False
    exploit_published: bool = False


# Simulated CVE database (in production, use actual NVD database)
CVE_DATABASE = {
    'apache': [
        {'cve_id': 'CVE-2021-41773', 'cvss_score': 7.5, 'severity': 'high', 'description': 'Apache Path Traversal', 'product': 'apache httpd'},
        {'cve_id': 'CVE-2021-45046', 'cvss_score': 8.8, 'severity': 'critical', 'description': 'Apache Remote Code Execution', 'product': 'apache httpd'},
    ],
    'nginx': [
        {'cve_id': 'CVE-2022-41741', 'cvss_score': 6.5, 'severity': 'medium', 'description': 'NGINX Heap Buffer Overflow', 'product': 'nginx'},
    ],
    'openssh': [
        {'cve_id': 'CVE-2023-38408', 'cvss_score': 9.8, 'severity': 'critical', 'description': 'OpenSSH RCE', 'product': 'openssh'},
    ],
    'samba': [
        {'cve_id': 'CVE-2017-7494', 'cvss_score': 10.0, 'severity': 'critical', 'description': 'Samba RCE', 'product': 'samba'},
    ],
    'wordpress': [
        {'cve_id': 'CVE-2023-22234', 'cvss_score': 9.8, 'severity': 'critical', 'description': 'WordPress RCE', 'product': 'wordpress'},
    ],
    'tomcat': [
        {'cve_id': 'C-193VE-20208', 'cvss_score': 9.8, 'severity': 'critical', 'description': 'Apache Tomcat AJP RCE', 'product': 'tomcat'},
    ],
    'mysql': [
        {'cve_id': 'CVE-2021-22555', 'cvss_score': 9.8, 'severity': 'critical', 'description': 'MySQL RCE', 'product': 'mysql'},
    ],
    'postgresql': [
        {'cve_id': 'CVE-2024-1597', 'cvss_score': 9.8, 'severity': 'critical', 'description': 'PostgreSQL RCE', 'product': 'postgresql'},
    ],
    'mssql': [
        {'cve_id': 'CVE-2023-29357', 'cvss_score': 9.8, 'severity': 'critical', 'description': 'Microsoft SQL Server RCE', 'product': 'mssql'},
    ],
    'smb': [
        {'cve_id': 'CVE-2017-0144', 'cvss_score': 9.8, 'severity': 'critical', 'description': 'EternalBlue - Windows SMB RCE', 'product': 'smb'},
        {'cve_id': 'CVE-2019-0708', 'cvss_score': 9.8, 'severity': 'critical', 'description': 'BlueKeep - Windows RDP RCE', 'product': 'rdp'},
    ],
}


def get_severity(cvss_score: float) -> str:
    """Get severity rating from CVSS score."""
    if cvss_score >= 9.0:
        return 'critical'
    elif cvss_score >= 7.0:
        return 'high'
    elif cvss_score >= 4.0:
        return 'medium'
    elif cvss_score >= 0.1:
        return 'low'
    return 'informational'


def match_cves(service_name: str, version: str = None) -> List[dict]:
    """Match CVEs to a service based on name and version."""
    matches = []
    service_lower = service_name.lower()
    
    for product, cves in CVE_DATABASE.items():
        if product in service_lower or service_lower in product:
            for cve in cves:
                matches.append({
                    **cve,
                    'severity': get_severity(cve['cvss_score']),
                    'exploit_available': cve['cvss_score'] >= 7.0,
                })
    
    return matches


@router.post("/search", response_model=CVESearchResponse)
async def search_cves(
    request: CVESearchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Search for CVEs matching discovered services.
    
    This endpoint correlates discovered services with CVE database
    to identify potential vulnerabilities.
    """
    correlations = []
    
    for service in request.services:
        service_name = service.get('service_name', '')
        version = service.get('service_version', '')
        host_id = service.get('host_id', 0)
        host_ip = service.get('ip', '')
        service_id = service.get('id', 0)
        
        cves = match_cves(service_name, version)
        
        for cve in cves:
            correlations.append({
                'service_id': service_id,
                'host_id': host_id,
                'host_ip': host_ip,
                'cve_id': cve['cve_id'],
                'cvss_score': cve['cvss_score'],
                'severity': cve['severity'],
                'exploit_available': cve['exploit_available'],
                'description': cve['description'],
                'confidence': 0.85,
            })
    
    return {
        'correlations': correlations,
        'total_found': len(correlations),
    }


@router.get("/cve/{cve_id}", response_model=CVEInfo)
async def get_cve_info(
    cve_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get detailed information about a specific CVE.
    """
    # Search in local database
    for product, cves in CVE_DATABASE.items():
        for cve in cves:
            if cve['cve_id'] == cve_id:
                return {
                    'cve_id': cve['cve_id'],
                    'description': cve['description'],
                    'cvss_score': cve['cvss_score'],
                    'severity': get_severity(cve['cvss_score']),
                    'exploit_available': cve['cvss_score'] >= 7.0,
                    'exploit_status': 'available' if cve['cvss_score'] >= 7.0 else None,
                    'references': [f'https://nvd.nist.gov/vuln/detail/{cve_id}'],
                }
    
    raise HTTPException(
        status_code=404,
        detail=f"CVE {cve_id} not found",
    )


@router.get("/correlate/{engagement_id}")
async def correlate_engagement_cves(
    engagement_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Correlate CVEs for all services in an engagement.
    """
    # In production, this would query the database for services
    # For now, return a placeholder response
    return {
        'engagement_id': engagement_id,
        'status': 'pending',
        'message': 'CVE correlation in progress',
    }
