from sqlalchemy import Column, Integer, String, Enum, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
from app.database.base import Base


class SponsorStatus(PyEnum):
    ACTIVE = "active"
    PENDING = "pending"
    INACTIVE = "inactive"


class SponsorTier(PyEnum):
    PLATINUM = "Platinum"
    GOLD = "Gold"
    SILVER = "Silver"
    BRONZE = "Bronze"


class Sponsor(Base):
    __tablename__ = "sponsors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    industry = Column(String, nullable=True)
    contact_email = Column(String, nullable=False)
    contact_person = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    website = Column(String, nullable=True)
    tier = Column(Enum(SponsorTier), default=SponsorTier.BRONZE)
    status = Column(Enum(SponsorStatus), default=SponsorStatus.PENDING)
    budget = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
