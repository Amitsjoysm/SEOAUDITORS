"""Audit routes"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, extract
from typing import List
import logging
import uuid
from datetime import datetime, timezone
import asyncio

from database import get_db
from models import User, Audit, AuditResult, AuditStatus, Subscription, CheckStatus
from schemas import AuditCreate, AuditResponse, AuditDetailResponse, AuditResultResponse
from auth import get_current_user
from seo_engine.audit_processor import process_audit_background_task

router = APIRouter(prefix="/audits", tags=["Audits"])
logger = logging.getLogger(__name__)


@router.post("/", response_model=AuditResponse, status_code=status.HTTP_201_CREATED)
async def create_audit(
    audit_data: AuditCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new SEO audit"""
    # Check user's subscription and usage limits
    result = await db.execute(
        select(Subscription)
        .where(
            and_(
                Subscription.user_id == current_user.id,
                Subscription.status == 'active'
            )
        )
        .order_by(Subscription.created_at.desc())
    )
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No active subscription found"
        )
    
    # Check if user has reached audit limit
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    result = await db.execute(
        select(func.count(Audit.id))
        .where(
            and_(
                Audit.user_id == current_user.id,
                extract('month', Audit.created_at) == current_month,
                extract('year', Audit.created_at) == current_year
            )
        )
    )
    audits_this_month = result.scalar()
    
    # Get plan details
    from sqlalchemy.orm import selectinload
    result = await db.execute(
        select(Subscription)
        .options(selectinload(Subscription.plan))
        .where(Subscription.id == subscription.id)
    )
    subscription = result.scalar_one()
    
    if audits_this_month >= subscription.plan.max_audits_per_month:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Monthly audit limit reached ({subscription.plan.max_audits_per_month}). Upgrade your plan for more audits."
        )
    
    # Create audit
    audit = Audit(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        website_url=audit_data.website_url,
        status=AuditStatus.PENDING
    )
    
    db.add(audit)
    await db.commit()
    await db.refresh(audit)
    
    # Start background processing with enhanced orchestrator
    background_tasks.add_task(
        process_audit_background_task,
        audit.id,
        audit_data.website_url,
        subscription.plan.max_pages_per_audit
    )
    
    logger.info(f"✨ Enhanced audit created: {audit.id} for {audit_data.website_url}")
    logger.info(f"🤖 Will use: DataForSEO + Lighthouse + 6 Sub-Agents")
    
    return audit


@router.get("/", response_model=List[AuditResponse])
async def get_user_audits(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's audits"""
    result = await db.execute(
        select(Audit)
        .where(Audit.user_id == current_user.id)
        .order_by(Audit.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    audits = result.scalars().all()
    return audits


@router.get("/{audit_id}", response_model=AuditDetailResponse)
async def get_audit_detail(
    audit_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed audit results"""
    # Get audit
    result = await db.execute(
        select(Audit).where(Audit.id == audit_id)
    )
    audit = result.scalar_one_or_none()
    
    if not audit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit not found"
        )
    
    # Check ownership (superadmins can see all)
    if audit.user_id != current_user.id and current_user.role != 'superadmin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this audit"
        )
    
    # Get results
    result = await db.execute(
        select(AuditResult)
        .where(AuditResult.audit_id == audit_id)
        .order_by(AuditResult.impact_score.desc())
    )
    results = result.scalars().all()
    
    # Build response
    audit_dict = {
        "id": audit.id,
        "user_id": audit.user_id,
        "website_url": audit.website_url,
        "status": audit.status,
        "pages_crawled": audit.pages_crawled,
        "total_checks_run": audit.total_checks_run,
        "checks_passed": audit.checks_passed,
        "checks_failed": audit.checks_failed,
        "checks_warning": audit.checks_warning,
        "overall_score": audit.overall_score,
        "error_message": audit.error_message,
        "created_at": audit.created_at,
        "completed_at": audit.completed_at,
        "results": results,
        "metadata": audit.audit_metadata or {}
    }
    
    return audit_dict



@router.get("/{audit_id}/analytics")
async def get_audit_analytics(
    audit_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed analytics and scoring for an audit"""
    # Get audit
    result = await db.execute(
        select(Audit).where(Audit.id == audit_id)
    )
    audit = result.scalar_one_or_none()
    
    if not audit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit not found"
        )
    
    # Check ownership (superadmins can see all)
    if audit.user_id != current_user.id and current_user.role != 'superadmin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this audit"
        )
    
    # Get all results to generate priority roadmap
    result = await db.execute(
        select(AuditResult)
        .where(AuditResult.audit_id == audit_id)
    )
    results = result.scalars().all()
    
    # Convert results to dict format
    check_results = []
    for r in results:
        check_results.append({
            'check_name': r.check_name,
            'category': r.category,
            'status': r.status.value,
            'impact_score': r.impact_score,
            'ranking_impact': r.ranking_impact,
            'solution': r.solution,
            'enhancements': r.enhancements or []
        })
    
    # Generate priority roadmap
    from seo_engine.analytics_scoring import SEOScoreCalculator
    calculator = SEOScoreCalculator()
    roadmap = calculator.generate_priority_roadmap(check_results)
    
    # Return complete analytics
    return {
        'overall_score': audit.overall_score,
        'potential_score': audit.potential_score,
        'score_gap': (audit.potential_score or audit.overall_score) - (audit.overall_score or 0),
        'grade': audit.score_grade,
        'interpretation': audit.score_interpretation,
        'category_scores': audit.category_scores or [],
        'executive_summary': audit.analytics_summary or {},
        'priority_roadmap': roadmap,
        'status_distribution': {
            'passed': audit.checks_passed,
            'warnings': audit.checks_warning,
            'failed': audit.checks_failed,
            'total': audit.total_checks_run
        }
    }
