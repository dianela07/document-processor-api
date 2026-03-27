"""
SQLAlchemy models for the database.
"""
from sqlalchemy import Column, String, DateTime, JSON, Text, Boolean, Integer
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()


class Process(Base):
    """Model for document processing records."""
    __tablename__ = "processes"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String(255), nullable=False)
    status = Column(String(50), default="pending")  # pending, processing, completed, error
    content_preview = Column(Text, nullable=True)
    extracted_data = Column(JSON, default=dict)
    metadata = Column(JSON, default=dict)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    
    def to_dict(self) -> dict:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "filename": self.filename,
            "status": self.status,
            "content_preview": self.content_preview,
            "extracted_data": self.extracted_data or {},
            "metadata": self.metadata or {},
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "processed_at": self.processed_at.isoformat() if self.processed_at else None
        }


class ExtractionFieldModel(Base):
    """Model for extraction field configurations."""
    __tablename__ = "extraction_fields"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=False)
    field_type = Column(String(50), default="string")  # string, number, date, boolean
    required = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self) -> dict:
        """Convert model to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "field_type": self.field_type,
            "required": self.required
        }
