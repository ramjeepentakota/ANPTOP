"""
ANPTOP Backend - Approval and Report Models
"""

from datetime import datetime
from enum import Enum as PyEnum
from typing import List, Optional
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from app.db.base import Base, TimestampMixin


class ApprovalStatus(str, PyEnum):
    """Approval request status."""
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class ApprovalType(str, PyEnum):
    """Types of approval requests."""
    WORKFLOW_EXECUTION = "workflow_execution"
    EXPLOITATION = "exploitation"
    SCOPE_CHANGE = "scope_change"
    REPORT_GENERATION = "report_generation"
    DATA_EXPORT = "data_export"
    ACCESS_REQUEST = "access_request"


class Approval(Base, TimestampMixin):
    """Approval request model for gated operations."""
    
    id = Column(Integer, primary_key=True, index=True)
    engagement_id = Column(Integer, ForeignKey("engagements.id"), nullable=False)
    
    # Request info
    approval_type = Column(Enum(ApprovalType), nullable=False)
    status = Column(Enum(ApprovalStatus), default=ApprovalStatus.PENDING, nullable=False)
    
    # Request details
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    requested_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Workflow-specific (if applicable)
    workflow_execution_id = Column(Integer, ForeignKey("workflow_executions.id"), nullable=True)
    
    # Approval info
    approver_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    approval_notes = Column(Text, nullable=True)
    
    # Denial info
    denial_reason = Column(Text, nullable=True)
    
    # Expiration
    expires_at = Column(DateTime, nullable=True)
    
    # Priority
    priority = Column(Integer, default=5, nullable=False)  # 1-10, higher = more urgent
    
    # Supporting data
    request_data = Column(JSON, default={}, nullable=True)
    
    # Relationships
    engagement = relationship("Engagement", back_populates="approvals")
    requester = relationship("User", foreign_keys=[requested_by_id])
    approver = relationship("User", foreign_keys=[approver_id])
    
    # CRUD operations
    @classmethod
    async def get_by_id(cls, db, approval_id: int) -> Optional["Approval"]:
        """Get approval by ID."""
        from sqlalchemy import select
        result = await db.execute(select(cls).where(cls.id == approval_id))
        return result.scalar_one_or_none()
    
    @classmethod
    async def get_pending(cls, db, approver_id: int = None) -> List["Approval"]:
        """Get pending approvals."""
        from sqlalchemy import select
        query = select(cls).where(cls.status == ApprovalStatus.PENDING)
        if approver_id:
            query = query.where(cls.approver_id == approver_id)
        result = await db.execute(query.order_by(cls.priority.desc(), cls.created_at.asc()))
        return result.scalars().all()
    
    @classmethod
    async def get_by_engagement(cls, db, engagement_id: int) -> List["Approval"]:
        """Get all approvals for an engagement."""
        from sqlalchemy import select
        result = await db.execute(
            select(cls).where(cls.engagement_id == engagement_id).order_by(cls.created_at.desc())
        )
        return result.scalars().all()
    
    async def save(self, db) -> "Approval":
        """Save the approval."""
        db.add(self)
        await db.commit()
        await db.refresh(self)
        return self
    
    async def approve(self, db, approver_id: int, notes: str = None) -> "Approval":
        """Approve the request."""
        self.status = ApprovalStatus.APPROVED
        self.approver_id = approver_id
        self.approved_at = datetime.utcnow()
        self.approval_notes = notes
        await db.commit()
        await db.refresh(self)
        return self
    
    async def deny(self, db, approver_id: int, reason: str) -> "Approval":
        """Deny the request."""
        self.status = ApprovalStatus.DENIED
        self.approver_id = approver_id
        self.denial_reason = reason
        await db.commit()
        await db.refresh(self)
        return self
    
    async def cancel(self, db) -> "Approval":
        """Cancel the request."""
        self.status = ApprovalStatus.CANCELLED
        await db.commit()
        await db.refresh(self)
        return self


class ReportType(str, PyEnum):
    """Types of reports."""
    EXECUTIVE_SUMMARY = "executive_summary"
    TECHNICAL_REPORT = "technical_report"
    PCI_DSS_ASSESSMENT = "pci_dss"
    SOC2_ASSESSMENT = "soc2"
    COMPLIANCE_REPORT = "compliance"
    CUSTOM = "custom"


class Report(Base, TimestampMixin):
    """Report model."""
    
    id = Column(Integer, primary_key=True, index=True)
    engagement_id = Column(Integer, ForeignKey("engagements.id"), nullable=False)
    
    # Report info
    title = Column(String(255), nullable=False)
    report_type = Column(Enum(ReportType), default=ReportType.TECHNICAL_REPORT, nullable=False)
    
    # Content
    summary = Column(Text, nullable=True)
    findings_summary = Column(JSON, default=[], nullable=True)
    methodology = Column(Text, nullable=True)
    recommendations = Column(Text, nullable=True)
    
    # Risk metrics
    critical_count = Column(Integer, default=0, nullable=False)
    high_count = Column(Integer, default=0, nullable=False)
    medium_count = Column(Integer, default=0, nullable=False)
    low_count = Column(Integer, default=0, nullable=False)
    info_count = Column(Integer, default=0, nullable=False)
    
    # Files
    file_path = Column(String(500), nullable=True)
    file_size = Column(Integer, nullable=True)
    mime_type = Column(String(100), nullable=True)
    template_used = Column(String(255), nullable=True)
    
    # Generation
    generated_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Status
    is_draft = Column(Boolean, default=True, nullable=False)
    is_final = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    engagement = relationship("Engagement", back_populates="reports")
    generated_by = relationship("User")
    
    # CRUD operations
    @classmethod
    async def get_by_id(cls, db, report_id: int) -> Optional["Report"]:
        """Get report by ID."""
        from sqlalchemy import select
        result = await db.execute(select(cls).where(cls.id == report_id))
        return result.scalar_one_or_none()
    
    @classmethod
    async def get_by_engagement(cls, db, engagement_id: int) -> List["Report"]:
        """Get all reports for an engagement."""
        from sqlalchemy import select
        result = await db.execute(
            select(cls).where(cls.engagement_id == engagement_id).order_by(cls.created_at.desc())
        )
        return result.scalars().all()
    
    @classmethod
    async def get_final_reports(cls, db, engagement_id: int) -> List["Report"]:
        """Get final reports for an engagement."""
        from sqlalchemy import select
        result = await db.execute(
            select(cls).where(
                cls.engagement_id == engagement_id,
                cls.is_final == True
            )
        )
        return result.scalars().all()
    
    async def save(self, db) -> "Report":
        """Save the report."""
        db.add(self)
        await db.commit()
        await db.refresh(self)
        return self
    
    async def update(self, db, **kwargs) -> "Report":
        """Update report fields."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        await db.commit()
        await db.refresh(self)
        return self
    
    async def finalize(self, db) -> "Report":
        """Mark report as final."""
        self.is_draft = False
        self.is_final = True
        await db.commit()
        await db.refresh(self)
        return self
