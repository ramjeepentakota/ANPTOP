# ANPTOP - FastAPI Backend Documentation

## Table of Contents
1. [Project Structure](#project-structure)
2. [API Endpoints](#api-endpoints)
3. [Authentication & Security](#authentication--security)
4. [Core Services](#core-services)
5. [Database Models](#database-models)
6. [Configuration](#configuration)

---

## 1. Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application
│   ├── config.py                  # Configuration management
│   ├── constants.py               # Application constants
│   │
│   ├── api/                       # API endpoints
│   │   ├── __init__.py
│   │   ├── deps.py                # Dependencies (auth, DB, etc.)
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py            # Authentication endpoints
│   │   │   ├── engagements.py     # Engagement management
│   │   │   ├── hosts.py           # Host management
│   │   │   ├── ports.py           # Port management
│   │   │   ├── services.py        # Service management
│   │   │   ├── vulnerabilities.py # Vulnerability management
│   │   │   ├── exploits.py        # Exploitation management
│   │   │   ├── post_exploitation.py
│   │   │   ├── lateral_movement.py
│   │   │   ├── approvals.py       # Approval workflow
│   │   │   ├── evidence.py        # Evidence management
│   │   │   ├── reports.py         # Report generation
│   │   │   ├── audit.py           # Audit logging
│   │   │   ├── notifications.py   # Notifications
│   │   │   └── webhooks.py        # Webhook endpoints
│   │   │
│   │   └── errors.py              # Error handlers
│   │
│   ├── core/                      # Core functionality
│   │   ├── __init__.py
│   │   ├── config.py              # Settings
│   │   ├── security.py            # Security utilities
│   │   ├── permissions.py         # RBAC implementation
│   │   ├── logging.py             # Logging configuration
│   │   └── encryption.py          # Encryption utilities
│   │
│   ├── models/                    # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── engagement.py
│   │   ├── host.py
│   │   ├── port.py
│   │   ├── service.py
│   │   ├── vulnerability.py
│   │   ├── exploit.py
│   │   ├── post_exploitation.py
│   │   ├── lateral_movement.py
│   │   ├── evidence.py
│   │   ├── approval.py
│   │   ├── audit.py
│   │   └── notification.py
│   │
│   ├── schemas/                    # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── engagement.py
│   │   ├── host.py
│   │   ├── port.py
│   │   ├── service.py
│   │   ├── vulnerability.py
│   │   ├── exploit.py
│   │   ├── evidence.py
│   │   ├── approval.py
│   │   ├── audit.py
│   │   └── common.py
│   │
│   ├── services/                  # Business logic
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── engagement_service.py
│   │   ├── scan_service.py
│   │   ├── n8n_service.py
│   │   ├── approval_service.py
│   │   ├── evidence_service.py
│   │   ├── report_service.py
│   │   ├── cve_service.py
│   │   └── notification_service.py
│   │
│   ├── db/                        # Database
│   │   ├── __init__.py
│   │   ├── session.py             # DB sessions
│   │   ├── base.py                # Base class
│   │   └── init_db.py             # DB initialization
│   │
│   ├── ml/                        # Machine learning
│   │   ├── __init__.py
│   │   ├── vulnerability_ranker.py
│   │   └── false_positive_detector.py
│   │
│   └── utils/                      # Utilities
│       ├── __init__.py
│       ├── validators.py
│       ├── formatters.py
│       └── helpers.py
│
├── migrations/
│   └── versions/
│
├── tests/
│   ├── __init__.py
│   ├── test_auth.py
│   ├── test_engagements.py
│   └── test_api.py
│
├── scripts/
│   ├── init_db.py
│   ├── create_admin.py
│   └── seed_data.py
│
├── Dockerfile
├── requirements.txt
├── alembic.ini
└── .env.example
```

---

## 2. Main Application

### 2.1 main.py
```python
"""
ANPTOP - FastAPI Backend Application
"""
import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer

from app.core.config import settings
from app.db.session import get_db, engine
from app.db.init_db import init_db
from app.api import deps
from app.api.v1 import auth, engagements, hosts, ports, services, vulnerabilities, exploits, approvals, evidence, reports, audit, notifications, webhooks
from app.core.security import verify_token
from app.core.logging import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Security scheme
bearer_scheme = HTTPBearer(auto_error=False)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting ANPTOP Backend...")
    
    # Initialize database
    if settings.INIT_DB:
        init_db()
    
    logger.info("ANPTOP Backend started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down ANPTOP Backend...")


# Create FastAPI application
app = FastAPI(
    title="ANPTOP API",
    description="Automated Network Penetration Testing Orchestration Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS,
)


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


# Include routers
app.include_router(auth.router, prefix="/api/v1", tags=["Authentication"])
app.include_router(engagements.router, prefix="/api/v1/engagements", tags=["Engagements"])
app.include_router(hosts.router, prefix="/api/v1/hosts", tags=["Hosts"])
app.include_router(ports.router, prefix="/api/v1/ports", tags=["Ports"])
app.include_router(services.router, prefix="/api/v1/services", tags=["Services"])
app.include_router(vulnerabilities.router, prefix="/api/v1/vulnerabilities", tags=["Vulnerabilities"])
app.include_router(exploits.router, prefix="/api/v1/exploits", tags=["Exploits"])
app.include_router(approvals.router, prefix="/api/v1/approvals", tags=["Approvals"])
app.include_router(evidence.router, prefix="/api/v1/evidence", tags=["Evidence"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports"])
app.include_router(audit.router, prefix="/api/v1/audit", tags=["Audit"])
app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["Notifications"])
app.include_router(webhooks.router, prefix="/api/v1/webhooks", tags=["Webhooks"])


# Health check
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}


@app.get("/api/v1/me", tags=["Authentication"])
async def get_current_user(
    token: str = Depends(bearer_scheme),
    db=Depends(get_db)
):
    """Get current authenticated user"""
    if not token:
        return JSONResponse(status_code=403, content={"detail": "Not authenticated"})
    
    payload = verify_token(token.credentials)
    if not payload:
        return JSONResponse(status_code=401, content={"detail": "Invalid token"})
    
    user = deps.get_user_by_email(db, payload.get("sub"))
    if not user:
        return JSONResponse(status_code=404, content={"detail": "User not found"})
    
    return user


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## 2. API Endpoints

### 2.1 Authentication Endpoints

#### auth.py
```python
"""
Authentication API endpoints
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    get_password_hash,
    generate_mfa_secret,
    verify_mfa_token,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import Token, TokenPayload, UserCreate, UserResponse, UserLogin
from app.services.auth_service import AuthService
from app.api import deps
from app.schemas.common import Msg, ErrorResponse

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user
    
    - **username**: Unique username
    - **email**: Unique email address
    - **password**: Secure password (min 16 chars)
    - **first_name**: User's first name
    - **last_name**: User's last name
    """
    service = AuthService(db)
    
    # Check if user exists
    if service.get_user_by_email(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    if service.get_user_by_username(user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create user
    user = service.create_user(user_data)
    
    return user


@router.post("/login", response_model=Token)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    OAuth2 compatible token login
    
    Returns JWT access token and refresh token
    """
    service = AuthService(db)
    
    # Get user by username
    user = service.get_user_by_username(form_data.username)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled",
        )
    
    # Check MFA if enabled
    if user.mfa_enabled:
        # Return partial response indicating MFA required
        return {
            "access_token": "",
            "token_type": "bearer",
            "mfa_required": True,
            "mfa_token": service.create_mfa_token(user.id)
        }
    
    # Create tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    
    access_token = create_access_token(
        subject=user.id,
        expires_delta=access_token_expires,
        additional_claims={"role": user.role}
    )
    
    refresh_token = create_refresh_token(
        subject=user.id,
        expires_delta=refresh_token_expires
    )
    
    # Update last login
    service.update_last_login(user.id)
    
    # Log authentication
    await service.log_authentication(
        user_id=user.id,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
        success=True
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "mfa_required": False
    }


@router.post("/login/mfa", response_model=Token)
async def login_mfa(
    mfa_token: str,
    mfa_code: str,
    db: Session = Depends(get_db)
):
    """
    Complete MFA authentication
    """
    service = AuthService(db)
    
    # Validate MFA token
    user_id = service.validate_mfa_token(mfa_token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired MFA token"
        )
    
    user = service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify MFA code
    if not verify_mfa_token(user.mfa_secret, mfa_code):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid MFA code"
        )
    
    # Create tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.id,
        expires_delta=access_token_expires,
        additional_claims={"role": user.role}
    )
    
    refresh_token = create_refresh_token(
        subject=user.id,
        expires_delta=timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "mfa_required": False
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token
    """
    service = AuthService(db)
    
    payload = service.verify_refresh_token(refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user = service.get_user_by_id(payload.get("sub"))
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Create new access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.id,
        expires_delta=access_token_expires,
        additional_claims={"role": user.role}
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "mfa_required": False
    }


@router.post("/logout")
async def logout(
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Logout and invalidate tokens
    """
    service = AuthService(db)
    service.revoke_all_sessions(current_user.id)
    
    return {"message": "Successfully logged out"}


@router.post("/password/reset")
async def password_reset_request(
    email: str,
    db: Session = Depends(get_db)
):
    """
    Request password reset email
    """
    service = AuthService(db)
    user = service.get_user_by_email(email)
    
    # Always return success to prevent email enumeration
    if user:
        service.create_password_reset_token(user.id)
    
    return {"message": "If the email exists, a reset link has been sent"}


@router.post("/password/reset/confirm")
async def password_reset_confirm(
    token: str,
    new_password: str,
    db: Session = Depends(get_db)
):
    """
    Reset password with token
    """
    service = AuthService(db)
    user_id = service.verify_password_reset_token(token)
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    service.reset_password(user_id, new_password)
    
    return {"message": "Password has been reset successfully"}
```

### 2.2 Engagement Endpoints

#### engagements.py
```python
"""
Engagement API endpoints
"""
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.db.session import get_db
from app.models.user import User
from app.models.engagement import Engagement
from app.schemas.engagement import (
    EngagementCreate, 
    EngagementUpdate, 
    EngagementResponse,
    EngagementListResponse
)
from app.services.engagement_service import EngagementService
from app.services.approval_service import ApprovalService
from app.api import deps
from app.core.permissions import require_permission

router = APIRouter()


@router.get("", response_model=EngagementListResponse)
async def list_engagements(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status_filter: Optional[str] = None,
    client_name: Optional[str] = None,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all engagements for the current user
    
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    - **status_filter**: Filter by status
    - **client_name**: Filter by client name
    """
    service = EngagementService(db)
    
    # Get engagements based on role
    if current_user.role in ['CISO', 'TEAM_LEAD', 'AUDITOR']:
        # Can see all engagements
        engagements, total = service.list_engagements(
            skip=skip,
            limit=limit,
            status=status_filter,
            client_name=client_name
        )
    else:
        # Can only see own engagements or team engagements
        engagements, total = service.list_user_engagements(
            user_id=current_user.id,
            skip=skip,
            limit=limit,
            status=status_filter,
            client_name=client_name
        )
    
    return {
        "data": engagements,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/{engagement_id}", response_model=EngagementResponse)
async def get_engagement(
    engagement_id: str,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get engagement by ID
    """
    service = EngagementService(db)
    
    engagement = service.get_engagement(engagement_id)
    if not engagement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Engagement not found"
        )
    
    # Check access
    if not service.can_access_engagement(current_user, engagement):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this engagement"
        )
    
    return engagement


@router.post("", response_model=EngagementResponse, status_code=status.HTTP_201_CREATED)
async def create_engagement(
    engagement_data: EngagementCreate,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new engagement
    
    Requires ANALYST role or higher
    """
    # Require ANALYST or higher
    if current_user.role in ['VIEWER']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to create engagements"
        )
    
    service = EngagementService(db)
    
    # Validate scope
    is_valid, error = service.validate_scope(engagement_data.scope_targets)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid scope: {error}"
        )
    
    # Create engagement
    engagement = service.create_engagement(
        engagement_data=engagement_data,
        created_by=current_user.id
    )
    
    # Create audit log
    service.create_audit_log(
        engagement_id=engagement.id,
        user_id=current_user.id,
        action="create",
        details={"name": engagement.name}
    )
    
    return engagement


@router.put("/{engagement_id}", response_model=EngagementResponse)
async def update_engagement(
    engagement_id: str,
    engagement_data: EngagementUpdate,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an engagement
    """
    service = EngagementService(db)
    
    engagement = service.get_engagement(engagement_id)
    if not engagement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Engagement not found"
        )
    
    # Check permissions
    if not service.can_modify_engagement(current_user, engagement):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot modify this engagement"
        )
    
    # Update engagement
    updated = service.update_engagement(engagement, engagement_data)
    
    return updated


@router.delete("/{engagement_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_engagement(
    engagement_id: str,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete an engagement (soft delete)
    
    Requires TEAM_LEAD role or higher
    """
    if current_user.role not in ['TEAM_LEAD', 'CISO']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to delete engagements"
        )
    
    service = EngagementService(db)
    engagement = service.get_engagement(engagement_id)
    
    if not engagement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Engagement not found"
        )
    
    service.soft_delete_engagement(engagement)


@router.post("/{engagement_id}/start")
async def start_engagement(
    engagement_id: str,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Start an engagement (triggers host discovery)
    """
    service = EngagementService(db)
    
    engagement = service.get_engagement(engagement_id)
    if not engagement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Engagement not found"
        )
    
    # Check if engagement can be started
    if engagement.status != "approved":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Engagement must be approved before starting"
        )
    
    # Check scope validation
    if engagement.scope_validation_status != "validated":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Scope must be validated before starting"
        )
    
    # Start engagement workflow
    service.start_engagement_workflow(engagement_id, current_user.id)
    
    return {"message": "Engagement started successfully"}


@router.post("/{engagement_id}/pause")
async def pause_engagement(
    engagement_id: str,
    reason: str,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Pause an engagement
    """
    service = EngagementService(db)
    
    engagement = service.get_engagement(engagement_id)
    if not engagement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Engagement not found"
        )
    
    # Check permissions
    if not service.can_modify_engagement(current_user, engagement):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot pause this engagement"
        )
    
    service.pause_engagement(engagement, reason, current_user.id)
    
    return {"message": "Engagement paused successfully"}


@router.post("/{engagement_id}/resume")
async def resume_engagement(
    engagement_id: str,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Resume a paused engagement
    """
    service = EngagementService(db)
    
    engagement = service.get_engagement(engagement_id)
    if not engagement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Engagement not found"
        )
    
    # Check permissions
    if not service.can_modify_engagement(current_user, engagement):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot resume this engagement"
        )
    
    service.resume_engagement(engagement, current_user.id)
    
    return {"message": "Engagement resumed successfully"}


@router.post("/{engagement_id}/complete")
async def complete_engagement(
    engagement_id: str,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark an engagement as complete
    """
    service = EngagementService(db)
    
    engagement = service.get_engagement(engagement_id)
    if not engagement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Engagement not found"
        )
    
    # Check permissions
    if not service.can_modify_engagement(current_user, engagement):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot complete this engagement"
        )
    
    service.complete_engagement(engagement, current_user.id)
    
    return {"message": "Engagement completed successfully"}


@router.get("/{engagement_id}/summary")
async def get_engagement_summary(
    engagement_id: str,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get engagement summary statistics
    """
    service = EngagementService(db)
    
    engagement = service.get_engagement(engagement_id)
    if not engagement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Engagement not found"
        )
    
    summary = service.get_engagement_summary(engagement_id)
    
    return summary


@router.get("/{engagement_id}/hosts")
async def list_engagement_hosts(
    engagement_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    alive_only: bool = False,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all hosts in an engagement
    """
    service = EngagementService(db)
    
    engagement = service.get_engagement(engagement_id)
    if not engagement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Engagement not found"
        )
    
    hosts, total = service.list_hosts(
        engagement_id=engagement_id,
        skip=skip,
        limit=limit,
        alive_only=alive_only
    )
    
    return {
        "data": hosts,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/{engagement_id}/vulnerabilities")
async def list_engagement_vulnerabilities(
    engagement_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    severity: Optional[str] = None,
    status_filter: Optional[str] = None,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all vulnerabilities in an engagement
    """
    service = EngagementService(db)
    
    vulnerabilities_data, total = service.list_vulnerabilities(
        engagement_id=engagement_id,
        skip=skip,
        limit=limit,
        severity=severity,
        status=status_filter
    )
    
    return {
        "data": vulnerabilities_data,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/{engagement_id}/timeline")
async def get_engagement_timeline(
    engagement_id: str,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get engagement timeline of events
    """
    service = EngagementService(db)
    
    timeline = service.get_engagement_timeline(engagement_id)
    
    return {"events": timeline}
```

### 2.3 Approval Endpoints

#### approvals.py
```python
"""
Approval API endpoints
"""
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.approval import (
    ApprovalCreate, 
    ApprovalResponse,
    ApprovalDecision,
    ApprovalListResponse
)
from app.services.approval_service import ApprovalService
from app.services.notification_service import NotificationService
from app.api import deps

router = APIRouter()


@router.get("", response_model=ApprovalListResponse)
async def list_approvals(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status_filter: Optional[str] = None,
    approval_type: Optional[str] = None,
    engagement_id: Optional[str] = None,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(get_db)
):
    """
    List pending approvals for the current user
    """
    service = ApprovalService(db)
    
    approvals_data, total = service.list_user_approvals(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        status=status_filter,
        approval_type=approval_type,
        engagement_id=engagement_id
    )
    
    return {
        "data": approvals_data,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/{approval_id}", response_model=ApprovalResponse)
async def get_approval(
    approval_id: str,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get approval details
    """
    service = ApprovalService(db)
    
    approval = service.get_approval(approval_id)
    if not approval:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval not found"
        )
    
    return approval


@router.post("/{approval_id}/approve", response_model=ApprovalResponse)
async def approve_action(
    approval_id: str,
    decision: ApprovalDecision,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Approve or reject an approval request
    
    Requires appropriate role based on risk level
    """
    service = ApprovalService(db)
    
    approval = service.get_approval(approval_id)
    if not approval:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval not found"
        )
    
    # Check if user can approve this request
    can_approve, error = service.can_user_approve(current_user, approval)
    if not can_approve:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=error
        )
    
    # Process decision
    if decision.approve:
        result = service.approve(
            approval=approval,
            approver=current_user,
            comments=decision.comments,
            justification=decision.justification
        )
    else:
        result = service.reject(
            approval=approval,
            rejecter=current_user,
            reason=decision.reason
        )
    
    # Create notification
    notification_service = NotificationService(db)
    notification_service.notify_approval_decision(
        approval=approval,
        decision=decision.approve,
        decided_by=current_user
    )
    
    return result


@router.post("/{approval_id}/escalate")
async def escalate_approval(
    approval_id: str,
    escalate_to: str,
    reason: str,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Escalate an approval request
    """
    service = ApprovalService(db)
    
    approval = service.get_approval(approval_id)
    if not approval:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval not found"
        )
    
    service.escalate(
        approval=approval,
        escalated_by=current_user,
        escalate_to=escalate_to,
        reason=reason
    )
    
    return {"message": "Approval escalated successfully"}


@router.post("/{approval_id}/cancel")
async def cancel_approval(
    approval_id: str,
    reason: str,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancel an approval request (requester only)
    """
    service = ApprovalService(db)
    
    approval = service.get_approval(approval_id)
    if not approval:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval not found"
        )
    
    # Only requester can cancel
    if approval.requested_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the requester can cancel this approval"
        )
    
    service.cancel(approval, reason)
    
    return {"message": "Approval cancelled successfully"}


@router.get("/{approval_id}/signatures")
async def get_approval_signatures(
    approval_id: str,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all signatures for an approval
    """
    service = ApprovalService(db)
    
    signatures = service.get_approval_signatures(approval_id)
    
    return {"signatures": signatures}
```

### 2.4 Evidence Endpoints

#### evidence.py
```python
"""
Evidence API endpoints
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse

from app.db.session import get_db
from app.models.user import User
from app.schemas.evidence import EvidenceResponse, EvidenceListResponse
from app.services.evidence_service import EvidenceService
from app.api import deps

router = APIRouter()


@router.get("", response_model=EvidenceListResponse)
async def list_evidence(
    engagement_id: Optional[str] = None,
    host_id: Optional[str] = None,
    evidence_type: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(get_db)
):
    """
    List evidence files
    """
    service = EvidenceService(db)
    
    evidence_list, total = service.list_evidence(
        engagement_id=engagement_id,
        host_id=host_id,
        evidence_type=evidence_type,
        skip=skip,
        limit=limit
    )
    
    return {
        "data": evidence_list,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/{evidence_id}", response_model=EvidenceResponse)
async def get_evidence(
    evidence_id: str,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get evidence details
    """
    service = EvidenceService(db)
    
    evidence = service.get_evidence(evidence_id)
    if not evidence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evidence not found"
        )
    
    return evidence


@router.get("/{evidence_id}/download")
async def download_evidence(
    evidence_id: str,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Download evidence file
    """
    service = EvidenceService(db)
    
    evidence = service.get_evidence(evidence_id)
    if not evidence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evidence not found"
        )
    
    # Check permissions
    if not service.can_access_evidence(current_user, evidence):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this evidence"
        )
    
    # Log download
    service.log_download(evidence_id, current_user.id)
    
    # Return file
    return FileResponse(
        path=evidence.storage_path,
        filename=evidence.name,
        media_type=evidence.mime_type
    )


@router.get("/{evidence_id}/verify")
async def verify_evidence_integrity(
    evidence_id: str,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Verify evidence integrity by recalculating hash
    """
    service = EvidenceService(db)
    
    evidence = service.get_evidence(evidence_id)
    if not evidence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evidence not found"
        )
    
    verification = service.verify_integrity(evidence_id)
    
    return verification


@router.get("/{evidence_id}/custody")
async def get_chain_of_custody(
    evidence_id: str,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get chain of custody for evidence
    """
    service = EvidenceService(db)
    
    custody = service.get_chain_of_custody(evidence_id)
    
    return {"chain_of_custody": custody}
```

---

## 3. Authentication & Security

### 3.1 Security Implementation

#### security.py
```python
"""
Security utilities for authentication and authorization
"""
import os
import hashlib
import secrets
import jwt
import pyotp
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from jose import JWTError, jwt as jose_jwt

from app.core.config import settings


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(
    subject: str,
    expires_delta: Optional[timedelta] = None,
    additional_claims: Optional[Dict] = None
) -> str:
    """
    Create JWT access token
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {
        "sub": subject,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    }
    
    if additional_claims:
        to_encode.update(additional_claims)
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def create_refresh_token(
    subject: str,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create JWT refresh token
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {
        "sub": subject,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify and decode JWT token
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against hash
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash password
    """
    return pwd_context.hash(password)


def generate_mfa_secret() -> str:
    """
    Generate MFA secret
    """
    return pyotp.random_base32()


def verify_mfa_token(secret: str, token: str) -> bool:
    """
    Verify MFA TOTP token
    """
    totp = pyotp.TOTP(secret)
    return totp.verify(token, valid_window=1)


def generate_mfa_uri(secret: str, user_email: str, issuer: str = "ANPTOP") -> str:
    """
    Generate MFA setup URI for authenticator apps
    """
    totp = pyotp.totp.TOTP(secret)
    return totp.provisioning_uri(name=user_email, issuer_name=issuer)


def generate_api_key() -> tuple:
    """
    Generate API key and hash
    """
    key = secrets.token_urlsafe(32)
    key_hash = hashlib.shahexdigest()
    return key256(key.encode())., key_hash


def hash_api_key(key: str) -> str:
    """
    Hash API key
    """
    return hashlib.sha256(key.encode()).hexdigest()


def verify_api_key(key: str, key_hash: str) -> bool:
    """
    Verify API key against hash
    """
    return hashlib.sha256(key.encode()).hexdigest() == key_hash
```

### 3.2 Permissions

#### permissions.py
```python
"""
Role-based access control implementation
"""
from typing import List, Optional
from enum import Enum
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from app.api import deps


class Role(Enum):
    VIEWER = "VIEWER"
    ANALYST = "ANALYST"
    SENIOR_ANALYST = "SENIOR_ANALYST"
    ENGAGEMENT_MANAGER = "ENGAGEMENT_MANAGER"
    AUDITOR = "AUDITOR"
    TEAM_LEAD = "TEAM_LEAD"
    CISO = "CISO"


# Role hierarchy
ROLE_LEVELS = {
    "VIEWER": 1,
    "ANALYST": 2,
    "SENIOR_ANALYST": 3,
    "ENGAGEMENT_MANAGER": 3,
    "AUDITOR": 3,
    "TEAM_LEAD": 4,
    "CISO": 5,
}


def require_role(allowed_roles: List[str]):
    """
    Dependency factory for role-based access control
    
    Usage:
        @router.post("/admin")
        async def admin_endpoint(user: User = Depends(require_role(["CISO"]))):
            pass
    """
    def role_checker(
        current_user: User = Depends(deps.get_current_user),
        db: Session = Depends(get_db)
    ):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of roles: {', '.join(allowed_roles)}"
            )
        return current_user
    
    return role_checker


def require_min_level(min_level: int):
    """
    Dependency factory for minimum role level
    
    Usage:
        @router.post("/scan")
        async def scan_endpoint(user: User = Depends(require_min_level(2))):
            pass
    """
    def level_checker(
        current_user: User = Depends(deps.get_current_user),
        db: Session = Depends(get_db)
    ):
        if ROLE_LEVELS.get(current_user.role, 0) < min_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Minimum role level {min_level} required"
            )
        return current_user
    
    return level_checker


def require_approval_for_exploitation():
    """
    Dependency to require exploitation approval
    """
    async def exploitation_checker(
        current_user: User = Depends(deps.get_current_user),
        db: Session = Depends(get_db)
    ):
        # Exploitation requires SENIOR_ANALYST or higher
        if ROLE_LEVELS.get(current_user.role, 0) < 3:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Exploitation requires SENIOR_ANALYST role or higher"
            )
        return current_user
    
    return exploitation_checker


def require_critical_approval():
    """
    Dependency for critical actions (CISO/TEAM_LEAD only)
    """
    async def critical_checker(
        current_user: User = Depends(deps.get_current_user),
        db: Session = Depends(get_db)
    ):
        if current_user.role not in ["CISO", "TEAM_LEAD"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Critical action requires TEAM_LEAD or CISO role"
            )
        return current_user
    
    return critical_checker


def can_access_engagement(user: User, engagement) -> bool:
    """
    Check if user can access an engagement
    """
    # Admins can access all
    if user.role in ["CISO", "TEAM_LEAD", "AUDITOR"]:
        return True
    
    # Check if user is owner or team member
    if engagement.created_by == user.id:
        return True
    
    if user.id in engagement.team_members:
        return True
    
    return False


def can_modify_engagement(user: User, engagement) -> bool:
    """
    Check if user can modify an engagement
    """
    # Only certain roles can modify
    if user.role == "VIEWER":
        return False
    
    # Owner can always modify
    if engagement.created_by == user.id:
        return True
    
    # Team leads can modify team engagements
    if user.role in ["TEAM_LEAD", "CISO"]:
        return True
    
    return False
```

---

## 4. Core Services

### 4.1 Engagement Service

#### engagement_service.py
```python
"""
Engagement business logic
"""
from datetime import datetime
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc
import ipaddress

from app.models.engagement import Engagement
from app.models.host import Host
from app.models.vulnerability import Vulnerability
from app.models.audit import AuditLog
from app.schemas.engagement import EngagementCreate, EngagementUpdate


class EngagementService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_engagement(
        self,
        engagement_data: EngagementCreate,
        created_by: str
    ) -> Engagement:
        """
        Create a new engagement
        """
        engagement = Engagement(
            name=engagement_data.name,
            description=engagement_data.description,
            client_name=engagement_data.client_name,
            client_contact_name=engagement_data.client_contact_name,
            client_contact_email=engagement_data.client_contact_email,
            client_contact_phone=engagement_data.client_contact_phone,
            scope_type=engagement_data.scope_type,
            scope_targets=engagement_data.scope_targets,
            scope_exclusions=engagement_data.scope_exclusions,
            rules_of_engagement=engagement_data.rules_of_engagement,
            legal_contact_name=engagement_data.legal_contact_name,
            legal_contact_email=engagement_data.legal_contact_email,
            legal_case_number=engagement_data.legal_case_number,
            methodology=engagement_data.methodology,
            start_date=engagement_data.start_date,
            end_date=engagement_data.end_date,
            timezone=engagement_data.timezone,
            team_lead_id=engagement_data.team_lead_id,
            team_members=engagement_data.team_members,
            created_by=created_by,
            status="draft"
        )
        
        self.db.add(engagement)
        self.db.commit()
        self.db.refresh(engagement)
        
        return engagement
    
    def get_engagement(self, engagement_id: str) -> Optional[Engagement]:
        """
        Get engagement by ID
        """
        return self.db.query(Engagement).filter(
            Engagement.id == engagement_id,
            Engagement.deleted_at.is_(None)
        ).first()
    
    def list_engagements(
        self,
        skip: int = 0,
        limit: int = 100,
        status_filter: Optional[str] = None,
        client_name: Optional[str] = None
    ) -> Tuple[List[Engagement], int]:
        """
        List all engagements
        """
        query = self.db.query(Engagement).filter(
            Engagement.deleted_at.is_(None)
        )
        
        if status_filter:
            query = query.filter(Engagement.status == status_filter)
        
        if client_name:
            query = query.filter(Engagement.client_name.ilike(f"%{client_name}%"))
        
        total = query.count()
        engagements = query.order_by(
            desc(Engagement.created_at)
        ).offset(skip).limit(limit).all()
        
        return engagements, total
    
    def validate_scope(
        self,
        targets: List[str]
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate engagement scope
        """
        for target in targets:
            try:
                # Try to parse as IP range
                if "-" in target:
                    start_ip, end_ip = target.split("-")
                    ipaddress.ip_address(start_ip.strip())
                    ipaddress.ip_address(end_ip.strip())
                # Try to parse as CIDR
                elif "/" in target:
                    ipaddress.ip_network(target, strict=False)
                # Try to parse as single IP
                else:
                    ipaddress.ip_address(target)
            except ValueError as e:
                # Not an IP, could be hostname
                if not self._is_valid_hostname(target):
                    return False, f"Invalid target: {target}"
        
        return True, None
    
    def _is_valid_hostname(self, hostname: str) -> bool:
        """
        Check if hostname is valid
        """
        if len(hostname) > 255:
            return False
        if hostname[-1] == ".":
            hostname = hostname[:-1]
        allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
        return all(allowed.match(x) for x in hostname.split("."))
    
    def start_engagement_workflow(self, engagement_id: str, user_id: str):
        """
        Trigger n8n workflow for engagement
        """
        # Call n8n webhook to start host discovery
        # This would integrate with the n8n service
        pass
    
    def pause_engagement(
        self,
        engagement: Engagement,
        reason: str,
        user_id: str
    ):
        """
        Pause engagement
        """
        engagement.status = "paused"
        engagement.updated_at = datetime.utcnow()
        
        self.db.commit()
        
        self.create_audit_log(
            engagement_id=engagement.id,
            user_id=user_id,
            action="pause",
            details={"reason": reason}
        )
    
    def resume_engagement(
        self,
        engagement: Engagement,
        user_id: str
    ):
        """
        Resume engagement
        """
        engagement.status = "in_progress"
        engagement.updated_at = datetime.utcnow()
        
        self.db.commit()
        
        self.create_audit_log(
            engagement_id=engagement.id,
            user_id=user_id,
            action="resume",
            details={}
        )
    
    def complete_engagement(
        self,
        engagement: Engagement,
        user_id: str
    ):
        """
        Complete engagement
        """
        engagement.status = "completed"
        engagement.completed_at = datetime.utcnow()
        engagement.updated_at = datetime.utcnow()
        
        self.db.commit()
        
        self.create_audit_log(
            engagement_id=engagement.id,
            user_id=user_id,
            action="complete",
            details={}
        )
    
    def get_engagement_summary(self, engagement_id: str) -> dict:
        """
        Get engagement summary statistics
        """
        hosts_count = self.db.query(Host).filter(
            Host.engagement_id == engagement_id
        ).count()
        
        alive_hosts = self.db.query(Host).filter(
            Host.engagement_id == engagement_id,
            Host.is_alive == True
        ).count()
        
        vulns = self.db.query(Vulnerability).filter(
            Vulnerability.engagement_id == engagement_id
        ).all()
        
        return {
            "total_hosts": hosts_count,
            "alive_hosts": alive_hosts,
            "total_vulnerabilities": len(vulns),
            "critical_count": sum(1 for v in vulns if v.risk_rating == "critical"),
            "high_count": sum(1 for v in vulns if v.risk_rating == "high"),
            "medium_count": sum(1 for v in vulns if v.risk_rating == "medium"),
            "low_count": sum(1 for v in vulns if v.risk_rating == "low"),
        }
    
    def create_audit_log(
        self,
        engagement_id: str,
        user_id: str,
        action: str,
        details: dict
    ):
        """
        Create audit log entry
        """
        audit_entry = AuditLog(
            engagement_id=engagement_id,
            user_id=user_id,
            action=action,
            resource_type="engagement",
            resource_id=engagement_id,
            details=details,
            timestamp=datetime.utcnow()
        )
        
        self.db.add(audit_entry)
        self.db.commit()
```

---

## 5. Database Models

### 5.1 Sample Model

#### engagement.py
```python
"""
Engagement database model
"""
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer, JSON, Enum
from sqlalchemy.dialects.postgresql import UUID, INET, ARRAY
from sqlalchemy.sql import func
from app.db.base import Base
import enum


class EngagementStatus(enum.Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"


class EngagementType(enum.Enum):
    NETWORK = "network"
    WEB_APPLICATION = "web_application"
    INTERNAL = "internal"
    EXTERNAL = "external"
    SOCIAL_ENGINEERING = "social_engineering"
    PHYSICAL = "physical"


class Engagement(Base):
    """
    Engagement model for tracking penetration testing engagements
    """
    __tablename__ = "engagements"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=func.gen_random_uuid())
    
    # Basic information
    name = Column(String(128), nullable=False)
    description = Column(Text)
    client_name = Column(String(128))
    client_contact_name = Column(String(128))
    client_contact_email = Column(String(255))
    client_contact_phone = Column(String(32))
    
    # Status and type
    status = Column(String(32), default=EngagementStatus.DRAFT.value)
    type = Column(String(32), default=EngagementType.NETWORK.value)
    methodology = Column(String(64), default="blackbox")
    
    # Scope
    scope_type = Column(String(32), nullable=False)
    scope_targets = Column(ARRAY(String), nullable=False, default=[])
    scope_exclusions = Column(ARRAY(String), nullable=False, default=[])
    scope_validation_status = Column(String(16), default="pending")
    scope_validation_result = Column(JSON)
    
    # Rules of engagement
    rules_of_engagement = Column(Text)
    legal_contact_name = Column(String(128))
    legal_contact_email = Column(String(255))
    legal_case_number = Column(String(64))
    
    # Timing
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    timezone = Column(String(32), default="UTC")
    estimated_duration_days = Column(Integer)
    
    # Risk
    impact_rating = Column(String(16))
    risk_tolerance = Column(Text)
    
    # Reporting
    report_template = Column(String(64))
    executive_summary = Column(Text)
    
    # Team
    team_lead_id = Column(UUID(as_uuid=True))
    team_members = Column(ARRAY(UUID), default=[])
    
    # Metadata
    created_by = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True))
    deleted_at = Column(DateTime(timezone=True))
    
    # Soft delete
    is_deleted = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<Engagement(id={self.id}, name='{self.name}', status='{self.status}')>"
    
    @property
    def is_active(self) -> bool:
        """Check if engagement is active"""
        return self.status in [
            EngagementStatus.IN_PROGRESS.value,
            EngagementStatus.APPROVED.value
        ]
    
    @property
    def can_be_modified(self) -> bool:
        """Check if engagement can be modified"""
        return self.status in [
            EngagementStatus.DRAFT.value,
            EngagementStatus.PENDING_APPROVAL.value
        ]
```

---

## 6. Configuration

### 6.1 Configuration File

#### config.py
```python
"""
Application configuration
"""
import os
from typing import List, Optional
from pydantic import BaseSettings, Field
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings
    """
    # Application
    APP_NAME: str = "ANPTOP"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Security
    SECRET_KEY: str = Field(..., description="Secret key for JWT encryption")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 480  # 8 hours
    
    # Password policy
    PASSWORD_MIN_LENGTH: int = 16
    PASSWORD_REQUIRE_UPPER: bool = True
    PASSWORD_REQUIRE_LOWER: bool = True
    PASSWORD_REQUIRE_NUMBER: bool = True
    PASSWORD_REQUIRE_SPECIAL: bool = True
    
    # MFA
    MFA_ENABLED: bool = True
    
    # Database
    DATABASE_URL: str = Field(
        "postgresql://user:password@localhost:5432/anptop",
        description="PostgreSQL database URL"
    )
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 40
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # n8n
    N8N_URL: str = "http://localhost:5678"
    N8N_API_KEY: Optional[str] = None
    
    # OpenVAS
    OPENVAS_HOST: str = "localhost"
    OPENVAS_PORT: int = 9392
    OPENVAS_USERNAME: str = "admin"
    OPENVAS_PASSWORD: str = "admin"
    
    # Storage
    EVIDENCE_STORAGE_PATH: str = "/tmp/anptop/evidence"
    OBJECT_STORAGE_ENDPOINT: Optional[str] = None
    OBJECT_STORAGE_BUCKET: str = "anptop-evidence"
    OBJECT_STORAGE_ACCESS_KEY: Optional[str] = None
    OBJECT_STORAGE_SECRET_KEY: Optional[str] = None
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Init database
    INIT_DB: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings
    """
    return Settings()


settings = get_settings()
```

---

## 7. Pydantic Schemas

### 7.1 Sample Schema

#### engagement.py
```python
"""
Engagement Pydantic schemas
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, HttpUrl, ConfigDict

from app.models.engagement import EngagementStatus, EngagementType


class EngagementBase(BaseModel):
    """Base engagement schema"""
    name: str = Field(..., min_length=1, max_length=128)
    description: Optional[str] = None
    client_name: Optional[str] = None
    scope_type: str = Field(..., description="Type of scope: ip_range, ip_list, domain, etc.")
    scope_targets: List[str] = Field(..., min_items=1, description="Target list")


class EngagementCreate(EngagementBase):
    """Schema for creating engagement"""
    client_contact_name: Optional[str] = None
    client_contact_email: Optional[str] = None
    client_contact_phone: Optional[str] = None
    scope_exclusions: Optional[List[str]] = []
    rules_of_engagement: Optional[str] = None
    legal_contact_name: Optional[str] = None
    legal_contact_email: Optional[str] = None
    legal_case_number: Optional[str] = None
    methodology: Optional[str] = "blackbox"
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    timezone: Optional[str] = "UTC"
    team_lead_id: Optional[str] = None
    team_members: Optional[List[str]] = []


class EngagementUpdate(BaseModel):
    """Schema for updating engagement"""
    name: Optional[str] = Field(None, min_length=1, max_length=128)
    description: Optional[str] = None
    client_name: Optional[str] = None
    scope_targets: Optional[List[str]] = None
    scope_exclusions: Optional[List[str]] = None
    rules_of_engagement: Optional[str] = None
    methodology: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    timezone: Optional[str] = None


class EngagementResponse(BaseModel):
    """Schema for engagement response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    name: str
    description: Optional[str] = None
    client_name: Optional[str] = None
    status: str
    type: str
    scope_type: str
    scope_targets: List[str]
    scope_exclusions: List[str]
    scope_validation_status: str
    methodology: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    team_lead_id: Optional[str] = None
    team_members: List[str] = []
    created_by: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class EngagementListResponse(BaseModel):
    """Schema for engagement list response"""
    data: List[EngagementResponse]
    total: int
    skip: int
    limit: int
```

---

**Document Version**: 1.0  
**Last Updated**: 2024-02-06  
**Classification**: Internal Use Only
