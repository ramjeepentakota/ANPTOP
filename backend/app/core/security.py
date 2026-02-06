"""
ANPTOP Backend - Security Utilities
"""

import secrets
from datetime import datetime, timedelta
from typing import Optional, List
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from sqlalchemy.ext.asyncio import AsyncSession
import pyotp
import qrcode
import io
import base64

from app.core.config import settings
from app.db.session import get_db
from app.models.user import User, UserRole


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme with scopes
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"/api/v1/auth/login",
    scopes={
        "admin": "Full administrative access",
        "lead": "Lead tester - create/manage engagements, approve workflows",
        "senior": "Senior tester - execute workflows, access all engagements",
        "tester": "Tester - execute assigned workflows",
        "analyst": "Analyst - view reports, create findings",
        "viewer": "Viewer - read-only access",
        "api": "API access - programmatic integration",
    },
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
    scopes: Optional[List[str]] = None,
) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    
    if scopes:
        to_encode.update({"scopes": scopes})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create a JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_REFRESH_SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    
    return encoded_jwt


def decode_token(token: str) -> dict:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Get the current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": f"Bearer {security_scopes.scope_str}"},
    )
    
    try:
        payload = decode_token(token)
        user_id: int = payload.get("sub")
        token_scopes: List[str] = payload.get("scopes", [])
        
        if user_id is None:
            raise credentials_exception
        
    except HTTPException:
        raise credentials_exception
    
    # Get user from database
    user = await User.get_by_id(db, user_id)
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )
    
    # Check required scopes
    if security_scopes.scopes:
        for scope in security_scopes.scopes:
            if scope not in token_scopes and scope not in user.get_scopes():
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Missing required scope: {scope}",
                    headers={"WWW-Authenticate": f"Bearer {security_scopes.scope_str}"},
                )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )
    return current_user


def generate_mfa_secret() -> str:
    """Generate a new MFA secret."""
    return pyotp.random_base32()


def get_mfa_uri(secret: str, email: str) -> str:
    """Generate MFA setup URI for authenticator apps."""
    return pyotp.totp.TOTP(secret).provisioning_uri(
        name=email,
        issuer_name=settings.MFA_ISSUER_NAME,
    )


def generate_mfa_qr_code(uri: str) -> str:
    """Generate base64 QR code for MFA setup."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


def verify_mfa_token(secret: str, token: str) -> bool:
    """Verify an MFA token."""
    totp = pyotp.TOTP(secret)
    return totp.verify(token, valid_window=1)


# Kill switch implementation
_kill_switch_active = False


def activate_kill_switch() -> None:
    """Activate the kill switch - stops all operations."""
    global _kill_switch_active
    _kill_switch_active = True


def deactivate_kill_switch() -> None:
    """Deactivate the kill switch."""
    global _kill_switch_active
    _kill_switch_active = False


def kill_switch_active() -> bool:
    """Check if kill switch is active."""
    if not settings.ENABLE_KILL_SWITCH:
        return False
    return _kill_switch_active


# Scope validation
def verify_scope_boundaries(
    engagement_id: int,
    target_ip: str,
    target_scope: List[str],
) -> bool:
    """Verify that a target is within engagement scope."""
    if not settings.SCOPE_VALIDATION:
        return True
    
    # Simple scope validation - check if target IP matches any scope pattern
    # In production, implement more sophisticated scope checking
    for scope_pattern in target_scope:
        if target_ip == scope_pattern or target_ip.startswith(scope_pattern.rstrip("*")):
            return True
    
    return False


# Audit logging
import asyncio
from app.models.evidence import AuditLog

_audit_logs = []


async def audit_log(
    action: str,
    user_id: Optional[int] = None,
    resource: Optional[str] = None,
    details: Optional[dict] = None,
    db: AsyncSession = None,
) -> None:
    """Create an audit log entry."""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "action": action,
        "user_id": user_id,
        "resource": resource,
        "details": details,
    }
    
    # Log to console
    print(f"[AUDIT] {log_entry}")
    
    # Store in memory for now (in production, use database)
    _audit_logs.append(log_entry)
    
    # Optionally save to database
    if db:
        try:
            audit = AuditLog(
                action=action,
                user_id=user_id,
                resource=resource,
                details=details,
            )
            db.add(audit)
            await db.commit()
        except Exception as e:
            print(f"[AUDIT ERROR] Failed to save audit log: {e}")


def generate_api_key() -> str:
    """Generate a secure API key."""
    return f"anptop_{secrets.token_urlsafe(32)}"


def hash_api_key(api_key: str) -> str:
    """Hash an API key for storage."""
    return get_password_hash(api_key)


def verify_api_key(api_key: str, hashed_key: str) -> bool:
    """Verify an API key against a hash."""
    return verify_password(api_key, hashed_key)


# Role-based permission checking
def check_permission(user: User, permission: str) -> bool:
    """Check if user has a specific permission."""
    role_permissions = {
        UserRole.ADMIN: ["*"],  # All permissions
        UserRole.LEAD: [
            "engagements:create",
            "engagements:read",
            "engagements:update",
            "engagements:delete",
            "targets:create",
            "targets:read",
            "targets:update",
            "targets:delete",
            "workflows:execute",
            "workflows:approve",
            "reports:create",
            "reports:read",
            "reports:export",
        ],
        UserRole.SENIOR: [
            "engagements:read",
            "targets:create",
            "targets:read",
            "targets:update",
            "workflows:execute",
            "workflows:approve",
            "reports:create",
            "reports:read",
            "reports:export",
        ],
        UserRole.TESTER: [
            "engagements:read",
            "targets:read",
            "workflows:execute",
            "reports:read",
        ],
        UserRole.ANALYST: [
            "engagements:read",
            "reports:create",
            "reports:read",
            "reports:export",
        ],
        UserRole.VIEWER: [
            "engagements:read",
            "reports:read",
        ],
        UserRole.API: [
            "engagements:read",
            "targets:read",
            "workflows:execute",
            "reports:read",
        ],
    }
    
    user_permissions = role_permissions.get(user.role, [])
    
    # Admin has all permissions
    if "*" in user_permissions:
        return True
    
    # Check specific permission
    return permission in user_permissions


# Crypto utilities
def generate_secure_token(length: int = 32) -> str:
    """Generate a secure random token."""
    return secrets.token_urlsafe(length)


def hash_evidence(data: bytes) -> str:
    """Create SHA-256 hash of evidence for integrity verification."""
    import hashlib
    return hashlib.sha256(data).hexdigest()
