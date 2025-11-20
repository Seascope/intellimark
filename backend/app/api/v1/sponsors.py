# app/api/v1/sponsors.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.sponsor import Sponsor
from app.schemas.sponsor import SponsorCreate, SponsorUpdate, SponsorResponse, SponsorMatchRequest, SponsorMatchResponse
from app.api.deps import get_current_user, require_marketing_lead
from app.database.session import get_db
from app.services.sponsor_matcher import SponsorMatcher

router = APIRouter(prefix="/sponsors", tags=["Sponsors"])


@router.post("/", response_model=SponsorResponse)
def create_sponsor(
    sponsor: SponsorCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_marketing_lead)
):
    db_sponsor = Sponsor(**sponsor.dict())
    db.add(db_sponsor)
    db.commit()
    db.refresh(db_sponsor)
    return db_sponsor


@router.get("/", response_model=list[SponsorResponse])
def list_sponsors(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return db.query(Sponsor).all()


@router.post("/match", response_model=list[SponsorMatchResponse])
def match_sponsors(
    request: SponsorMatchRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_marketing_lead)
):
    matcher = SponsorMatcher(db)
    results = matcher.match_sponsors(request)
    return results

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database.session import get_db
from app.models.user import User
from app.models.sponsor import Sponsor, SponsorStatus, SponsorTier
from app.schemas.sponsor import (
    SponsorCreate, SponsorUpdate, SponsorResponse,
    SponsorMatchRequest, SponsorMatchResponse
)
from app.api.deps import get_current_user, require_marketing_lead
from app.services.sponsor_matcher import SponsorMatcher

router = APIRouter()



@router.post("/", response_model=SponsorResponse, status_code=status.HTTP_201_CREATED)
def create_sponsor(
    sponsor_data: SponsorCreate,
    current_user: User = Depends(require_marketing_lead),
    db: Session = Depends(get_db)
):
    """Create a new sponsor"""
    
    # Check if sponsor already exists
    existing = db.query(Sponsor).filter(
        Sponsor.organization_id == current_user.organization_id,
        Sponsor.contact_email == sponsor_data.contact_email
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sponsor with this email already exists"
        )
    
    # Create sponsor
    db_sponsor = Sponsor(
        **sponsor_data.dict(),
        organization_id=current_user.organization_id,
        added_by_id=current_user.id
    )
    
    db.add(db_sponsor)
    db.commit()
    db.refresh(db_sponsor)
    
    return SponsorResponse.from_orm(db_sponsor)


@router.get("/", response_model=List[SponsorResponse])
def list_sponsors(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, le=100),
    status: Optional[SponsorStatus] = None,
    tier: Optional[SponsorTier] = None,
    industry: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all sponsors for the organization"""
    
    query = db.query(Sponsor).filter(
        Sponsor.organization_id == current_user.organization_id
    )
    
    # Apply filters
    if status:
        query = query.filter(Sponsor.status == status)
    if tier:
        query = query.filter(Sponsor.tier == tier)
    if industry:
        query = query.filter(Sponsor.industry == industry)
    if search:
        query = query.filter(Sponsor.name.ilike(f"%{search}%"))
    
    # Order by relevance score
    query = query.order_by(Sponsor.relevance_score.desc())
    
    sponsors = query.offset(skip).limit(limit).all()
    
    return [SponsorResponse.from_orm(s) for s in sponsors]


@router.get("/{sponsor_id}", response_model=SponsorResponse)
def get_sponsor(
    sponsor_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific sponsor"""
    
    sponsor = db.query(Sponsor).filter(
        Sponsor.id == sponsor_id,
        Sponsor.organization_id == current_user.organization_id
    ).first()
    
    if not sponsor:
        raise HTTPException(status_code=404, detail="Sponsor not found")
    
    return SponsorResponse.from_orm(sponsor)


@router.put("/{sponsor_id}", response_model=SponsorResponse)
def update_sponsor(
    sponsor_id: int,
    sponsor_data: SponsorUpdate,
    current_user: User = Depends(require_marketing_lead),
    db: Session = Depends(get_db)
):
    """Update a sponsor"""
    
    sponsor = db.query(Sponsor).filter(
        Sponsor.id == sponsor_id,
        Sponsor.organization_id == current_user.organization_id
    ).first()
    
    if not sponsor:
        raise HTTPException(status_code=404, detail="Sponsor not found")
    
    # Update fields
    update_data = sponsor_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(sponsor, field, value)
    
    db.commit()
    db.refresh(sponsor)
    
    return SponsorResponse.from_orm(sponsor)


@router.delete("/{sponsor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sponsor(
    sponsor_id: int,
    current_user: User = Depends(require_marketing_lead),
    db: Session = Depends(get_db)
):
    """Delete a sponsor"""
    
    sponsor = db.query(Sponsor).filter(
        Sponsor.id == sponsor_id,
        Sponsor.organization_id == current_user.organization_id
    ).first()
    
    if not sponsor:
        raise HTTPException(status_code=404, detail="Sponsor not found")
    
    db.delete(sponsor)
    db.commit()
    
    return None


@router.post("/match", response_model=List[SponsorMatchResponse])
def match_sponsors_to_event(
    match_request: SponsorMatchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    AI-powered sponsor matching to event.
    Returns ranked list of sponsors based on relevance.
    """
    
    # Get active sponsors
    sponsors = db.query(Sponsor).filter(
        Sponsor.organization_id == current_user.organization_id,
        Sponsor.status.in_([SponsorStatus.ACTIVE, SponsorStatus.PROSPECT])
    ).all()
    
    if not sponsors:
        return []
    
    # Perform AI matching
    matches = sponsor_matcher.match_sponsors_to_event(
        sponsors=sponsors,
        event={
            'title': match_request.event_title,
            'description': match_request.event_description,
            'category': match_request.event_category,
            'tags': match_request.event_tags
        },
        top_k=match_request.top_k
    )
    
    # Format response
    results = []
    for sponsor, score in matches:
        results.append(SponsorMatchResponse(
            sponsor=SponsorResponse.from_orm(sponsor),
            relevance_score=float(score),
            match_reasons=sponsor_matcher.get_match_reasons(sponsor, match_request)
        ))
    
    return results


@router.post("/update-scores", status_code=status.HTTP_200_OK)
def update_relevance_scores(
    current_user: User = Depends(require_marketing_lead),
    db: Session = Depends(get_db)
):
    """
    Update relevance scores for all sponsors.
    Should be run periodically or after organization profile changes.
    """
    
    sponsors = db.query(Sponsor).filter(
        Sponsor.organization_id == current_user.organization_id
    ).all()
    
    if not sponsors:
        return {"message": "No sponsors to update"}
    
    # Get organization profile
    org = current_user.organization
    org_profile = {
        'description': org.description or '',
        'focus_areas': [],  # Can be extended
        'past_event_themes': []  # Can be extended
    }
    
    # Update scores
    sponsor_matcher.batch_update_relevance_scores(sponsors, org_profile)
    
    return {
        "message": f"Updated relevance scores for {len(sponsors)} sponsors",
        "sponsors_updated": len(sponsors)
    }
