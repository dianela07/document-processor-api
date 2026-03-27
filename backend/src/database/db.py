"""
SQLite Database Module with SQLAlchemy.
Provides persistent storage for document processing records.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from typing import Optional, List
import os

from src.database.models import Base, Process, ExtractionFieldModel
from src.core.config import settings


# Create database directory if not exists
db_dir = os.path.dirname(settings.DATABASE_URL.replace("sqlite:///", ""))
if db_dir and not os.path.exists(db_dir):
    os.makedirs(db_dir, exist_ok=True)

# Create engine and session
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},  # Required for SQLite
    echo=settings.DEBUG
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize the database, creating all tables."""
    Base.metadata.create_all(bind=engine)


def get_db() -> Session:
    """Get a database session."""
    db = SessionLocal()
    try:
        return db
    finally:
        pass  # Session management handled by caller


class ProcessesDB:
    """Repository for document processing records."""
    
    def __init__(self):
        init_db()
    
    def _get_session(self) -> Session:
        return SessionLocal()
    
    def load_processes(self, limit: int = 100, offset: int = 0) -> dict:
        """Load all processes as a dictionary (for backward compatibility)."""
        with self._get_session() as session:
            processes = session.query(Process)\
                .order_by(Process.created_at.desc())\
                .offset(offset)\
                .limit(limit)\
                .all()
            return {p.id: p.to_dict() for p in processes}
    
    def get_all_processes(self, limit: int = 100, offset: int = 0) -> List[dict]:
        """Get all processes as a list of dictionaries."""
        with self._get_session() as session:
            processes = session.query(Process)\
                .order_by(Process.created_at.desc())\
                .offset(offset)\
                .limit(limit)\
                .all()
            return [p.to_dict() for p in processes]
    
    def get_total_count(self) -> int:
        """Get total number of processes."""
        with self._get_session() as session:
            return session.query(Process).count()
    
    def add_process(self, response: dict) -> str:
        """Add a new process record."""
        with self._get_session() as session:
            process = Process(
                id=response.get('id'),
                filename=response.get('filename', 'unknown'),
                status=response.get('status', 'completed'),
                content_preview=response.get('content_preview'),
                extracted_data=response.get('extracted_data', {}),
                metadata=response.get('metadata', {}),
                error_message=response.get('error_message'),
                processed_at=datetime.fromisoformat(response['processed_at']) 
                    if response.get('processed_at') else datetime.utcnow()
            )
            session.add(process)
            session.commit()
            return process.id
    
    def get_process(self, process_id: str) -> Optional[dict]:
        """Get a single process by ID."""
        with self._get_session() as session:
            process = session.query(Process).filter(Process.id == process_id).first()
            return process.to_dict() if process else None
    
    def delete_process(self, process_id: str) -> bool:
        """Delete a process by ID."""
        with self._get_session() as session:
            process = session.query(Process).filter(Process.id == process_id).first()
            if process:
                session.delete(process)
                session.commit()
                return True
            return False


class FieldsDB:
    """Repository for extraction field configurations."""
    
    def __init__(self):
        init_db()
    
    def _get_session(self) -> Session:
        return SessionLocal()
    
    def get_all(self) -> List[dict]:
        """Get all extraction fields."""
        with self._get_session() as session:
            fields = session.query(ExtractionFieldModel).all()
            return [f.to_dict() for f in fields]
    
    def create(self, field_data: dict) -> dict:
        """Create a new extraction field."""
        with self._get_session() as session:
            # Check if field already exists
            existing = session.query(ExtractionFieldModel)\
                .filter(ExtractionFieldModel.name == field_data['name']).first()
            if existing:
                raise ValueError(f"Field '{field_data['name']}' already exists")
            
            field = ExtractionFieldModel(
                name=field_data['name'],
                description=field_data['description'],
                field_type=field_data.get('field_type', 'string'),
                required=field_data.get('required', True)
            )
            session.add(field)
            session.commit()
            return field.to_dict()
    
    def delete(self, field_name: str) -> bool:
        """Delete a field by name."""
        with self._get_session() as session:
            field = session.query(ExtractionFieldModel)\
                .filter(ExtractionFieldModel.name == field_name).first()
            if field:
                session.delete(field)
                session.commit()
                return True
            return False
    
    def delete_all(self) -> int:
        """Delete all fields. Returns count of deleted fields."""
        with self._get_session() as session:
            count = session.query(ExtractionFieldModel).count()
            session.query(ExtractionFieldModel).delete()
            session.commit()
            return count
    
    def update(self, field_name: str, updates: dict) -> bool:
        """Update a field by name."""
        with self._get_session() as session:
            field = session.query(ExtractionFieldModel)\
                .filter(ExtractionFieldModel.name == field_name).first()
            if field:
                for key, value in updates.items():
                    if hasattr(field, key):
                        setattr(field, key, value)
                session.commit()
                return True
            return False
