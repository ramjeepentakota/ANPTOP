"""
ANPTOP Backend - Social Engineering Endpoints
"""

from datetime import datetime
from typing import Optional, List, Dict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.db.session import get_db
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()


# Pydantic schemas
class PhishingCampaignCreate(BaseModel):
    """Phishing campaign creation schema."""
    engagement_id: int
    campaign_name: str
    target_emails: List[str]
    template_id: Optional[str] = None
    landing_page_id: Optional[str] = None
    sender_name: Optional[str] = None
    sender_email: Optional[str] = None
    subject: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    status: str = "pending"  # pending, running, completed, paused


class PhishingCampaignResponse(BaseModel):
    """Phishing campaign response schema."""
    id: int
    engagement_id: int
    campaign_name: str
    target_emails: List[str]
    template_id: Optional[str]
    landing_page_id: Optional[str]
    sender_name: Optional[str]
    sender_email: Optional[str]
    subject: Optional[str]
    status: str
    scheduled_at: Optional[datetime]
    sent_count: int = 0
    opened_count: int = 0
    clicked_count: int = 0
    submitted_count: int = 0
    created_at: datetime


class PhishingResultCreate(BaseModel):
    """Phishing result submission schema."""
    campaign_id: int
    target_email: str
    event_type: str  # sent, opened, clicked, submitted, reported
    timestamp: datetime
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    metadata: Dict = {}


# In-memory storage
phishing_campaigns = []
phishing_results = []


@router.post("/campaigns", response_model=PhishingCampaignResponse)
async def create_phishing_campaign(
    campaign: PhishingCampaignCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new phishing campaign.
    """
    new_campaign = {
        'id': len(phishing_campaigns) + 1,
        **campaign.dict(),
        'sent_count': 0,
        'opened_count': 0,
        'clicked_count': 0,
        'submitted_count': 0,
        'created_at': datetime.utcnow(),
    }
    phishing_campaigns.append(new_campaign)
    return new_campaign


@router.get("/campaigns", response_model=List[PhishingCampaignResponse])
async def get_phishing_campaigns(
    engagement_id: Optional[int] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get phishing campaigns, optionally filtered.
    """
    result = phishing_campaigns
    
    if engagement_id:
        result = [c for c in result if c['engagement_id'] == engagement_id]
    
    if status:
        result = [c for c in result if c['status'] == status]
    
    return result


@router.get("/campaigns/{campaign_id}", response_model=PhishingCampaignResponse)
async def get_phishing_campaign(
    campaign_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a specific phishing campaign.
    """
    for campaign in phishing_campaigns:
        if campaign['id'] == campaign_id:
            return campaign
    raise HTTPException(status_code=404, detail="Campaign not found")


@router.post("/results")
async def submit_phishing_result(
    result: PhishingResultCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Submit a phishing campaign result (opened, clicked, etc.).
    """
    new_result = {
        'id': len(phishing_results) + 1,
        **result.dict(),
    }
    phishing_results.append(new_result)
    
    # Update campaign stats
    for campaign in phishing_campaigns:
        if campaign['id'] == result.campaign_id:
            if result.event_type == 'sent':
                campaign['sent_count'] += 1
            elif result.event_type == 'opened':
                campaign['opened_count'] += 1
            elif result.event_type == 'clicked':
                campaign['clicked_count'] += 1
            elif result.event_type == 'submitted':
                campaign['submitted_count'] += 1
            break
    
    return {'status': 'success'}


@router.get("/campaigns/{campaign_id}/stats")
async def get_phishing_campaign_stats(
    campaign_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get statistics for a phishing campaign.
    """
    campaign = None
    for c in phishing_campaigns:
        if c['id'] == campaign_id:
            campaign = c
            break
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    results = [r for r in phishing_results if r['campaign_id'] == campaign_id]
    
    return {
        'campaign_id': campaign_id,
        'total_targets': len(campaign['target_emails']),
        'sent': campaign['sent_count'],
        'opened': campaign['opened_count'],
        'clicked': campaign['clicked_count'],
        'submitted': campaign['submitted_count'],
        'opened_rate': round((campaign['opened_count'] / campaign['sent_count'] * 100), 2) if campaign['sent_count'] > 0 else 0,
        'clicked_rate': round((campaign['clicked_count'] / campaign['opened_count'] * 100), 2) if campaign['opened_count'] > 0 else 0,
        'submission_rate': round((campaign['submitted_count'] / campaign['clicked_count'] * 100), 2) if campaign['clicked_count'] > 0 else 0,
    }


class VoicePhishingCreate(BaseModel):
    """Voice phishing (vishing) campaign schema."""
    engagement_id: int
    campaign_name: str
    target_numbers: List[str]
    script: Optional[str] = None
    audio_file_id: Optional[str] = None
    status: str = "pending"


@router.post("/vishing")
async def create_vishing_campaign(
    campaign: VoicePhishingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a vishing campaign (placeholder for integration).
    """
    return {
        'id': len(phishing_campaigns) + 1,
        **campaign.dict(),
        'created_at': datetime.utcnow(),
    }


class SmishingCreate(BaseModel):
    """SMS phishing (smishing) campaign schema."""
    engagement_id: int
    campaign_name: str
    target_numbers: List[str]
    message: Optional[str] = None
    link: Optional[str] = None
    status: str = "pending"


@router.post("/smishing")
async def create_smishing_campaign(
    campaign: SmishingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a smishing campaign (placeholder for integration).
    """
    return {
        'id': len(phishing_campaigns) + 1,
        **campaign.dict(),
        'created_at': datetime.utcnow(),
    }
