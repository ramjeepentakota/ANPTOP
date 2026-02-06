"""
ANPTOP Backend - Database Base Configuration
"""

from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, declared_attr
from sqlalchemy import Column, DateTime


class Base(DeclarativeBase):
    """Base class for all database models."""
    
    @declared_attr
    def __tablename__(cls) -> str:
        """Generate table name from class name (snake_case)."""
        import re
        name = re.sub(r'(?<!^)(?=[A-Z])', '_', cls.__name__).lower()
        return f"{name}s" if not name.endswith('s') else name
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class TimestampMixin:
    """Mixin for adding timestamp columns."""
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
