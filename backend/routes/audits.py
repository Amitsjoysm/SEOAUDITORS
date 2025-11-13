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
from seo_engine import crawl_website, run_all_checks
from seo_engine.orchestrator import SEOOrchestrator

router = APIRouter(prefix="/audits", tags=["Audits"])
logger = logging.getLogger(__name__)


async def process_audit(audit_id: str, website_url: str, max_pages: int):
    """Background task to process audit"""
    from database import AsyncSessionLocal
    
    async with AsyncSessionLocal() as db:
        try:
            # Get audit
            result = await db.execute(select(Audit).where(Audit.id == audit_id))
            audit = result.scalar_one()
            
            # Update status to crawling
            audit.status = AuditStatus.CRAWLING
            await db.commit()
            
            # Crawl website
            logger.info(f"Starting crawl for {website_url}")
            pages = await crawl_website(website_url, max_pages=max_pages)
            
            audit.pages_crawled = len(pages)
            audit.status = AuditStatus.ANALYZING
            await db.commit()
            
            # Run SEO checks
            logger.info(f"Running SEO checks for audit {audit_id}")
            check_results = run_all_checks(pages)
            
            # Save results
            passed = 0
            failed = 0
            warning = 0
            total_impact = 0
            
            for check_result in check_results:
                result_obj = AuditResult(
                    id=str(uuid.uuid4()),
                    audit_id=audit_id,
                    category=check_result.get('category', 'Unknown'),
                    check_name=check_result.get('check_name', ''),
                    status=CheckStatus(check_result.get('status', 'info')),
                    impact_score=check_result.get('impact_score', 50),
                    current_value=check_result.get('current_value', ''),
                    recommended_value=check_result.get('recommended_value', ''),
                    pros=check_result.get('pros', []),
                    cons=check_result.get('cons', []),
                    ranking_impact=check_result.get('ranking_impact', ''),
                    solution=check_result.get('solution', ''),
                    enhancements=check_result.get('enhancements', []),
                    details=check_result.get('details', {})
                )
                db.add(result_obj)
                
                # Count statuses
                if result_obj.status == CheckStatus.PASS:
                    passed += 1
                elif result_obj.status == CheckStatus.FAIL:
                    failed += 1
                    total_impact += result_obj.impact_score
                elif result_obj.status == CheckStatus.WARNING:
                    warning += 1
                    total_impact += result_obj.impact_score * 0.5
            
            # Calculate overall score (0-100)
            total_checks = len(check_results)
            if total_checks > 0:
                # Score based on passed checks and impact of failed checks
                base_score = (passed / total_checks) * 100
                penalty = (total_impact / total_checks) * 0.3  # Impact penalty
                overall_score = max(0, min(100, base_score - penalty))
            else:
                overall_score = 0
            
            # Update audit
            audit.status = AuditStatus.COMPLETED
            audit.total_checks_run = total_checks
            audit.checks_passed = passed
            audit.checks_failed = failed
            audit.checks_warning = warning
            audit.overall_score = round(overall_score, 1)
            audit.completed_at = datetime.now(timezone.utc)
            audit.metadata = {
                'crawl_time': sum(p.load_time for p in pages),
                'avg_load_time': sum(p.load_time for p in pages) / len(pages) if pages else 0
            }
            
            await db.commit()
            
            logger.info(f"Audit {audit_id} completed. Score: {overall_score:.1f}")
            
        except Exception as e:
            logger.error(f"Error processing audit {audit_id}: {str(e)}")
            # Update audit status to failed
            result = await db.execute(select(Audit).where(Audit.id == audit_id))
            audit = result.scalar_one_or_none()
            if audit:
                audit.status = AuditStatus.FAILED
                audit.error_message = str(e)
                await db.commit()


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
    
    # Start background processing
    background_tasks.add_task(
        process_audit,
        audit.id,
        audit_data.website_url,
        subscription.plan.max_pages_per_audit
    )
    
    logger.info(f"Audit created: {audit.id} for {audit_data.website_url}")
    
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
        "metadata": audit.metadata or {}
    }
    
    return audit_dict
