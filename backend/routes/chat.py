"""Chat routes for Enhanced SEO Orchestrator interaction with 6 Sub-Agents"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import logging
import uuid
from datetime import datetime, timezone

from database import get_db
from models import User, Audit, ChatMessage
from schemas import ChatMessageCreate, ChatMessageResponse
from auth import get_current_user
from seo_engine.enhanced_orchestrator import enhanced_orchestrator
from seo_engine.multi_llm_client import get_active_llm_client

router = APIRouter(prefix="/chat", tags=["Chat"])
logger = logging.getLogger(__name__)


@router.post("/", response_model=ChatMessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    message_data: ChatMessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Send a message to the enhanced SEO orchestrator with 6 specialized sub-agents"""
    # Verify audit exists and belongs to user
    result = await db.execute(
        select(Audit).where(Audit.id == message_data.audit_id)
    )
    audit = result.scalar_one_or_none()
    
    if not audit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit not found"
        )
    
    if audit.user_id != current_user.id and current_user.role != 'superadmin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this audit"
        )
    
    # Save user message
    user_message = ChatMessage(
        id=str(uuid.uuid4()),
        audit_id=message_data.audit_id,
        user_id=current_user.id,
        role="user",
        content=message_data.content,
        created_at=datetime.now(timezone.utc)
    )
    db.add(user_message)
    await db.commit()
    
    try:
        # Initialize enhanced orchestrator if needed
        if not enhanced_orchestrator.llm_client:
            await enhanced_orchestrator.initialize(db)
        
        # Prepare enhanced audit context with all data
        enhanced_context = {
            "website_url": audit.website_url,
            "overall_score": audit.overall_score,
            "checks_failed": audit.checks_failed,
            "checks_passed": audit.checks_passed,
            "pages_crawled": audit.pages_crawled,
            "competitor_count": audit.competitor_count or 0,
            "opportunities_found": audit.opportunities_found or 0,
            "anomalies_detected": audit.anomalies_detected or 0,
            "lighthouse_score": audit.lighthouse_data.get('performance_score') if audit.lighthouse_data else None,
            "has_lighthouse_data": bool(audit.lighthouse_data),
            "has_competitor_data": audit.competitor_count > 0,
            "has_opportunity_data": audit.opportunities_found > 0
        }
        
        # Use orchestrator's intelligent chat with sub-agent routing
        ai_response = await enhanced_orchestrator.chat(user_message.content, enhanced_context)
        
        # Save assistant message
        assistant_message = ChatMessage(
            id=str(uuid.uuid4()),
            audit_id=message_data.audit_id,
            user_id=current_user.id,
            role="assistant",
            content=ai_response,
            created_at=datetime.now(timezone.utc)
        )
        db.add(assistant_message)
        await db.commit()
        await db.refresh(assistant_message)
        
        return assistant_message
    
    except Exception as e:
        logger.error(f"Error in chat: {e}", exc_info=True)
        # Create fallback response
        fallback_message = ChatMessage(
            id=str(uuid.uuid4()),
            audit_id=message_data.audit_id,
            user_id=current_user.id,
            role="assistant",
            content=f"I apologize, but I encountered an error processing your request. Please try again or rephrase your question.",
            created_at=datetime.now(timezone.utc)
        )
        db.add(fallback_message)
        await db.commit()
        await db.refresh(fallback_message)
        
        return fallback_message


@router.get("/{audit_id}", response_model=List[ChatMessageResponse])
async def get_chat_history(
    audit_id: str,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get chat history for an audit"""
    # Verify audit access
    result = await db.execute(
        select(Audit).where(Audit.id == audit_id)
    )
    audit = result.scalar_one_or_none()
    
    if not audit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit not found"
        )
    
    if audit.user_id != current_user.id and current_user.role != 'superadmin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this audit"
        )
    
    # Get chat messages
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.audit_id == audit_id)
        .order_by(ChatMessage.created_at)
        .limit(limit)
    )
    messages = result.scalars().all()
    
    return messages


@router.delete("/{audit_id}")
async def clear_chat_history(
    audit_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Clear chat history for an audit"""
    # Verify audit access
    result = await db.execute(
        select(Audit).where(Audit.id == audit_id)
    )
    audit = result.scalar_one_or_none()
    
    if not audit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit not found"
        )
    
    if audit.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this audit"
        )
    
    # Delete all messages for this audit
    result = await db.execute(
        select(ChatMessage).where(ChatMessage.audit_id == audit_id)
    )
    messages = result.scalars().all()
    
    for message in messages:
        await db.delete(message)
    
    await db.commit()
    
    return {"message": "Chat history cleared successfully"}

