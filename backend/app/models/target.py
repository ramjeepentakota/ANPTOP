"""
ANPTOP Backend - Target Model
"""

from datetime import datetime
from enum import Enum as PyEnum
from typing import List, Optional
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY
from app.db.base import Base, TimestampMixin


class TargetType(str, PyEnum):
    """Types of targets."""
    HOST = "host"
    IP_RANGE = "ip_range"
    DOMAIN = "domain"
    SUBNET = "subnet"
    URL = "url"
    WEB_APPLICATION = "web_application"
    API = "api"
    CLOUD_AWS = "cloud_aws"
    CLOUD_AZURE = "cloud_azure"
    CLOUD_GCP = "cloud_gcp"
    KUBERNETES = "kubernetes"
    DATABASE = "database"
    NETWORK_DEVICE = "network_device"


class TargetStatus(str, PyEnum):
    """Target discovery/exploitation status."""
    PENDING = "pending"
    DISCOVERED = "discovered"
    SCANNED = "scanned"
    VULNERABLE = "vulnerable"
    EXPLOITED = "exploited"
    CONFIRMED = "confirmed"
    FALSE_POSITIVE = "false_positive"
    OUT_OF_SCOPE = "out_of_scope"


class Target(Base, TimestampMixin):
    """Target model for engagement targets."""
    
    id = Column(Integer, primary_key=True, index=True)
    engagement_id = Column(Integer, ForeignKey("engagements.id"), nullable=False)
    
    # Identification
    identifier = Column(String(255), nullable=False)  # IP, domain, URL, etc.
    target_type = Column(Enum(TargetType), default=TargetType.HOST, nullable=False)
    
    # Discovery info
    hostname = Column(String(255), nullable=True)
    operating_system = Column(String(255), nullable=True)
    mac_address = Column(String(50), nullable=True)
    
    # Network info
    ports = Column(ARRAY(Integer), default=[], nullable=False)
    services = Column(JSON, default=[], nullable=True)
    protocols = Column(ARRAY(String), default=["tcp"], nullable=False)
    
    # Status
    status = Column(Enum(TargetStatus), default=TargetStatus.PENDING, nullable=False)
    is_alive = Column(Boolean, default=False, nullable=False)
    is_in_scope = Column(Boolean, default=True, nullable=False)
    
    # Cloud-specific (if applicable)
    cloud_provider = Column(String(50), nullable=True)
    cloud_account_id = Column(String(255), nullable=True)
    cloud_region = Column(String(100), nullable=True)
    cloud_resource_id = Column(String(255), nullable=True)
    
    # Web app specific
    web_framework = Column(String(100), nullable=True)
    technologies = Column(ARRAY(String), default=[], nullable=False)
    directories = Column(ARRAY(String), default=[], nullable=False)
    
    # K8s specific
    kubernetes_cluster = Column(String(255), nullable=True)
    kubernetes_namespace = Column(String(100), nullable=True)
    kubernetes_pod = Column(String(255), nullable=True)
    
    # Scanning results
    scan_results = Column(JSON, default={}, nullable=True)
    vulnerabilities = Column(JSON, default=[], nullable=True)
    
    # Metadata
    target_metadata = Column(JSON, nullable=True)
    notes = Column(Text, nullable=True)
    tags = Column(ARRAY(String), default=[], nullable=False)
    
    # Relationships
    engagement = relationship("Engagement", back_populates="targets")
    services_rel = relationship("TargetService", back_populates="target", cascade="all, delete-orphan")
    vulnerabilities_rel = relationship("Vulnerability", back_populates="target", cascade="all, delete-orphan")
    evidence = relationship("Evidence", back_populates="target", cascade="all, delete-orphan")
    
    # CRUD operations
    @classmethod
    async def get_by_id(cls, db, target_id: int) -> Optional["Target"]:
        """Get target by ID."""
        from sqlalchemy import select
        result = await db.execute(select(cls).where(cls.id == target_id))
        return result.scalar_one_or_none()
    
    @classmethod
    async def get_by_engagement(cls, db, engagement_id: int, skip: int = 0, limit: int = 100) -> List["Target"]:
        """Get all targets for an engagement."""
        from sqlalchemy import select
        result = await db.execute(
            select(cls).where(cls.engagement_id == engagement_id).offset(skip).limit(limit)
        )
        return result.scalars().all()
    
    @classmethod
    async def get_by_identifier(cls, db, identifier: str) -> Optional["Target"]:
        """Get target by identifier (IP, domain, etc.)."""
        from sqlalchemy import select
        result = await db.execute(select(cls).where(cls.identifier == identifier))
        return result.scalar_one_or_none()
    
    async def save(self, db) -> "Target":
        """Save the target."""
        db.add(self)
        await db.commit()
        await db.refresh(self)
        return self
    
    async def update(self, db, **kwargs) -> "Target":
        """Update target fields."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        await db.commit()
        await db.refresh(self)
        return self
    
    def add_vulnerability(self, vulnerability_data: dict) -> None:
        """Add a vulnerability to the target."""
        vulnerabilities = self.vulnerabilities or []
        vulnerabilities.append(vulnerability_data)
        self.vulnerabilities = vulnerabilities
    
    def get_ports_with_services(self) -> dict:
        """Get a mapping of ports to services."""
        return {service.get("port"): service for service in self.services or []}


class TargetService(Base):
    """Service running on a target."""
    
    id = Column(Integer, primary_key=True, index=True)
    target_id = Column(Integer, ForeignKey("targets.id"), nullable=False)
    
    port = Column(Integer, nullable=False)
    protocol = Column(String(10), default="tcp", nullable=False)
    name = Column(String(100), nullable=True)
    version = Column(String(100), nullable=True)
    product = Column(String(255), nullable=True)
    banner = Column(Text, nullable=True)
    tls_version = Column(String(50), nullable=True)
    cves = Column(ARRAY(String), default=[], nullable=False)
    
    # Relationships
    target = relationship("Target", back_populates="services_rel")
    
    @classmethod
    async def get_by_target(cls, db, target_id: int) -> List["TargetService"]:
        """Get all services for a target."""
        from sqlalchemy import select
        result = await db.execute(select(cls).where(cls.target_id == target_id))
        return result.scalars().all()
