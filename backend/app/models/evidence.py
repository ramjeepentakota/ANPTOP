"""
ANPTOP Backend - Evidence and Audit Models
"""

from datetime import datetime
from enum import Enum as PyEnum
from typing import List, Optional
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey, JSON, LargeBinary, Boolean
from sqlalchemy.orm import relationship
from app.db.base import Base, TimestampMixin


class EvidenceType(str, PyEnum):
    """Types of evidence."""
    SCREENSHOT = "screenshot"
    PCAP = "pcap"
    LOG = "log"
    CONFIG = "config"
    SCRIPT = "script"
    REPORT = "report"
    JSON_OUTPUT = "json_output"
    XML_OUTPUT = "xml_output"
    BINARY = "binary"
    DOCUMENT = "document"
    IMAGE = "image"
    COMMAND_OUTPUT = "command_output"
    METASPLOIT_DATA = "metasploit_data"
    DATABASE_DUMP = "database_dump"
    CREDENTIAL = "credential"
    HASH = "hash"


class EvidenceChainOfCustody(Base, TimestampMixin):
    """Chain of custody tracking for evidence."""
    
    id = Column(Integer, primary_key=True, index=True)
    evidence_id = Column(Integer, ForeignKey("evidence.id"), nullable=False)
    
    action = Column(String(255), nullable=False)  # collected, transferred, viewed, exported, deleted
    action_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    action_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    location = Column(String(500), nullable=True)  # File path, URL, etc.
    notes = Column(Text, nullable=True)
    hash_value = Column(String(255), nullable=True)  # SHA-256 hash at time of action
    
    # Relationships
    evidence = relationship("Evidence", back_populates="chain_of_custody")


class Evidence(Base, TimestampMixin):
    """Evidence model for collected artifacts."""
    
    id = Column(Integer, primary_key=True, index=True)
    engagement_id = Column(Integer, ForeignKey("engagements.id"), nullable=False)
    target_id = Column(Integer, ForeignKey("targets.id"), nullable=True)
    workflow_execution_id = Column(Integer, ForeignKey("workflow_executions.id"), nullable=True)
    vulnerability_id = Column(Integer, ForeignKey("vulnerabilities.id"), nullable=True)
    
    # Identification
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=True)
    evidence_type = Column(Enum(EvidenceType), nullable=False)
    
    # Storage
    storage_backend = Column(String(50), default="local", nullable=False)  # local, s3, minio
    storage_path = Column(String(500), nullable=True)
    file_size = Column(Integer, nullable=True)
    mime_type = Column(String(100), nullable=True)
    
    # Hashes for integrity
    sha256_hash = Column(String(255), nullable=True)
    md5_hash = Column(String(255), nullable=True)
    
    # Description
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Metadata
    collected_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    collected_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    tool_used = Column(String(255), nullable=True)
    command_executed = Column(Text, nullable=True)
    
    # Classification
    confidentiality_level = Column(String(50), default="internal", nullable=False)  # public, internal, confidential, restricted
    retention_date = Column(DateTime, nullable=True)
    
    # Chain of custody
    chain_of_custody = relationship("EvidenceChainOfCustody", back_populates="evidence", cascade="all, delete-orphan")
    
    # Relationships
    engagement = relationship("Engagement", back_populates="evidence")
    target = relationship("Target", back_populates="evidence")
    workflow_execution = relationship("WorkflowExecution", back_populates="evidence_items")
    vulnerability = relationship("Vulnerability", back_populates="evidence")
    collector = relationship("User", foreign_keys=[collected_by])
    
    # CRUD operations
    @classmethod
    async def get_by_id(cls, db, evidence_id: int) -> Optional["Evidence"]:
        """Get evidence by ID."""
        from sqlalchemy import select
        result = await db.execute(select(cls).where(cls.id == evidence_id))
        return result.scalar_one_or_none()
    
    @classmethod
    async def get_by_engagement(cls, db, engagement_id: int, skip: int = 0, limit: int = 100) -> List["Evidence"]:
        """Get all evidence for an engagement."""
        from sqlalchemy import select
        result = await db.execute(
            select(cls).where(cls.engagement_id == engagement_id).offset(skip).limit(limit)
        )
        return result.scalars().all()
    
    @classmethod
    async def get_by_target(cls, db, target_id: int) -> List["Evidence"]:
        """Get all evidence for a target."""
        from sqlalchemy import select
        result = await db.execute(select(cls).where(cls.target_id == target_id))
        return result.scalars().all()
    
    async def save(self, db) -> "Evidence":
        """Save the evidence."""
        db.add(self)
        await db.commit()
        await db.refresh(self)
        return self
    
    async def update(self, db, **kwargs) -> "Evidence":
        """Update evidence fields."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        await db.commit()
        await db.refresh(self)
        return self
    
    async def add_custody_record(self, db, action: str, user_id: int, notes: str = None) -> None:
        """Add a chain of custody record."""
        custody = EvidenceChainOfCustody(
            evidence_id=self.id,
            action=action,
            action_by=user_id,
            hash_value=self.sha256_hash,
            notes=notes,
        )
        db.add(custody)
        await db.commit()


class AuditLog(Base):
    """Audit log model for tracking all actions."""
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Action info
    action = Column(String(255), nullable=False)
    resource = Column(String(255), nullable=True)
    resource_id = Column(String(255), nullable=True)
    
    # Details
    details = Column(JSON, default={}, nullable=True)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    # Timing
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Status
    success = Column(Boolean, default=True, nullable=False)
    error_message = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    
    @classmethod
    async def get_by_id(cls, db, log_id: int) -> Optional["AuditLog"]:
        """Get audit log by ID."""
        from sqlalchemy import select
        result = await db.execute(select(cls).where(cls.id == log_id))
        return result.scalar_one_or_none()
    
    @classmethod
    async def get_by_user(cls, db, user_id: int, skip: int = 0, limit: int = 100) -> List["AuditLog"]:
        """Get audit logs for a user."""
        from sqlalchemy import select
        result = await db.execute(
            select(cls).where(cls.user_id == user_id).order_by(cls.timestamp.desc()).offset(skip).limit(limit)
        )
        return result.scalars().all()
    
    @classmethod
    async def get_by_resource(cls, db, resource: str, resource_id: str = None) -> List["AuditLog"]:
        """Get audit logs for a specific resource."""
        from sqlalchemy import select
        query = select(cls).where(cls.resource == resource)
        if resource_id:
            query = query.where(cls.resource_id == resource_id)
        result = await db.execute(query.order_by(cls.timestamp.desc()))
        return result.scalars().all()
    
    async def save(self, db) -> "AuditLog":
        """Save the audit log."""
        db.add(self)
        await db.commit()
        return self
