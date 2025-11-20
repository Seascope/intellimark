from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List
from enum import Enum


class SponsorStatus(str, Enum):
    ACTIVE = "active"
    PENDING = "pending"
    INACTIVE = "inactive"


class SponsorTier(str, Enum):
    PLATINUM = "Platinum"
    GOLD = "Gold"
    SILVER = "Silver"
    BRONZE = "Bronze"


class SponsorBase(BaseModel):
    name: str
    industry: Optional[str] = None
    contact_email: EmailStr
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    tier: SponsorTier = SponsorTier.BRONZE
    status: SponsorStatus = SponsorStatus.PENDING
    budget: Optional[float] = None
    notes: Optional[str] = None


class SponsorCreate(SponsorBase):
    pass


class SponsorUpdate(BaseModel):
    industry: Optional[str] = None
    tier: Optional[SponsorTier] = None
    status: Optional[SponsorStatus] = None
    budget: Optional[float] = None
    notes: Optional[str] = None


class SponsorResponse(SponsorBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ---------- Matching Schemas ----------

class SponsorMatchRequest(BaseModel):
    event_name: str
    event_theme: Optional[str] = None
    description: Optional[str] = None
    keywords: Optional[List[str]] = None


class SponsorMatchResponse(BaseModel):
    sponsor_id: int
    sponsor_name: str
    relevance_score: float
