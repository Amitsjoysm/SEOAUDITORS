"""Plan and subscription management routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import logging
import uuid

from database import get_db
from models import Plan, User
from schemas import PlanResponse, PlanCreate, PlanUpdate
from auth import get_current_user, get_current_superadmin

router = APIRouter(prefix="/plans", tags=["Plans"])
logger = logging.getLogger(__name__)


@router.get("/", response_model=List[PlanResponse])
async def get_plans(db: AsyncSession = Depends(get_db)):
    """Get all active plans (public)"""
    result = await db.execute(
        select(Plan)
        .where(Plan.is_active == True)
        .order_by(Plan.price)
    )
    plans = result.scalars().all()
    return plans


@router.post("/", response_model=PlanResponse)
async def create_plan(
    plan_data: PlanCreate,
    current_user: User = Depends(get_current_superadmin),
    db: AsyncSession = Depends(get_db)
):
    """Create a new plan (superadmin only)"""
    # Check if plan name already exists
    result = await db.execute(select(Plan).where(Plan.name == plan_data.name))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Plan with this name already exists"
        )
    
    plan = Plan(
        id=str(uuid.uuid4()),
        name=plan_data.name,
        display_name=plan_data.display_name,
        description=plan_data.description,
        price=plan_data.price,
        stripe_price_id=plan_data.stripe_price_id,
        max_audits_per_month=plan_data.max_audits_per_month,
        max_pages_per_audit=plan_data.max_pages_per_audit,
        features=plan_data.features,
        is_active=True
    )
    
    db.add(plan)
    await db.commit()
    await db.refresh(plan)
    
    logger.info(f"Plan created: {plan.name}")
    return plan


@router.put("/{plan_id}", response_model=PlanResponse)
async def update_plan(
    plan_id: str,
    plan_data: PlanUpdate,
    current_user: User = Depends(get_current_superadmin),
    db: AsyncSession = Depends(get_db)
):
    """Update a plan (superadmin only)"""
    result = await db.execute(select(Plan).where(Plan.id == plan_id))
    plan = result.scalar_one_or_none()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found"
        )
    
    # Update fields
    update_data = plan_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(plan, field, value)
    
    await db.commit()
    await db.refresh(plan)
    
    logger.info(f"Plan updated: {plan.name}")
    return plan
