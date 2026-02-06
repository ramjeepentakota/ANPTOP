"""
ANPTOP Backend - Report Endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from datetime import datetime

from app.db.session import get_db
from app.models.user import User
from app.models.report import Report, ReportType
from app.models.engagement import Engagement
from app.core.security import get_current_user, check_permission


router = APIRouter()


class ReportCreate(BaseModel):
    """Report creation schema."""
    engagement_id: int
    title: str = Field(..., min_length=1, max_length=255)
    report_type: ReportType = ReportType.TECHNICAL_REPORT
    summary: Optional[str] = None
    methodology: Optional[str] = None
    recommendations: Optional[str] = None


class ReportResponse(BaseModel):
    """Report response schema."""
    id: int
    engagement_id: int
    title: str
    report_type: ReportType
    summary: Optional[str]
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    info_count: int
    generated_by_id: int
    generated_at: datetime
    is_draft: bool
    is_final: bool
    
    class Config:
        from_attributes = True


@router.get("/", response_model=List[ReportResponse])
async def list_reports(
    engagement_id: int = Query(..., description="Engagement ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List reports for an engagement."""
    if not check_permission(current_user, "reports:read"):
        raise HTTPException(status_code=403, detail="Permission denied")
    return await Report.get_by_engagement(db, engagement_id)


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get report by ID."""
    report = await Report.get_by_id(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.post("/", response_model=ReportResponse, status_code=201)
async def create_report(
    data: ReportCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new report."""
    if not check_permission(current_user, "reports:create"):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    report = Report(
        engagement_id=data.engagement_id,
        title=data.title,
        report_type=data.report_type,
        summary=data.summary,
        methodology=data.methodology,
        recommendations=data.recommendations,
        generated_by_id=current_user.id,
        is_draft=True,
        is_final=False,
    )
    await report.save(db)
    return report


@router.post("/{report_id}/finalize")
async def finalize_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark a report as final."""
    report = await Report.get_by_id(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return await report.finalize(db)
