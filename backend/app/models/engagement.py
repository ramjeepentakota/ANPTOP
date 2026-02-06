"""
ANPTOP Backend - Engagement Model
"""

from datetime import datetime
from enum import Enum as PyEnum
from typing import List, Optional
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY
from app.db.base import Base, TimestampMixin


class EngagementStatus(str, PyEnum):
    """Engagement lifecycle status."""
    PLANNING = "planning"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class EngagementType(str, PyEnum):
    """Types of penetration tests."""
    EXTERNAL = "external"
    INTERNAL = "internal"
    WEB_APPLICATION = "web_application"
    MOBILE_APPLICATION = "mobile_application"
    API = "api"
    CLOUD = "cloud"
    SOCIAL_ENGINEERING = "social_engineering"
    PHYSICAL = "physical"
    RED_TEAM = "red_team"
    COMPLIANCE = "compliance"


class Engagement(Base, TimestampMixin):
    """Penetration testing engagement model."""
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic information
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    engagement_type = Column(Enum(EngagementType), default=EngagementType.EXTERNAL, nullable=False)
    status = Column(Enum(EngagementStatus), default=EngagementStatus.PLANNING, nullable=False)
    
    # Timeline
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    estimated_completion = Column(DateTime, nullable=True)
    
    # Scope
    target_scope = Column(ARRAY(String), default=[], nullable=False)
    blacklisted_ips = Column(ARRAY(String), default=[], nullable=False)
    rules_of_engagement = Column(Text, nullable=True)
    
    # Compliance standards
    compliance_standards = Column(ARRAY(String), default=[], nullable=False)  # PCI-DSS, SOC2, etc.
    
    # Client information
    client_name = Column(String(255), nullable=True)
    client_contact = Column(String(255), nullable=True)
    client_email = Column(String(255), nullable=True)
    
    # Team
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    team_members = Column(ARRAY(Integer), default=[], nullable=False)  # User IDs
    
    # Settings
    is_api_access_enabled = Column(Boolean, default=False, nullable=False)
    auto_approve_workflows = Column(Boolean, default=False, nullable=False)
    require_evidence = Column(Boolean, default=True, nullable=False)
    
    # Metadata
    engagement_metadata = Column(JSON, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    owner = relationship("User", back_populates="engagements", foreign_keys=[owner_id])
    targets = relationship("Target", back_populates="engagement", cascade="all, delete-orphan")
    findings = relationship("Finding", back_populates="engagement", cascade="all, delete-orphan")
    workflow_executions = relationship("WorkflowExecution", back_populates="engagement", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="engagement", cascade="all, delete-orphan")
    approvals = relationship("Approval", back_populates="engagement", cascade="all, delete-orphan")
    
    # New relationships for fintech features
    cloud_findings = relationship("CloudFinding", back_populates="engagement", cascade="all, delete-orphan")
    cloud_assets = relationship("CloudAsset", back_populates="engagement", cascade="all, delete-orphan")
    kubernetes_clusters = relationship("KubernetesCluster", back_populates="engagement", cascade="all, delete-orphan")
    kubernetes_findings = relationship("KubernetesFinding", back_populates="engagement", cascade="all, delete-orphan")
    kubernetes_pods = relationship("KubernetesPod", back_populates="engagement", cascade="all, delete-orphan")
    payment_gateways = relationship("PaymentGateway", back_populates="engagement", cascade="all, delete-orphan")
    payment_findings = relationship("PaymentFinding", back_populates="engagement", cascade="all, delete-orphan")
    pci_scan_results = relationship("PCIScanResult", back_populates="engagement", cascade="all, delete-orphan")
    card_exposures = relationship("CardDataExposure", back_populates="engagement", cascade="all, delete-orphan")
    phishing_campaigns = relationship("PhishingCampaign", back_populates="engagement", cascade="all, delete-orphan")
    social_engineering_findings = relationship("SocialEngineeringFinding", back_populates="engagement", cascade="all, delete-orphan")
    
    # CRUD operations
    @classmethod
    async def get_by_id(cls, db, engagement_id: int) -> Optional["Engagement"]:
        """Get engagement by ID."""
        from sqlalchemy import select
        result = await db.execute(select(cls).where(cls.id == engagement_id))
        return result.scalar_one_or_none()
    
    @classmethod
    async def get_all(cls, db, skip: int = 0, limit: int = 100, status: str = None) -> List["Engagement"]:
        """Get all engagements with optional status filter."""
        from sqlalchemy import select
        query = select(cls).offset(skip).limit(limit)
        if status:
            query = query.where(cls.status == status)
        result = await db.execute(query)
        return result.scalars().all()
    
    @classmethod
    async def get_by_owner(cls, db, owner_id: int, skip: int = 0, limit: int = 100) -> List["Engagement"]:
        """Get engagements by owner ID."""
        from sqlalchemy import select
        result = await db.execute(
            select(cls).where(cls.owner_id == owner_id).offset(skip).limit(limit)
        )
        return result.scalars().all()
    
    async def save(self, db) -> "Engagement":
        """Save the engagement."""
        db.add(self)
        await db.commit()
        await db.refresh(self)
        return self
    
    async def update(self, db, **kwargs) -> "Engagement":
        """Update engagement fields."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        await db.commit()
        await db.refresh(self)
        return self
    
    async def add_target(self, db, target) -> None:
        """Add a target to the engagement."""
        target.engagement_id = self.id
        db.add(target)
        await db.commit()
    
    async def add_finding(self, db, finding) -> None:
        """Add a finding to the engagement."""
        finding.engagement_id = self.id
        db.add(finding)
        await db.commit()
    
    def is_target_in_scope(self, target_ip: str) -> bool:
        """Check if a target IP is within the engagement scope."""
        if target_ip in self.blacklisted_ips:
            return False
        
        for scope_pattern in self.target_scope:
            if target_ip == scope_pattern or target_ip.startswith(scope_pattern.rstrip("*")):
                return True
        
        return False
