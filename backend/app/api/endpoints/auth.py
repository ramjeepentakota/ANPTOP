"""
ANPTOP Backend - Authentication Endpoints
"""

from datetime import timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordRequestForm, SecurityScopes
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr

from app.db.session import get_db
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    get_current_user,
    get_current_active_user,
    generate_mfa_secret,
    get_mfa_uri,
    generate_mfa_qr_code,
    verify_mfa_token,
    generate_api_key,
    hash_api_key,
)
from app.models.user import User, UserRole
from app.core.config import settings


router = APIRouter()


# Pydantic schemas
class Token(BaseModel):
    """Token response schema."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Token payload data."""
    email: Optional[EmailStr] = None
    user_id: Optional[int] = None
    scopes: list[str] = []


class UserLogin(BaseModel):
    """User login schema."""
    email: EmailStr
    password: str
    mfa_token: Optional[str] = None


class UserCreate(BaseModel):
    """User creation schema."""
    email: EmailStr
    username: str
    password: str
    full_name: str
    role: Optional[UserRole] = UserRole.TESTER


class UserResponse(BaseModel):
    """User response schema."""
    id: int
    email: str
    username: str
    full_name: str
    role: UserRole
    is_active: bool
    mfa_enabled: bool
    
    class Config:
        from_attributes = True


class MFAEnableResponse(BaseModel):
    """MFA enable response schema."""
    secret: str
    qr_code: str
    message: str


class MFAVerifyResponse(BaseModel):
    """MFA verification response schema."""
    verified: bool
    message: str


@router.post("/login", response_model=Token)
async def login(
    form_data: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    """
    Authenticate user and return JWT tokens.
    
    Supports:
    - Email/password authentication
    - MFA verification (TOTP)
    - API key authentication (for service accounts)
    """
    # Get user by email
    user = await User.get_by_email(db, form_data.email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )
    
    # Verify MFA if enabled
    if user.mfa_enabled and form_data.mfa_token:
        if not user.mfa_secret:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MFA is enabled but no secret found",
            )
        
        if not verify_mfa_token(user.mfa_secret, form_data.mfa_token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid MFA token",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    # Create tokens
    scopes = user.get_scopes()
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    access_token = create_access_token(
        data={"sub": user.id, "email": user.email, "scopes": scopes},
        expires_delta=access_token_expires,
        scopes=scopes,
    )
    
    refresh_token = create_refresh_token(data={"sub": user.id})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Refresh access token using refresh token.
    """
    from app.core.security import decode_token
    
    try:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
        
        user = await User.get_by_id(db, user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )
        
        scopes = user.get_scopes()
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        access_token = create_access_token(
            data={"sub": user.id, "email": user.email, "scopes": scopes},
            expires_delta=access_token_expires,
            scopes=scopes,
        )
        
        new_refresh_token = create_refresh_token(data={"sub": user.id})
        
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not refresh token: {str(e)}",
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
):
    """Get current authenticated user information."""
    return current_user


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new user.
    
    Note: In production, this should be restricted to admins only.
    """
    # Check if email already exists
    existing_user = await User.get_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Check if username already exists
    existing_username = await User.get_by_username(db, user_data.username)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )
    
    # Create user
    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        role=user_data.role,
        is_active=True,
        mfa_secret=None,
        mfa_enabled=False,
    )
    
    await user.save(db)
    
    return user


@router.post("/mfa/setup", response_model=MFAEnableResponse)
async def setup_mfa(
    current_user: User = Depends(get_current_active_user),
):
    """
    Setup MFA for current user.
    Returns TOTP secret and QR code for authenticator app.
    """
    if current_user.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA is already enabled",
        )
    
    # Generate new secret
    secret = generate_mfa_secret()
    
    # Generate QR code URI
    uri = get_mfa_uri(secret, current_user.email)
    qr_code = generate_mfa_qr_code(uri)
    
    return {
        "secret": secret,
        "qr_code": qr_code,
        "message": "Scan this QR code with your authenticator app",
    }


@router.post("/mfa/enable", response_model=MFAVerifyResponse)
async def enable_mfa(
    token: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Enable MFA after verification.
    """
    if not current_user.mfa_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA not setup. Call /mfa/setup first.",
        )
    
    if not verify_mfa_token(current_user.mfa_secret, token):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid MFA token",
        )
    
    # Enable MFA
    current_user.mfa_enabled = True
    await current_user.update(db)
    
    return {
        "verified": True,
        "message": "MFA enabled successfully",
    }


@router.post("/mfa/disable", response_model=MFAVerifyResponse)
async def disable_mfa(
    token: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Disable MFA for current user.
    Requires MFA verification.
    """
    if not current_user.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA is not enabled",
        )
    
    if not verify_mfa_token(current_user.mfa_secret, token):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid MFA token",
        )
    
    # Disable MFA
    current_user.mfa_enabled = False
    current_user.mfa_secret = None
    await current_user.update(db)
    
    return {
        "verified": True,
        "message": "MFA disabled successfully",
    }


@router.post("/change-password")
async def change_password(
    old_password: str,
    new_password: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Change user password.
    """
    # Verify old password
    if not verify_password(old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password",
        )
    
    # Update password
    current_user.hashed_password = get_password_hash(new_password)
    await current_user.update(db)
    
    return {"message": "Password changed successfully"}


@router.post("/api-key/generate")
async def generate_api_key_endpoint(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate API key for current user.
    Only available for API role users.
    """
    if current_user.role != UserRole.API:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only API users can generate API keys",
        )
    
    api_key = generate_api_key()
    current_user.api_key = api_key
    current_user.api_key_hash = hash_api_key(api_key)
    await current_user.update(db)
    
    return {
        "api_key": api_key,
        "message": "Save this API key. It will not be shown again.",
    }


@router.post("/logout")
async def logout():
    """
    Logout endpoint.
    
    Note: In a stateless JWT setup, logout is handled client-side.
    For stateful sessions, implement session invalidation here.
    """
    return {"message": "Successfully logged out"}
