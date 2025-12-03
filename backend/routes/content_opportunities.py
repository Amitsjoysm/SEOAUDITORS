"""
Content Opportunities Routes
AI-generated content recommendations, keyword opportunities, content briefs
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from pydantic import BaseModel
from datetime import datetime

from database import get_db
from auth import get_current_user
from models import User, Audit, ContentOpportunity, OpportunityType

router = APIRouter(prefix="/audits/{audit_id}/opportunities", tags=["Content Opportunities"])


# Schemas
class ContentOpportunityResponse(BaseModel):
    id: str
    opportunity_type: str
    keyword: str | None
    current_position: int | None
    target_position: int | None
    search_volume: int | None
    keyword_difficulty: float | None
    potential_traffic: int | None
    competition_level: str | None
    priority_score: float | None
    estimated_effort_hours: float | None
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class ContentOpportunityDetail(ContentOpportunityResponse):
    content_brief: str | None
    recommended_word_count: int | None
    recommended_headings: dict | None
    related_keywords: dict | None
    competitor_analysis: dict | None
    ai_recommendations: str | None
    cpc_value: float | None


class GenerateOpportunitiesRequest(BaseModel):
    focus_area: str = "all"  # all, technical, content, keywords


# Routes
@router.get("/", response_model=List[ContentOpportunityResponse])
async def list_opportunities(
    audit_id: str,
    opportunity_type: OpportunityType | None = None,
    status: str | None = None,
    min_priority: float | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all content opportunities for an audit"""
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
    
    # Build query
    query = select(ContentOpportunity).where(ContentOpportunity.audit_id == audit_id)
    
    if opportunity_type:
        query = query.where(ContentOpportunity.opportunity_type == opportunity_type)
    
    if status:
        query = query.where(ContentOpportunity.status == status)
    
    if min_priority:
        query = query.where(ContentOpportunity.priority_score >= min_priority)
    
    query = query.order_by(ContentOpportunity.priority_score.desc())
    
    result = await db.execute(query)
    opportunities = result.scalars().all()
    
    return [ContentOpportunityResponse.from_orm(opp) for opp in opportunities]


@router.get("/{opportunity_id}", response_model=ContentOpportunityDetail)
async def get_opportunity(
    audit_id: str,
    opportunity_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed content opportunity with brief"""
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
    
    # Get opportunity
    result = await db.execute(
        select(ContentOpportunity).where(
            ContentOpportunity.id == opportunity_id,
            ContentOpportunity.audit_id == audit_id
        )
    )
    opportunity = result.scalar_one_or_none()
    
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    return ContentOpportunityDetail.from_orm(opportunity)


@router.post("/generate")
async def generate_opportunities(
    audit_id: str,
    request: GenerateOpportunitiesRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate AI-powered content opportunities"""
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
    
    # TODO: Trigger background task to generate opportunities using enhanced orchestrator
    # For now, return placeholder
    
    return {
        "message": "Content opportunity generation started",
        "audit_id": audit_id,
        "focus_area": request.focus_area,
        "status": "generating"
    }


@router.post("/{opportunity_id}/generate-brief")
async def generate_content_brief(
    audit_id: str,
    opportunity_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate detailed content brief for an opportunity"""
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
    
    # Get opportunity
    result = await db.execute(
        select(ContentOpportunity).where(
            ContentOpportunity.id == opportunity_id,
            ContentOpportunity.audit_id == audit_id
        )
    )
    opportunity = result.scalar_one_or_none()
    
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    # Generate brief using enhanced orchestrator
    from seo_engine.enhanced_orchestrator import enhanced_orchestrator
    
    brief_result = await enhanced_orchestrator.generate_content_brief(
        keyword=opportunity.keyword or "",
        competitor_data=opportunity.competitor_analysis or {},
        keyword_data={
            "search_volume": opportunity.search_volume,
            "difficulty": opportunity.keyword_difficulty,
            "cpc": opportunity.cpc_value
        }
    )
    
    if brief_result.get('success'):
        opportunity.content_brief = brief_result['brief']
        await db.commit()
        await db.refresh(opportunity)
        
        return {
            "message": "Content brief generated successfully",
            "brief": brief_result['brief']
        }
    else:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate brief: {brief_result.get('error')}"
        )


@router.put("/{opportunity_id}/status")
async def update_opportunity_status(
    audit_id: str,
    opportunity_id: str,
    status: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update opportunity status (pending, in_progress, completed, dismissed)"""
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
    
    # Get opportunity
    result = await db.execute(
        select(ContentOpportunity).where(
            ContentOpportunity.id == opportunity_id,
            ContentOpportunity.audit_id == audit_id
        )
    )
    opportunity = result.scalar_one_or_none()
    
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    # Validate status
    valid_statuses = ["pending", "in_progress", "completed", "dismissed"]
    if status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )
    
    opportunity.status = status
    await db.commit()
    
    return {
        "message": "Status updated successfully",
        "opportunity_id": opportunity_id,
        "new_status": status
    }


@router.get("/stats/overview")
async def get_opportunities_overview(
    audit_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get overview statistics of content opportunities"""
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
    
    # Get all opportunities
    result = await db.execute(
        select(ContentOpportunity).where(ContentOpportunity.audit_id == audit_id)
    )
    opportunities = result.scalars().all()
    
    # Calculate stats
    total = len(opportunities)
    by_type = {}
    by_status = {}
    total_potential_traffic = 0
    avg_difficulty = 0
    
    for opp in opportunities:
        # By type
        opp_type = opp.opportunity_type.value if opp.opportunity_type else "unknown"
        by_type[opp_type] = by_type.get(opp_type, 0) + 1
        
        # By status
        by_status[opp.status] = by_status.get(opp.status, 0) + 1
        
        # Traffic
        if opp.potential_traffic:
            total_potential_traffic += opp.potential_traffic
        
        # Difficulty
        if opp.keyword_difficulty:
            avg_difficulty += opp.keyword_difficulty
    
    avg_difficulty = avg_difficulty / total if total > 0 else 0
    
    # Top opportunities
    top_opportunities = sorted(
        opportunities,
        key=lambda x: x.priority_score or 0,
        reverse=True
    )[:10]
    
    return {
        "total_opportunities": total,
        "by_type": by_type,
        "by_status": by_status,
        "total_potential_traffic": total_potential_traffic,
        "avg_keyword_difficulty": round(avg_difficulty, 2),
        "top_opportunities": [
            {
                "id": opp.id,
                "keyword": opp.keyword,
                "type": opp.opportunity_type.value if opp.opportunity_type else None,
                "priority_score": opp.priority_score,
                "potential_traffic": opp.potential_traffic
            }
            for opp in top_opportunities
        ]
    }
