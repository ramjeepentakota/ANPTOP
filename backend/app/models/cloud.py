"""
ANPTOP Backend - Cloud Security Models
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship

from app.db.base import Base


class CloudProvider(Base):
    """Cloud provider enumeration."""
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)  # AWS, Azure, GCP
    account_id = Column(String(100), nullable=True)
    account_name = Column(String(200), nullable=True)
    organization = Column(String(200), nullable=True)
    region = Column(String(50), nullable=True)
    
    # Access credentials (encrypted in production)
    access_key_id = Column(String(200), nullable=True)
    is_active = Column(Boolean, default=True)
    last_checked = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<CloudProvider {self.name}:{self.account_id}>"


class CloudFinding(Base):
    """Cloud security finding model."""
    
    id = Column(Integer, primary_key=True, index=True)
    engagement_id = Column(Integer, ForeignKey("engagements.id"), nullable=False)
    
    # Provider details
    provider = Column(String(20), nullable=False)  # AWS, Azure, GCP
    service = Column(String(100), nullable=True)  # S3, EC2, Lambda, RDS, etc.
    region = Column(String(50), nullable=True)
    
    # Finding details
    resource_id = Column(String(500), nullable=True)
    resource_name = Column(String(500), nullable=True)
    resource_type = Column(String(100), nullable=True)
    
    finding_type = Column(String(100), nullable=False)  # misconfiguration, exposed, vulnerable, etc.
    severity = Column(String(20), nullable=False)  # CRITICAL, HIGH, MEDIUM, LOW
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    
    # AWS-specific fields
    aws_service = Column(String(50), nullable=True)
    aws_finding_id = Column(String(100), nullable=True)  # GuardDuty finding ID
    aws_compliance_check = Column(String(100), nullable=True)  # CIS, PCI-DSS, etc.
    
    # Azure-specific fields
    azure_subscription_id = Column(String(100), nullable=True)
    azure_resource_group = Column(String(200), nullable=True)
    azure_policy_id = Column(String(100), nullable=True)
    
    # GCP-specific fields
    gcp_project_id = Column(String(100), nullable=True)
    gcp_resource_type = Column(String(100), nullable=True)
    
    # Remediation
    remediation = Column(Text, nullable=True)
    remediation_url = Column(String(500), nullable=True)
    
    # Evidence
    evidence = Column(JSON, nullable=True)
    screenshots = Column(JSON, nullable=True)  # List of screenshot URLs
    logs = Column(Text, nullable=True)
    
    # Compliance
    compliance_frameworks = Column(JSON, nullable=True)  # CIS, PCI-DSS, SOC2, HIPAA
    compliance_requirements = Column(JSON, nullable=True)
    
    # Status
    status = Column(String(20), default="open")  # open, in_progress, resolved, accepted
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Timestamps
    discovered_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    engagement = relationship("Engagement", back_populates="cloud_findings")
    
    def __repr__(self):
        return f"<CloudFinding {self.provider}:{self.finding_type}:{self.severity}>"


class CloudAsset(Base):
    """Cloud asset inventory."""
    
    id = Column(Integer, primary_key=True, index=True)
    engagement_id = Column(Integer, ForeignKey("engagements.id"), nullable=False)
    
    provider = Column(String(20), nullable=False)
    service = Column(String(100), nullable=False)
    resource_id = Column(String(500), nullable=False)
    resource_name = Column(String(500), nullable=True)
    resource_type = Column(String(100), nullable=True)
    
    # Resource details
    arn = Column(String(500), nullable=True)
    region = Column(String(50), nullable=True)
    tags = Column(JSON, nullable=True)
    
    # Security status
    is_public = Column(Boolean, default=False)
    is_exposed = Column(Boolean, default=False)
    security_score = Column(Integer, nullable=True)
    
    # Discovery method
    discovery_tool = Column(String(100), nullable=True)  # Pacu, ScoutSuite, AWS CLI, etc.
    discovered_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    engagement = relationship("Engagement", back_populates="cloud_assets")
    
    def __repr__(self):
        return f"<CloudAsset {self.provider}:{self.service}:{self.resource_id}>"
