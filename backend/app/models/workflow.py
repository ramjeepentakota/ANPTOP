"""
ANPTOP Backend - Workflow Model
"""

from datetime import datetime
from enum import Enum as PyEnum
from typing import List, Optional
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from app.db.base import Base, TimestampMixin


class WorkflowType(str, PyEnum):
    """Types of workflows."""
    DISCOVERY = "discovery"
    SCANNING = "scanning"
    VULNERABILITY_ASSESSMENT = "vulnerability_assessment"
    EXPLOITATION = "exploitation"
    POST_EXPLOITATION = "post_exploitation"
    LATERAL_MOVEMENT = "lateral_movement"
    EVIDENCE_COLLECTION = "evidence_collection"
    REPORTING = "reporting"
    CLOUD_DISCOVERY = "cloud_discovery"
    CLOUD_EXPLOITATION = "cloud_exploitation"
    KUBERNETES_ASSESSMENT = "kubernetes_assessment"
    API_SECURITY = "api_security"
    PAYMENT_ASSESSMENT = "payment_assessment"


class WorkflowStatus(str, PyEnum):
    """Workflow execution status."""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    APPROVAL_REQUIRED = "approval_required"
    APPROVED = "approved"
    DENIED = "denied"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class Workflow(Base, TimestampMixin):
    """Workflow definition model."""
    
    id = Column(Integer, primary_key=True, index=True)
    n8n_workflow_id = Column(String(255), nullable=True)  # n8n workflow ID
    
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    workflow_type = Column(Enum(WorkflowType), nullable=False)
    
    # Configuration
    parameters = Column(JSON, default={}, nullable=True)
    tool_configurations = Column(JSON, default={}, nullable=True)
    scan_settings = Column(JSON, default={}, nullable=True)
    
    # Requirements
    requires_approval = Column(Boolean, default=False, nullable=False)
    approval_role = Column(String(50), default="lead", nullable=False)
    
    # Limits
    timeout_minutes = Column(Integer, default=60, nullable=False)
    max_retries = Column(Integer, default=3, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_template = Column(Boolean, default=False, nullable=False)
    
    # Metadata
    tags = Column(JSON, default=[], nullable=True)
    category = Column(String(100), nullable=True)
    
    # Relationships
    executions = relationship("WorkflowExecution", back_populates="workflow", cascade="all, delete-orphan")
    
    # CRUD operations
    @classmethod
    async def get_by_id(cls, db, workflow_id: int) -> Optional["Workflow"]:
        """Get workflow by ID."""
        from sqlalchemy import select
        result = await db.execute(select(cls).where(cls.id == workflow_id))
        return result.scalar_one_or_none()
    
    @classmethod
    async def get_by_type(cls, db, workflow_type: WorkflowType) -> List["Workflow"]:
        """Get all workflows of a specific type."""
        from sqlalchemy import select
        result = await db.execute(select(cls).where(cls.workflow_type == workflow_type))
        return result.scalars().all()
    
    @classmethod
    async def get_all(cls, db, skip: int = 0, limit: int = 100) -> List["Workflow"]:
        """Get all workflows."""
        from sqlalchemy import select
        result = await db.execute(select(cls).offset(skip).limit(limit))
        return result.scalars().all()
    
    @classmethod
    async def get_active(cls, db) -> List["Workflow"]:
        """Get all active workflows."""
        from sqlalchemy import select
        result = await db.execute(select(cls).where(cls.is_active == True))
        return result.scalars().all()
    
    async def save(self, db) -> "Workflow":
        """Save the workflow."""
        db.add(self)
        await db.commit()
        await db.refresh(self)
        return self
    
    async def update(self, db, **kwargs) -> "Workflow":
        """Update workflow fields."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        await db.commit()
        await db.refresh(self)
        return self


class WorkflowExecution(Base, TimestampMixin):
    """Workflow execution tracking model."""
    
    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=False)
    engagement_id = Column(Integer, ForeignKey("engagements.id"), nullable=False)
    target_id = Column(Integer, ForeignKey("targets.id"), nullable=True)
    
    # Execution info
    executed_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(Enum(WorkflowStatus), default=WorkflowStatus.PENDING, nullable=False)
    
    # Timing
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    estimated_completion = Column(DateTime, nullable=True)
    
    # Parameters used
    parameters = Column(JSON, default={}, nullable=True)
    
    # Results
    results = Column(JSON, default={}, nullable=True)
    findings = Column(JSON, default=[], nullable=True)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    
    # Evidence
    evidence_collected = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    workflow = relationship("Workflow", back_populates="executions")
    engagement = relationship("Engagement", back_populates="workflow_executions")
    executed_by = relationship("User", back_populates="workflow_executions")
    evidence_items = relationship("Evidence", back_populates="workflow_execution")
    
    # CRUD operations
    @classmethod
    async def get_by_id(cls, db, execution_id: int) -> Optional["WorkflowExecution"]:
        """Get execution by ID."""
        from sqlalchemy import select
        result = await db.execute(select(cls).where(cls.id == execution_id))
        return result.scalar_one_or_none()
    
    @classmethod
    async def get_by_engagement(cls, db, engagement_id: int, skip: int = 0, limit: int = 100) -> List["WorkflowExecution"]:
        """Get all executions for an engagement."""
        from sqlalchemy import select
        result = await db.execute(
            select(cls).where(cls.engagement_id == engagement_id).offset(skip).limit(limit)
        )
        return result.scalars().all()
    
    @classmethod
    async def get_pending_approvals(cls, db, required_role: str) -> List["WorkflowExecution"]:
        """Get all executions awaiting approval for a specific role."""
        from sqlalchemy import select
        result = await db.execute(
            select(cls).where(
                cls.status == WorkflowStatus.APPROVAL_REQUIRED
            )
        )
        return result.scalars().all()
    
    async def save(self, db) -> "WorkflowExecution":
        """Save the execution."""
        db.add(self)
        await db.commit()
        await db.refresh(self)
        return self
    
    async def start(self, db) -> "WorkflowExecution":
        """Mark execution as started."""
        self.started_at = datetime.utcnow()
        self.status = WorkflowStatus.RUNNING
        await db.commit()
        await db.refresh(self)
        return self
    
    async def complete(self, db, results: dict) -> "WorkflowExecution":
        """Mark execution as completed."""
        self.completed_at = datetime.utcnow()
        self.status = WorkflowStatus.COMPLETED
        self.results = results
        await db.commit()
        await db.refresh(self)
        return self
    
    async def fail(self, db, error_message: str) -> "WorkflowExecution":
        """Mark execution as failed."""
        self.completed_at = datetime.utcnow()
        self.status = WorkflowStatus.FAILED
        self.error_message = error_message
        await db.commit()
        await db.refresh(self)
        return self
    
    async def approve(self, db) -> "WorkflowExecution":
        """Approve the execution."""
        self.status = WorkflowStatus.APPROVED
        await db.commit()
        await db.refresh(self)
        return self
    
    async def deny(self, db, reason: str) -> "WorkflowExecution":
        """Deny the execution."""
        self.status = WorkflowStatus.DENIED
        self.error_message = reason
        await db.commit()
        await db.refresh(self)
        return self
