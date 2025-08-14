from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.sql import func
from app.core.database import Base

class User(Base):
    """User model for storing user information"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=True)
    name = Column(String(255), nullable=True)
    auth_provider = Column(String(50), nullable=True)  # firebase, cognito, etc.
    auth_provider_id = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Integer, default=1)  # 1 for active, 0 for inactive

class UserPreferences(Base):
    """User preferences model for storing fashion preferences"""
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), index=True, nullable=False)
    style_preferences = Column(JSON, nullable=True)  # List of preferred styles
    color_preferences = Column(JSON, nullable=True)  # List of preferred colors
    fit_preferences = Column(String(50), nullable=True)  # loose, fitted, oversized
    occasion_preferences = Column(JSON, nullable=True)  # List of preferred occasions
    body_type = Column(String(50), nullable=True)  # athletic, slim, plus-size, etc.
    age_group = Column(String(50), nullable=True)  # 18-25, 26-35, etc.
    budget_range = Column(String(50), nullable=True)  # low, medium, high
    brand_preferences = Column(JSON, nullable=True)  # List of preferred brands
    size_preferences = Column(JSON, nullable=True)  # Size preferences for different garments
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
