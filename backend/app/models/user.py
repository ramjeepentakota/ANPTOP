"""
ANPTOP Backend - User Model
"""

from datetime import datetime
from enum import Enum as PyEnum
from typing import List, Optional
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from app.db.base import Base, TimestampMixin


class UserRole(str, PyEnum):
    """User roles for RBAC."""
    ADMIN = "admin"
    LEAD = "lead"
    SENIOR = "senior"
    TESTER = "tester"
    ANALYST = "analyst"
    VIEWER = "viewer"
    API = "api"


class User(Base, TimestampMixin):
    """User model for authentication and authorization."""
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.TESTER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    
    # MFA
    mfa_secret = Column(String(255), nullable=True)
    mfa_enabled = Column(Boolean, default=False, nullable=False)
    
    # Password reset
    password_changed_at = Column(DateTime, default=datetime.utcnow)
    password_reset_token = Column(String(255), nullable=True)
    password_reset_expires = Column(DateTime, nullable=True)
    
    # API Key (for API users)
    api_key = Column(String(255), nullable=True)
    api_key_hash = Column(String(255), nullable=True)
    
    # Relationships
    engagements = relationship("Engagement", back_populates="owner", foreign_keys="Engagement.owner_id")
    findings = relationship("Finding", back_populates="creator")
    audit_logs = relationship("AuditLog", back_populates="user")
    workflow_executions = relationship("WorkflowExecution", back_populates="executed_by")
    
    def get_scopes(self) -> List[str]:
        """Get list of scopes based on user role."""
        scopes = {
            UserRole.ADMIN: ["admin", "lead", "senior", "tester", "analyst", "viewer", "api"],
            UserRole.LEAD: ["lead", "senior", "tester", "analyst", "viewer"],
            UserRole.SENIOR: ["senior", "tester", "analyst", "viewer"],
            UserRole.TESTER: ["tester", "analyst"],
            UserRole.ANALYST: ["analyst"],
            UserRole.VIEWER: ["viewer"],
            UserRole.API: ["api"],
        }
        return scopes.get(self.role, [])
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has a specific permission."""
        # Admins have all permissions
        if self.role == UserRole.ADMIN:
            return True
        
        # Define role-based permissions
        role_permissions = {
            UserRole.LEAD: [
                "engagements:create", "engagements:read", "engagements:update", "engagements:delete",
                "targets:create", "targets:read", "targets:update", "targets:delete",
                "workflows:execute", "workflows:approve", "workflows:create", "workflows:read",
                "reports:create", "reports:read", "reports:export", "reports:delete",
                "users:read", "users:create",
            ],
            UserRole.SENIOR: [
                "engagements:read", "targets:read", "targets:create", "targets:update",
                "workflows:execute", "workflows:approve", "workflows:read",
                "reports:create", "reports:read", "reports:export",
            ],
            UserRole.TESTER: [
                "engagements:read", "targets:read", "workflows:execute", "reports:read",
            ],
            UserRole.ANALYST: [
                "engagements:read", "reports:create", "reports:read", "reports:export",
                "findings:create", "findings:read", "findings:update",
            ],
            UserRole.VIEWER: [
                "engagements:read", "reports:read",
            ],
            UserRole.API: [
                "engagements:read", "targets:read", "workflows:execute", "reports:read",
            ],
        }
        
        user_permissions = role_permissions.get(self.role, [])
        return permission in user_permissions or "*" in user_permissions
    
    # CRUD operations
    @classmethod
    async def get_by_id(cls, db, user_id: int) -> Optional["User"]:
        """Get user by ID."""
        from sqlalchemy import select
        result = await db.execute(select(cls).where(cls.id == user_id))
        return result.scalar_one_or_none()
    
    @classmethod
    async def get_by_email(cls, db, email: str) -> Optional["User"]:
        """Get user by email."""
        from sqlalchemy import select
        result = await db.execute(select(cls).where(cls.email == email))
        return result.scalar_one_or_none()
    
    @classmethod
    async def get_by_username(cls, db, username: str) -> Optional["User"]:
        """Get user by username."""
        from sqlalchemy import select
        result = await db.execute(select(cls).where(cls.username == username))
        return result.scalar_one_or_none()
    
    @classmethod
    async def get_all(cls, db, skip: int = 0, limit: int = 100) -> List["User"]:
        """Get all users with pagination."""
        from sqlalchemy import select
        result = await db.execute(select(cls).offset(skip).limit(limit))
        return result.scalars().all()
    
    async def save(self, db) -> "User":
        """Save the user to the database."""
        db.add(self)
        await db.commit()
        await db.refresh(self)
        return self
    
    async def update(self, db, **kwargs) -> "User":
        """Update user fields."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        await db.commit()
        await db.refresh(self)
        return self
    
    async def delete(self, db) -> None:
        """Delete the user."""
        await db.delete(self)
        await db.commit()
