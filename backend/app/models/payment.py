"""
ANPTOP Backend - Payment Systems Security Models
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship

from app.db.base import Base


class PaymentGateway(Base):
    """Payment gateway configuration."""
    
    id = Column(Integer, primary_key=True, index=True)
    engagement_id = Column(Integer, ForeignKey("engagements.id"), nullable=False)
    
    # Gateway identification
    name = Column(String(100), nullable=False)  # Stripe, PayPal, Braintree, Square, etc.
    gateway_type = Column(String(50), nullable=False)  # stripe, paypal, braintree, square, custom
    
    # Configuration
    api_endpoint = Column(String(500), nullable=True)
    api_version = Column(String(20), nullable=True)
    
    # Access credentials
    api_key_hash = Column(String(500), nullable=True)
    secret_key_hash = Column(String(500), nullable=True)
    webhook_secret = Column(String(500), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    last_tested = Column(DateTime, nullable=True)
    
    # Relationships
    engagement = relationship("Engagement", back_populates="payment_gateways")
    
    def __repr__(self):
        return f"<PaymentGateway {self.name}>"


class PaymentFinding(Base):
    """Payment security finding model."""
    
    id = Column(Integer, primary_key=True, index=True)
    engagement_id = Column(Integer, ForeignKey("engagements.id"), nullable=False)
    
    # Payment system type
    payment_component = Column(String(100), nullable=False)  # gateway, processor, storage, encryption, tokenization
    gateway_name = Column(String(100), nullable=True)
    
    # Finding categorization
    finding_type = Column(String(100), nullable=False)  # 
    severity = Column(String(20), nullable=False)  # CRITICAL, HIGH, MEDIUM, LOW
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    
    # Affected component
    target = Column(String(500), nullable=True)
    target_type = Column(String(100), nullable=True)  # api_endpoint, database, filesystem, memory
    
    # PCI-DSS related
    pci_requirement = Column(String(50), nullable=True)  # 1.x, 2.x, 3.x, etc.
    pci_control = Column(String(100), nullable=True)  # Specific PCI control ID
    compliance_status = Column(String(20), nullable=True)  # compliant, non_compliant, not_applicable
    
    # Technical details
    vulnerability_class = Column(String(100), nullable=True)  # injection, exposure, weak_encryption, etc.
    cvss_score = Column(Float, nullable=True)
    cvss_vector = Column(String(100), nullable=True)
    
    # Evidence
    evidence = Column(JSON, nullable=True)
    transaction_logs = Column(JSON, nullable=True)
    screenshots = Column(JSON, nullable=True)
    curl_poc = Column(Text, nullable=True)  # Proof of concept curl command
    
    # Remediation
    remediation = Column(Text, nullable=True)
    remediation_steps = Column(JSON, nullable=True)
    priority_fix = Column(Boolean, default=False)  # Must fix for PCI compliance
    
    # Status
    status = Column(String(20), default="open")
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Timestamps
    discovered_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    engagement = relationship("Engagement", back_populates="payment_findings")
    
    def __repr__(self):
        return f"<PaymentFinding {self.finding_type}:{self.severity}>"


class PCIScanResult(Base):
    """PCI-DSS compliance scan results."""
    
    id = Column(Integer, primary_key=True, index=True)
    engagement_id = Column(Integer, ForeignKey("engagements.id"), nullable=False)
    
    # Scan details
    scan_target = Column(String(500), nullable=False)
    scan_type = Column(String(100), nullable=False)  # network_scan, configuration_scan, log_analysis
    
    # Compliance status
    overall_compliance = Column(Boolean, default=False)
    compliance_score = Column(Integer, nullable=True)  # 0-100
    
    # PCI requirements
    scanned_requirements = Column(JSON, nullable=True)  # List of requirement IDs
    passed_requirements = Column(JSON, nullable=True)
    failed_requirements = Column(JSON, nullable=True)
    
    # Detailed results
    requirement_details = Column(JSON, nullable=True)
    
    # Scan tool
    scan_tool = Column(String(100), nullable=True)  # Nessus, OpenVAS, Qualys, etc.
    scan_duration_seconds = Column(Integer, nullable=True)
    
    # Timestamps
    scanned_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    engagement = relationship("Engagement", back_populates="pci_scan_results")
    
    def __repr__(self):
        return f"<PCIScanResult {self.engagement_id}:{self.overall_compliance}>"


class CardDataExposure(Base):
    """Card data exposure tracking."""
    
    id = Column(Integer, primary_key=True, index=True)
    engagement_id = Column(Integer, ForeignKey("engagements.id"), nullable=False)
    
    # Exposure type
    exposure_type = Column(String(100), nullable=False)  # pan_exposure, cvv_exposure, track_data, etc.
    
    # Location
    target = Column(String(500), nullable=False)
    storage_location = Column(String(200), nullable=True)  # database, file_system, memory, log
    
    # Details
    data_format = Column(String(100), nullable=True)  # plaintext, hashed, encrypted, truncated
    encryption_type = Column(String(100), nullable=True)  # AES-256, RSA, etc.
    
    # Evidence
    sample_data_hash = Column(String(200), nullable=True)  # Hash of sample (not actual PAN)
    detection_method = Column(String(200), nullable=True)
    
    # Risk assessment
    risk_level = Column(String(20), nullable=False)  # CRITICAL, HIGH, MEDIUM, LOW
    compensating_controls = Column(JSON, nullable=True)
    
    # Timestamps
    discovered_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    engagement = relationship("Engagement", back_populates="card_exposures")
    
    def __repr__(self):
        return f"<CardDataExposure {self.exposure_type}:{self.risk_level}>"
