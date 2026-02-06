"""
Competitor Analysis Routes
Analyze competitors, find keyword gaps, identify opportunities
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from pydantic import BaseModel
from datetime import datetime

from database import get_db
from auth import get_current_user
from models import User, Audit, CompetitorAnalysis

router = APIRouter(prefix="/audits/{audit_id}/competitors", tags=["Competitors"])


# Schemas
class CompetitorResponse(BaseModel):
    id: str
    competitor_url: str
    competitor_domain: str | None
    competitor_score: float | None
    domain_authority: float | None
    backlink_count: int | None
    referring_domains: int | None
    organic_traffic_estimate: int | None
    keyword_overlap: dict | None
    keyword_gaps: dict | None
    strengths: dict | None
    weaknesses: dict | None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Routes
@router.get("/", response_model=List[CompetitorResponse])
async def list_competitors(
    audit_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all competitors for an audit"""
    # Verify audit belongs to user
    audit_result = await db.execute(
        select(Audit).where(
            Audit.id == audit_id,
            Audit.user_id == current_user.id
        )
    )
    audit = audit_result.scalar_one_or_none()
    
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    
    # Get competitors
    result = await db.execute(
        select(CompetitorAnalysis)
        .where(CompetitorAnalysis.audit_id == audit_id)
        .order_by(CompetitorAnalysis.competitor_score.desc())
    )
    competitors = result.scalars().all()
    
    return [CompetitorResponse.from_orm(comp) for comp in competitors]


@router.get("/{competitor_id}", response_model=CompetitorResponse)
async def get_competitor(
    audit_id: str,
    competitor_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed competitor analysis"""
    # Verify audit belongs to user
    audit_result = await db.execute(
        select(Audit).where(
            Audit.id == audit_id,
            Audit.user_id == current_user.id
        )
    )
    audit = audit_result.scalar_one_or_none()
    
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    
    # Get competitor
    result = await db.execute(
        select(CompetitorAnalysis).where(
            CompetitorAnalysis.id == competitor_id,
            CompetitorAnalysis.audit_id == audit_id
        )
    )
    competitor = result.scalar_one_or_none()
    
    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found")
    
    return CompetitorResponse.from_orm(competitor)


@router.get("/{competitor_id}/keyword-gaps")
async def get_keyword_gaps(
    audit_id: str,
    competitor_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get keyword gaps between your site and competitor"""
    # Verify audit belongs to user
    audit_result = await db.execute(
        select(Audit).where(
            Audit.id == audit_id,
            Audit.user_id == current_user.id
        )
    )
    audit = audit_result.scalar_one_or_none()
    
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    
    # Get competitor
    result = await db.execute(
        select(CompetitorAnalysis).where(
            CompetitorAnalysis.id == competitor_id,
            CompetitorAnalysis.audit_id == audit_id
        )
    )
    competitor = result.scalar_one_or_none()
    
    if not competitor:
        raise HTTPException(status_code=404, detail="Competitor not found")
    
    # Return keyword gaps
    keyword_gaps = competitor.keyword_gaps or []
    
    # Sort by opportunity (search volume / difficulty)
    if isinstance(keyword_gaps, list):
        keyword_gaps.sort(
            key=lambda x: (x.get('search_volume', 0) / max(x.get('difficulty', 1), 1)),
            reverse=True
        )
    
    return {
        "audit_id": audit_id,
        "competitor_id": competitor_id,
        "competitor_domain": competitor.competitor_domain,
        "keyword_gaps": keyword_gaps[:50],  # Top 50 opportunities
        "total_gaps": len(keyword_gaps) if isinstance(keyword_gaps, list) else 0
    }


@router.post("/analyze")
async def analyze_competitor(
    audit_id: str,
    competitor_url: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Analyze a new competitor (runs async)"""
    # Verify audit belongs to user
    audit_result = await db.execute(
        select(Audit).where(
            Audit.id == audit_id,
            Audit.user_id == current_user.id
        )
    )
    audit = audit_result.scalar_one_or_none()
    
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    
    # Create placeholder competitor entry
    from urllib.parse import urlparse
    domain = urlparse(competitor_url).netloc
    
    new_competitor = CompetitorAnalysis(
        audit_id=audit_id,
        competitor_url=competitor_url,
        competitor_domain=domain,
        data_source="dataforseo"
    )
    
    db.add(new_competitor)
    await db.commit()
    await db.refresh(new_competitor)
    
    # TODO: Trigger background task to analyze competitor
    # For now, return placeholder
    
    return {
        "message": "Competitor analysis started",
        "competitor_id": new_competitor.id,
        "status": "analyzing"
    }
