# app/api/v1/users.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.database.session import get_db
from app.models.user import User, ActivityLog
from app.schemas.user import (
    UserResponse, UserUpdate, UserWithOrganization,
    PasswordChange, ActivityLogResponse
)
from app.api.deps import get_current_user, require_admin
from app.core.security import verify_password, get_password_hash

router = APIRouter()


@router.get("/me", response_model=UserWithOrganization)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile with organization details"""
    return current_user


@router.put("/me", response_model=UserResponse)
def update_current_user_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user profile"""
    
    # Update fields
    update_data = user_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    
    return UserResponse.from_orm(current_user)


@router.post("/me/change-password", status_code=status.HTTP_200_OK)
def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user password"""
    
    # Verify old password
    if not verify_password(password_data.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password"
        )
    
    # Update password
    current_user.hashed_password = get_password_hash(password_data.new_password)
    db.commit()
    
    # Log activity
    activity = ActivityLog(
        user_id=current_user.id,
        action="UPDATE_PASSWORD",
        description="Password changed successfully"
    )
    db.add(activity)
    db.commit()
    
    return {"message": "Password changed successfully"}


@router.get("/", response_model=List[UserResponse])
def list_organization_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all users in the organization (admin only sees all, others see themselves)"""
    
    if current_user.is_admin:
        # Admins can see all users in their organization
        users = db.query(User).filter(
            User.organization_id == current_user.organization_id
        ).offset(skip).limit(limit).all()
    else:
        # Regular users only see themselves
        users = [current_user]
    
    return [UserResponse.from_orm(user) for user in users]


@router.get("/{user_id}", response_model=UserWithOrganization)
def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific user"""
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check permissions: can only view users in same organization
    if user.organization_id != current_user.organization_id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update a user (admin only)"""
    
    user = db.query(User).filter(
        User.id == user_id,
        User.organization_id == current_user.organization_id
    ).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update fields
    update_data = user_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    
    return UserResponse.from_orm(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Deactivate a user (admin only)"""
    
    user = db.query(User).filter(
        User.id == user_id,
        User.organization_id == current_user.organization_id
    ).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate yourself"
        )
    
    # Soft delete - deactivate instead of deleting
    user.is_active = False
    db.commit()
    
    return None


@router.get("/me/activity", response_model=List[ActivityLogResponse])
def get_user_activity(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's activity log"""
    
    activities = db.query(ActivityLog).filter(
        ActivityLog.user_id == current_user.id
    ).order_by(ActivityLog.timestamp.desc()).offset(skip).limit(limit).all()
    
    return [ActivityLogResponse.from_orm(activity) for activity in activities]


@router.get("/organization/activity", response_model=List[ActivityLogResponse])
def get_organization_activity(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, le=100),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get organization-wide activity log (admin only)"""
    
    activities = db.query(ActivityLog).join(User).filter(
        User.organization_id == current_user.organization_id
    ).order_by(ActivityLog.timestamp.desc()).offset(skip).limit(limit).all()
    
    return [ActivityLogResponse.from_orm(activity) for activity in activities]