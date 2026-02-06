"""
ANPTOP Backend - Payment Systems Security Endpoints
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
class PaymentFindingCreate(BaseModel):
    """Payment security finding creation schema."""
    engagement_id: int
    target: str
    finding_type: str  # tls_weakness, card_data_exposure, pci_violation, etc.
    severity: str
    title: str
    description: str
    evidence: Dict = {}
    remediation: Optional[str] = None
    pci_requirement: Optional[str] = None  # PCI-DSS requirement reference


class PaymentFindingResponse(BaseModel):
    """Payment finding response schema."""
    id: int
    engagement_id: int
    target: str
    finding_type: str
    severity: str
    title: str
    description: str
    evidence: Dict
    remediation: Optional[str]
    pci_requirement: Optional[str]
    created_at: datetime


class PCISummary(BaseModel):
    """PCI-DSS compliance summary."""
    engagement_id: int
    compliant: bool
    total_requirements: int
    compliant_requirements: int
    failed_requirements: List[str]
    findings_count: int
    risk_score: float


# In-memory storage
payment_findings = []


@router.post("/findings", response_model=PaymentFindingResponse)
async def create_payment_finding(
    finding: PaymentFindingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new payment security finding.
    """
    new_finding = {
        'id': len(payment_findings) + 1,
        **finding.dict(),
        'created_at': datetime.utcnow(),
    }
    payment_findings.append(new_finding)
    return new_finding


@router.get("/findings", response_model=List[PaymentFindingResponse])
async def get_payment_findings(
    engagement_id: Optional[int] = None,
    finding_type: Optional[str] = None,
    severity: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get payment security findings, optionally filtered.
    """
    result = payment_findings
    
    if engagement_id:
        result = [f for f in result if f['engagement_id'] == engagement_id]
    
    if finding_type:
        result = [f for f in result if f['finding_type'] == finding_type]
    
    if severity:
        result = [f for f in result if f['severity'] == severity]
    
    return result


@router.get("/pci-summary")
async def get_pci_summary(
    engagement_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get PCI-DSS compliance summary for an engagement.
    """
    findings = [f for f in payment_findings if f['engagement_id'] == engagement_id]
    
    # Common PCI-DSS requirements
    pci_requirements = {
        '1.1': 'Firewall and router configuration',
        '2.1': 'Vendor-supplied defaults removed',
        '3.1': 'Card data storage limits',
        '4.1': 'Encryption of transmission',
        '5.1': 'Anti-virus deployment',
        '6.1': 'Secure system development',
        '7.1': 'Access control measures',
        '8.1': 'Unique user identification',
        '9.1': 'Physical security',
        '10.1': 'Tracking and monitoring',
        '11.1': 'Regular testing',
        '12.1': 'Security policy',
    }
    
    failed_requirements = []
    for finding in findings:
        if finding.get('pci_requirement') and finding['severity'] in ['critical', 'high']:
            if finding['pci_requirement'] not in failed_requirements:
                failed_requirements.append(finding['pci_requirement'])
    
    compliant_requirements = len(pci_requirements) - len(failed_requirements)
    total = len(pci_requirements)
    
    # Calculate risk score (0-100)
    risk_score = min(100, (len([f for f in findings if f['severity'] == 'critical']) * 25) +
                              (len([f for f in findings if f['severity'] == 'high']) * 15))
    
    return {
        'engagement_id': engagement_id,
        'compliant': len(failed_requirements) == 0,
        'total_requirements': total,
        'compliant_requirements': compliant_requirements,
        'failed_requirements': [pci_requirements.get(r, r) for r in failed_requirements],
        'findings_count': len(findings),
        'risk_score': risk_score,
    }


@router.post("/tls-check")
async def tls_check(
    target: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Perform TLS configuration check (placeholder for actual tool integration).
    """
    # In production, this would integrate with sslscan or testssl.sh
    return {
        'target': target,
        'tls_version_1_3': True,
        'tls_version_1_2': True,
        'tls_version_1_1': False,
        'tls_version_1_0': False,
        'ssl_v2': False,
        'ssl_v3': False,
        'weak_ciphers': [],
        'certificate_valid': True,
        'certificate_chain_valid': True,
    }
