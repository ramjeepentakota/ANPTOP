"""
ANPTOP Backend - Kubernetes Security Endpoints
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
class K8sFindingCreate(BaseModel):
    """Kubernetes finding creation schema."""
    engagement_id: int
    cluster_name: Optional[str] = None
    namespace: Optional[str] = None
    resource_type: str  # pod, service, deployment, etc.
    resource_name: str
    finding_type: str  # vulnerability, misconfiguration, exposure
    severity: str
    title: str
    description: str
    remediation: Optional[str] = None
    evidence: Dict = {}


class K8sFindingResponse(BaseModel):
    """Kubernetes finding response schema."""
    id: int
    engagement_id: int
    cluster_name: Optional[str]
    namespace: Optional[str]
    resource_type: str
    resource_name: str
    finding_type: str
    severity: str
    title: str
    description: str
    remediation: Optional[str]
    evidence: Dict
    created_at: datetime


class K8sExploitationCreate(BaseModel):
    """Kubernetes exploitation creation schema."""
    engagement_id: int
    finding_id: Optional[int] = None
    cluster_name: Optional[str] = None
    namespace: Optional[str] = None
    technique: str  # pod_escape, service_account_abuse, etc.
    target_resource: Optional[str] = None
    exploitation_success: bool
    findings: Dict = {}
    output: Optional[str] = None


class K8sExploitationResponse(BaseModel):
    """Kubernetes exploitation response schema."""
    id: int
    engagement_id: int
    finding_id: Optional[int]
    cluster_name: Optional[str]
    namespace: Optional[str]
    technique: str
    target_resource: Optional[str]
    exploitation_success: bool
    findings: Dict
    output: Optional[str]
    created_at: datetime


# In-memory storage
k8s_findings = []
k8s_exploitations = []


@router.post("/findings", response_model=K8sFindingResponse)
async def create_k8s_finding(
    finding: K8sFindingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new Kubernetes security finding.
    """
    new_finding = {
        'id': len(k8s_findings) + 1,
        **finding.dict(),
        'created_at': datetime.utcnow(),
    }
    k8s_findings.append(new_finding)
    return new_finding


@router.get("/findings", response_model=List[K8sFindingResponse])
async def get_k8s_findings(
    engagement_id: Optional[int] = None,
    namespace: Optional[str] = None,
    severity: Optional[str] = None,
    resource_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get Kubernetes findings, optionally filtered.
    """
    result = k8s_findings
    
    if engagement_id:
        result = [f for f in result if f['engagement_id'] == engagement_id]
    
    if namespace:
        result = [f for f in result if f['namespace'] == namespace]
    
    if severity:
        result = [f for f in result if f['severity'] == severity]
    
    if resource_type:
        result = [f for f in result if f['resource_type'] == resource_type]
    
    return result


@router.get("/findings/summary")
async def get_k8s_findings_summary(
    engagement_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get summary of Kubernetes findings.
    """
    findings = [f for f in k8s_findings if f['engagement_id'] == engagement_id]
    
    severity_counts = {
        'critical': len([f for f in findings if f['severity'] == 'critical']),
        'high': len([f for f in findings if f['severity'] == 'high']),
        'medium': len([f for f in findings if f['severity'] == 'medium']),
        'low': len([f for f in findings if f['severity'] == 'low']),
    }
    
    namespace_counts = {}
    for finding in findings:
        ns = finding['namespace'] or 'default'
        namespace_counts[ns] = namespace_counts.get(ns, 0) + 1
    
    resource_counts = {}
    for finding in findings:
        rt = finding['resource_type']
        resource_counts[rt] = resource_counts.get(rt, 0) + 1
    
    return {
        'engagement_id': engagement_id,
        'total_findings': len(findings),
        'severity_counts': severity_counts,
        'namespace_counts': namespace_counts,
        'resource_counts': resource_counts,
    }


@router.post("/exploitation", response_model=K8sExploitationResponse)
async def create_k8s_exploitation(
    exploitation: K8sExploitationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a Kubernetes exploitation record.
    """
    new_exploitation = {
        'id': len(k8s_exploitations) + 1,
        **exploitation.dict(),
        'created_at': datetime.utcnow(),
    }
    k8s_exploitations.append(new_exploitation)
    return new_exploitation


@router.get("/exploitation", response_model=List[K8sExploitationResponse])
async def get_k8s_exploitations(
    engagement_id: Optional[int] = None,
    exploitation_success: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get Kubernetes exploitation records.
    """
    result = k8s_exploitations
    
    if engagement_id:
        result = [e for e in result if e['engagement_id'] == engagement_id]
    
    if exploitation_success is not None:
        result = [e for e in result if e['exploitation_success'] == exploitation_success]
    
    return result
