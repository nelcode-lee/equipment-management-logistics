"""
Authentication API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import timedelta

from ..models.database import get_db
from ..models.auth_schemas import (
    UserCreate, UserResponse, UserLogin, Token, UserUpdate, 
    PasswordChange, PasswordResetRequest, PasswordResetConfirm
)
from ..models.auth_models import UserRole
from ..services.auth_service import AuthService
from ..services.auth_dependencies import (
    get_auth_service, get_current_active_user, require_admin,
    get_client_ip, get_user_agent
)

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Register a new user"""
    try:
        user = auth_service.create_user(user_data)
        return UserResponse.from_orm(user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login", response_model=Token)
async def login(
    user_credentials: UserLogin,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Login user and return access token"""
    user = auth_service.authenticate_user(
        user_credentials.username, 
        user_credentials.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(hours=24)
    access_token = auth_service.create_access_token(
        data={
            "sub": user.username,
            "user_id": user.id,
            "role": user.role.value
        },
        expires_delta=access_token_expires
    )
    
    # Create session
    client_ip = get_client_ip(request)
    user_agent = get_user_agent(request)
    auth_service.create_user_session(user.id, client_ip, user_agent)
    
    # Update last login
    auth_service.update_last_login(user.id)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": int(access_token_expires.total_seconds()),
        "user": UserResponse.from_orm(user)
    }

@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_active_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Logout user (revoke all sessions)"""
    revoked_count = auth_service.revoke_all_user_sessions(current_user.id)
    return {"message": f"Logged out successfully. {revoked_count} sessions revoked."}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user information"""
    return UserResponse.from_orm(current_user)

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Update current user information"""
    # Prevent users from changing their own role
    if user_data.role and user_data.role != current_user.role:
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot change your own role"
            )
    
    updated_user = auth_service.update_user(current_user.id, user_data)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse.from_orm(updated_user)

@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Change user password"""
    success = auth_service.change_password(
        current_user.id,
        password_data.current_password,
        password_data.new_password
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    return {"message": "Password changed successfully"}

@router.post("/request-password-reset")
async def request_password_reset(
    reset_data: PasswordResetRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Request password reset token"""
    reset_token = auth_service.create_password_reset_token(reset_data.email)
    
    if not reset_token:
        # Don't reveal if email exists or not
        return {"message": "If the email exists, a password reset link has been sent"}
    
    # In a real application, you would send this token via email
    # For now, we'll return it (remove this in production!)
    return {
        "message": "Password reset token generated",
        "reset_token": reset_token  # Remove this in production!
    }

@router.post("/reset-password")
async def reset_password(
    reset_data: PasswordResetConfirm,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Reset password using reset token"""
    success = auth_service.reset_password(
        reset_data.reset_token,
        reset_data.new_password
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    return {"message": "Password reset successfully"}

# Admin-only endpoints
@router.get("/users", response_model=list[UserResponse])
async def get_all_users(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get all users (admin only)"""
    users = db.query(User).all()
    return [UserResponse.from_orm(user) for user in users]

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    current_user: User = Depends(require_admin),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Update any user (admin only)"""
    updated_user = auth_service.update_user(user_id, user_data)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse.from_orm(updated_user)

@router.delete("/users/{user_id}")
async def deactivate_user(
    user_id: str,
    current_user: User = Depends(require_admin),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Deactivate user (admin only)"""
    user = auth_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent admin from deactivating themselves
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account"
        )
    
    user.is_active = False
    auth_service.revoke_all_user_sessions(user_id)
    
    return {"message": "User deactivated successfully"}

@router.post("/users/{user_id}/activate")
async def activate_user(
    user_id: str,
    current_user: User = Depends(require_admin),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Activate user (admin only)"""
    user = auth_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = True
    return {"message": "User activated successfully"}
