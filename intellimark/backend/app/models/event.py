# app/models/event.py

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSON
from datetime import datetime
from app.database import Base


class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    
    # Event Details
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)
    tags = Column(JSON, default=list)
    
    # Location & Timing
    venue = Column(String(200), nullable=True)
    location = Column(String(200), nullable=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    
    # Media
    poster_image = Column(String, nullable=True)
    banner_image = Column(String, nullable=True)
    
    # Registration
    registration_url = Column(String, nullable=True)
    max_participants = Column(Integer, nullable=True)
    current_participants = Column(Integer, default=0)
    
    # Status
    is_published = Column(Boolean, default=False)
    is_cancelled = Column(Boolean, default=False)
    
    # AI Generated
    ai_generated_description = Column(Boolean, default=False)
    ai_generated_poster = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="events")
    campaigns = relationship("Campaign", back_populates="event")


# app/models/campaign.py

class Campaign(Base):
    __tablename__ = "campaigns"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=True)
    
    # Campaign Details
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    platform = Column(String(50), nullable=False)  # instagram, facebook, twitter, linkedin
    
    # Content
    post_content = Column(Text, nullable=False)
    media_urls = Column(JSON, default=list)
    hashtags = Column(JSON, default=list)
    
    # Scheduling
    scheduled_time = Column(DateTime, nullable=True)
    posted_at = Column(DateTime, nullable=True)
    
    # Status
    status = Column(String(20), default="draft")  # draft, scheduled, posted, failed
    
    # AI Features
    ai_generated_content = Column(Boolean, default=False)
    predicted_engagement_score = Column(Float, nullable=True)
    
    # Actual Engagement Metrics
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    reach = Column(Integer, default=0)
    impressions = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="campaigns")
    event = relationship("Event", back_populates="campaigns")