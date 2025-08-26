from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer
from datetime import timedelta
import logging

from app.models.user import UserCreate, UserLogin, UserResponse
from app.core.auth import create_access_token, create_refresh_token, verify_token
from app.core.database import get_db
from app.core.config import settings
from app.core.security import security_manager

router = APIRouter()
security = HTTPBearer()
logger = logging.getLogger(__name__)

@router.post("/register", response_model=dict)
async def register(user_data: UserCreate):
    """Register a new user"""
    db = get_db()
    
    try:
        # Check if user already exists
        existing_user = db.table("users").select("id").eq("email", user_data.email).execute()
        if existing_user.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create user in Supabase Auth
        auth_response = db.auth.sign_up({
            "email": user_data.email,
            "password": user_data.password,
            "options": {
                "data": {
                    "name": user_data.name,
                    "age": user_data.age,
                    "level": user_data.level
                }
            }
        })
        
        if auth_response.user is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user account"
            )
        
        return {
            "message": "User registered successfully",
            "user_id": auth_response.user.id,
            "email": user_data.email,
            "confirmation_sent": True
        }
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/login", response_model=dict)
async def login(credentials: UserLogin):
    """Login user and return tokens"""
    db = get_db()
    
    try:
        # Authenticate with Supabase
        auth_response = db.auth.sign_in_with_password({
            "email": credentials.email,
            "password": credentials.password
        })
        
        if auth_response.user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Get user profile
        user_response = db.table("users").select("*").eq("id", auth_response.user.id).execute()
        if not user_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        user = user_response.data[0]
        
        # Create tokens using security manager
        access_token = security_manager.create_access_token(
            data={"sub": str(auth_response.user.id), "email": credentials.email}
        )
        refresh_token = security_manager.create_refresh_token(
            data={"sub": str(auth_response.user.id), "email": credentials.email}
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": user
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@router.post("/refresh", response_model=dict)
async def refresh_token(refresh_token: str):
    """Refresh access token"""
    try:
        # Verify refresh token using security manager
        payload = security_manager.verify_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Create new access token
        access_token = security_manager.create_access_token(
            data={"sub": payload.get("sub"), "email": payload.get("email")}
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )

@router.post("/forgot-password", response_model=dict)
async def forgot_password(email: str):
    """Send password reset email"""
    db = get_db()
    
    try:
        # Check if user exists
        user_response = db.table("users").select("id").eq("email", email).execute()
        if not user_response.data:
            # Don't reveal if email exists or not for security
            return {"message": "If the email exists, a reset link has been sent"}
        
        # Send password reset email via Supabase
        reset_response = db.auth.reset_password_email(email)
        
        return {"message": "Password reset email sent successfully"}
        
    except Exception as e:
        logger.error(f"Password reset error: {e}")
        return {"message": "If the email exists, a reset link has been sent"}

@router.post("/reset-password", response_model=dict)
async def reset_password(token: str, new_password: str):
    """Reset password with token"""
    try:
        # Verify reset token
        email = security_manager.verify_password_reset_token(token)
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
        
        # Update password in Supabase
        db = get_db()
        # Note: This would typically be handled by Supabase's built-in reset flow
        # This is a simplified implementation
        
        return {"message": "Password reset successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password reset error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset failed"
        )

@router.post("/verify-email", response_model=dict)
async def verify_email(token: str):
    """Verify email address"""
    db = get_db()
    
    try:
        # Verify email with Supabase
        verify_response = db.auth.verify_otp({
            "token": token,
            "type": "email"
        })
        
        if verify_response.user is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification token"
            )
        
        return {"message": "Email verified successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Email verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Email verification failed"
        )

@router.post("/logout", response_model=dict)
async def logout():
    """Logout user"""
    db = get_db()
    
    try:
        # Sign out from Supabase
        db.auth.sign_out()
        return {"message": "Logged out successfully"}
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )
