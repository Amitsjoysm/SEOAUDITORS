"""Superadmin routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, extract
from typing import List
import logging
from datetime import datetime

from database import get_db
from models import User, Audit, Subscription, UserRole
from schemas import (
    UserResponse, 
    UserUpdate, 
    AdminDashboardStats,
    AuditResponse
)
from auth import get_current_superadmin

router = APIRouter(prefix="/admin", tags=["Admin"])
logger = logging.getLogger(__name__)


@router.get("/dashboard", response_model=AdminDashboardStats)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_superadmin),
    db: AsyncSession = Depends(get_db)
):
    """Get admin dashboard statistics"""
    # Total users
    result = await db.execute(select(func.count(User.id)))
    total_users = result.scalar()
    
    # Active users (logged in last 30 days)
    result = await db.execute(
        select(func.count(User.id))
        .where(User.is_active == True)
    )
    active_users = result.scalar()
    
    # Total audits
    result = await db.execute(select(func.count(Audit.id)))
    total_audits = result.scalar()
    
    # Audits this month
    current_month = datetime.now().month
    current_year = datetime.now().year
    result = await db.execute(
        select(func.count(Audit.id))
        .where(
            and_(
                extract('month', Audit.created_at) == current_month,
                extract('year', Audit.created_at) == current_year
            )
        )
    )
    audits_this_month = result.scalar()
    
    # Active subscriptions
    result = await db.execute(
        select(func.count(Subscription.id))
        .where(Subscription.status == 'active')
    )
    active_subscriptions = result.scalar()
    
    # Average audit score
    result = await db.execute(
        select(func.avg(Audit.overall_score))
        .where(Audit.overall_score.isnot(None))
    )
    avg_score = result.scalar() or 0.0
    
    return AdminDashboardStats(
        total_users=total_users,
        active_users=active_users,
        total_audits=total_audits,
        audits_this_month=audits_this_month,
        total_revenue=0.0,  # Would calculate from Stripe data
        active_subscriptions=active_subscriptions,
        avg_audit_score=round(avg_score, 1)
    )


@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_superadmin),
    db: AsyncSession = Depends(get_db)
):
    """Get all users (superadmin only)"""
    result = await db.execute(
        select(User)
        .order_by(User.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    users = result.scalars().all()
    return users


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_superadmin),
    db: AsyncSession = Depends(get_db)
):
    """Update user (superadmin only)"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update fields
    update_data = user_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    await db.commit()
    await db.refresh(user)
    
    logger.info(f"User updated by admin: {user.email}")
    return user


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    current_user: User = Depends(get_current_superadmin),
    db: AsyncSession = Depends(get_db)
):
    """Delete user (superadmin only)"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    await db.delete(user)
    await db.commit()
    
    logger.info(f"User deleted by admin: {user.email}")
    return {"message": "User deleted successfully"}


@router.get("/audits", response_model=List[AuditResponse])
async def get_all_audits(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_superadmin),
    db: AsyncSession = Depends(get_db)
):
    """Get all audits (superadmin only)"""
    result = await db.execute(
        select(Audit)
        .order_by(Audit.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    audits = result.scalars().all()
    return audits
