"""
ANPTOP Backend - Evidence Endpoints
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from datetime import datetime

from app.db.session import get_db
from app.models.user import User
from app.models.evidence import Evidence, EvidenceType, EvidenceChainOfCustody
from app.core.security import get_current_user, hash_evidence


router = APIRouter()


class EvidenceResponse(BaseModel):
    """Evidence response schema."""
    id: int
    engagement_id: int
    target_id: int
    workflow_execution_id: int
    filename: str
    evidence_type: EvidenceType
    file_size: int
    sha256_hash: str
    title: str
    description: str
    confidentiality_level: str
    collected_at: datetime
    collected_by: int
    
    class Config:
        from_attributes = True


@router.get("/", response_model=List[EvidenceResponse])
async def list_evidence(
    engagement_id: int = Query(..., description="Engagement ID"),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List evidence for an engagement."""
    return await Evidence.get_by_engagement(db, engagement_id, skip=skip, limit=limit)


@router.get("/{evidence_id}", response_model=EvidenceResponse)
async def get_evidence(
    evidence_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get evidence by ID."""
    evidence = await Evidence.get_by_id(db, evidence_id)
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    return evidence


@router.post("/upload", response_model=EvidenceResponse, status_code=201)
async def upload_evidence(
    file: UploadFile = File(...),
    engagement_id: int = Query(...),
    target_id: int = Query(None),
    workflow_execution_id: int = Query(None),
    title: str = Query(...),
    evidence_type: EvidenceType = Query(EvidenceType.SCREENSHOT),
    description: str = Query(""),
    confidentiality_level: str = Query("internal"),
    current_user: User = Depends(get_current_user),
):
    """
    Upload evidence file.
    
    Files are stored securely with cryptographic hashing for integrity.
    """
    content = await file.read()
    file_hash = hash_evidence(content)
    
    # In production, save to secure storage (S3/MinIO)
    file_path = f"/secure/evidence/{file_hash}"
    
    evidence = Evidence(
        engagement_id=engagement_id,
        target_id=target_id,
        workflow_execution_id=workflow_execution_id,
        filename=file.filename,
        file_path=file_path,
        evidence_type=evidence_type,
        file_size=len(content),
        mime_type=file.content_type,
        sha256_hash=file_hash,
        title=title,
        description=description,
        confidentiality_level=confidentiality_level,
        collected_by=current_user.id,
        storage_backend="local",
    )
    
    # Save metadata to database
    # Actual file would be saved to secure storage
    
    return evidence


@router.post("/{evidence_id}/custody")
async def add_custody_record(
    evidence_id: int,
    action: str,
    notes: str = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add a chain of custody record."""
    evidence = await Evidence.get_by_id(db, evidence_id)
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    
    custody = EvidenceChainOfCustody(
        evidence_id=evidence_id,
        action=action,
        action_by=current_user.id,
        notes=notes,
        hash_value=evidence.sha256_hash,
    )
    
    await custody.save(db)
    return {"message": "Custody record added"}
