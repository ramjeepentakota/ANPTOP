"""
ANPTOP Backend - Social Engineering Models
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship

from app.db.base import Base


class PhishingCampaign(Base):
    """Phishing campaign management."""
    
    id = Column(Integer, primary_key=True, index=True)
    engagement_id = Column(Integer, ForeignKey("engagements.id"), nullable=False)
    
    # Campaign details
    campaign_name = Column(String(200), nullable=False)
    campaign_type = Column(String(50), nullable=False)  # email, sms, voice
    template_id = Column(Integer, nullable=True)  # Reference to template
    
    # Target information
    target_list_id = Column(Integer, nullable=True)  # Reference to target list
    target_count = Column(Integer, default=0)
    target_emails = Column(JSON, nullable=True)  # List of email addresses
    target_phones = Column(JSON, nullable=True)  # List of phone numbers
    
    # Sender configuration
    sender_name = Column(String(200), nullable=True)
    sender_email = Column(String(200), nullable=True)
    reply_to = Column(String(200), nullable=True)
    
    # Email content
    subject_template = Column(String(500), nullable=True)
    body_template = Column(Text, nullable=True)
    html_content = Column(Text, nullable=True)
    
    # Landing page
    landing_page_url = Column(String(500), nullable=True)
    landing_page_id = Column(Integer, nullable=True)
    
    # Status
    status = Column(String(20), default="draft")  # draft, scheduled, running, paused, completed
    scheduled_at = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Statistics
    sent_count = Column(Integer, default=0)
    opened_count = Column(Integer, default=0)
    clicked_count = Column(Integer, default=0)
    submitted_count = Column(Integer, default=0)
    reported_count = Column(Integer, default=0)
    
    # Created by
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    engagement = relationship("Engagement", back_populates="phishing_campaigns")
    results = relationship("PhishingResult", back_populates="campaign", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<PhishingCampaign {self.campaign_name}:{self.status}>"


class PhishingResult(Base):
    """Individual phishing campaign result."""
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("phishing_campaigns.id"), nullable=False)
    
    # Target information
    target_email = Column(String(200), nullable=True)
    target_phone = Column(String(50), nullable=True)
    target_name = Column(String(200), nullable=True)
    
    # Event tracking
    event_type = Column(String(50), nullable=False)  # sent, delivered, opened, clicked, submitted, reported
    event_timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Technical details
    user_agent = Column(String(500), nullable=True)
    ip_address = Column(String(50), nullable=True)
    geo_location = Column(JSON, nullable=True)  # lat, lon, city, country
    
    # Interaction data
    email_client = Column(String(100), nullable=True)
    browser = Column(String(100), nullable=True)
    os = Column(String(100), nullable=True)
    
    # Form submissions (if any)
    submitted_data = Column(JSON, nullable=True)  # Captured form data (passwords, etc.)
    
    # Campaign reference
    engagement_id = Column(Integer, ForeignKey("engagements.id"), nullable=False)
    
    # Relationships
    campaign = relationship("PhishingCampaign", back_populates="results")
    
    def __repr__(self):
        return f"<PhishingResult {self.event_type}:{self.target_email}>"


class PhishingTemplate(Base):
    """Phishing email/SMS templates."""
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    category = Column(String(100), nullable=True)  # credential_harvest, malware, information_gathering
    
    # Content
    subject = Column(String(500), nullable=True)
    body_text = Column(Text, nullable=True)
    body_html = Column(Text, nullable=True)
    
    # Technical
    content_type = Column(String(50), default="email")  # email, sms, voice
    sender_name = Column(String(200), nullable=True)
    sender_email = Column(String(200), nullable=True)
    
    # Tracking
    tracking_pixel = Column(Boolean, default=True)
    link_tracking = Column(Boolean, default=True)
    
    # Metadata
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<PhishingTemplate {self.name}>"


class SocialEngineeringFinding(Base):
    """Social engineering finding model."""
    
    id = Column(Integer, primary_key=True, index=True)
    engagement_id = Column(Integer, ForeignKey("engagements.id"), nullable=False)
    
    # Finding details
    finding_type = Column(String(100), nullable=False)  # phishing_success, vishing_success, pretexting, baiting
    severity = Column(String(20), nullable=False)  # CRITICAL, HIGH, MEDIUM, LOW
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    
    # Attack vector
    attack_vector = Column(String(50), nullable=False)  # email, phone, in_person, usb, social_media
    campaign_id = Column(Integer, ForeignKey("phishing_campaigns.id"), nullable=True)
    
    # Target
    target = Column(String(200), nullable=True)
    department = Column(String(100), nullable=True)
    
    # Outcome
    data_obtained = Column(JSON, nullable=True)  # credentials, access_token, etc.
    access_gained = Column(Text, nullable=True)
    impact_level = Column(String(50), nullable=True)
    
    # Evidence
    screenshots = Column(JSON, nullable=True)
    recording_url = Column(String(500), nullable=True)  # For vishing
    audio_file = Column(String(500), nullable=True)
    
    # Remediation
    remediation = Column(Text, nullable=True)
    training_recommendation = Column(Text, nullable=True)
    
    # Status
    status = Column(String(20), default="open")
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Timestamps
    discovered_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    engagement = relationship("Engagement", back_populates="social_engineering_findings")
    
    def __repr__(self):
        return f"<SocialEngineeringFinding {self.finding_type}:{self.severity}>"


class TargetList(Base):
    """Target list for social engineering campaigns."""
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Targets
    targets = Column(JSON, nullable=True)  # List of target objects
    
    # Metadata
    source = Column(String(100), nullable=True)  # LinkedIn, Company Website, OSINT
    imported_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    imported_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<TargetList {self.name}>"
