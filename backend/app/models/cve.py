"""
ANPTOP Backend - CVE Database Model
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship

from app.db.base import Base


class CVE(Base):
    """CVE database entry model."""
    
    id = Column(Integer, primary_key=True, index=True)
    cve_id = Column(String(20), unique=True, index=True, nullable=False)  # CVE-YYYY-NNNNN
    description = Column(Text, nullable=True)
    severity = Column(String(20), nullable=True)  # CRITICAL, HIGH, MEDIUM, LOW
    cvss_score = Column(Float, nullable=True)
    cvss_vector = Column(String(100), nullable=True)
    published_date = Column(DateTime, nullable=True)
    modified_date = Column(DateTime, nullable=True)
    
    # CPE information
    cpe_match = Column(JSON, nullable=True)  # List of affected CPEs
    
    # References
    references = Column(JSON, nullable=True)  # List of reference URLs
    
    # Technical details
    attack_vector = Column(String(50), nullable=True)  # NETWORK, ADJACENT_NETWORK, LOCAL, PHYSICAL
    attack_complexity = Column(String(50), nullable=True)  # LOW, HIGH
    privileges_required = Column(String(50), nullable=True)  # NONE, LOW, HIGH
    user_interaction = Column(String(50), nullable=True)  # NONE, REQUIRED
    scope = Column(String(50), nullable=True)  # UNCHANGED, CHANGED
    confidentiality = Column(String(50), nullable=True)  # HIGH, LOW, NONE
    integrity = Column(String(50), nullable=True)  # HIGH, LOW, NONE
    availability = Column(String(50), nullable=True)  # HIGH, LOW, NONE
    
    # Related vulnerabilities
    cwe_id = Column(String(20), nullable=True)  # CWE-ID
    cwe_name = Column(String(200), nullable=True)
    
    # Fintech-specific
    fintech_impact = Column(String(100), nullable=True)  # payment_systems, blockchain, banking, etc.
    compliance_impact = Column(JSON, nullable=True)  # PCI-DSS, SOC2, etc. requirements
    
    # Metadata
    source = Column(String(50), default="NVD")  # NVD, MITRE, CUSTOM
    last_synced = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    findings = relationship("Vulnerability", back_populates="cve_reference")
    
    def __repr__(self):
        return f"<CVE {self.cve_id}>"


class CVEKeystones(Base):
    """Keystone list mapping CVEs to specific technologies/frameworks."""
    
    id = Column(Integer, primary_key=True, index=True)
    cve_id = Column(String(20), ForeignKey("cves.cve_id"), nullable=False)
    technology = Column(String(100), nullable=False)  # e.g., "Spring Boot", "Apache Struts"
    version_range = Column(String(50), nullable=True)  # e.g., "2.0.0-2.5.0"
    is_keystone = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<CVEKeystones {self.cve_id}:{self.technology}>"
