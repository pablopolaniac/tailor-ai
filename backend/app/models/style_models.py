from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Style(Base):
    """Style model for storing style profiles"""
    __tablename__ = "styles"
    
    id = Column(Integer, primary_key=True, index=True)
    style_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)  # casual, business, formal, sport
    tags = Column(JSON, nullable=True)  # List of tags
    user_id = Column(String(100), nullable=True)  # Owner of the style
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    images = relationship("StyleImage", back_populates="style", cascade="all, delete-orphan")

class StyleImage(Base):
    """Style image model for storing individual style images"""
    __tablename__ = "style_images"
    
    id = Column(Integer, primary_key=True, index=True)
    style_id = Column(Integer, ForeignKey("styles.id"), nullable=False)
    image_url = Column(String(500), nullable=False)
    image_type = Column(String(50), default="reference")  # reference, thumbnail, etc.
    embedding = Column(JSON, nullable=True)  # CLIP embedding vector
    image_metadata = Column(JSON, nullable=True)  # Image metadata (size, format, etc.)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    style = relationship("Style", back_populates="images")
