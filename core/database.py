"""
Database configuration and session management.
"""
import os
from sqlalchemy import create_engine, Column, String, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session as DBSession
from datetime import datetime
from dotenv import load_dotenv
from .logger import get_logger

load_dotenv()
logger = get_logger(__name__)

# Database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/travel_companion")

# Create engine
engine = create_engine(DATABASE_URL, echo=True)  # echo=True za debug

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Database Models
class ChatSession(Base):
    """Chat session model."""
    __tablename__ = "chat_sessions"
    
    session_id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=True)
    data = Column(JSON)  # Travel preferences
    itinerary = Column(JSON, nullable=True)  # Generated itinerary
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

def init_db():
    """Create all tables."""
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")

def get_db():
    """Dependency for FastAPI to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()