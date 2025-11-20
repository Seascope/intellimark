from sqlalchemy.orm import declarative_base
from app.models.user import User, ActivityLog
from app.database.base_class import Base  # Import Base only
from app.models.user import User, ActivityLog  # Import all models here

Base = declarative_base()
