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
        
        # Determine which sub-agent(s) to use based on user query
        user_query_lower = message_data.content.lower()
        
        # Route to appropriate sub-agent(s)
        if any(word in user_query_lower for word in ['competitor', 'competition', 'rival', 'vs']):
            # Use Competitor Analysis Agent
            agent = enhanced_orchestrator.sub_agents.get('competitor')
            agent_context = {
                'url': audit.website_url,
                'competitor_data': audit.serp_data or {},
                'serp_data': audit.serp_data or {}
            }
            result = await agent.analyze(agent_context) if agent else None
            ai_response = result.get('analysis', 'Competitor analysis not available') if result else 'Agent unavailable'
            
        elif any(word in user_query_lower for word in ['content', 'keyword', 'topic', 'write', 'article']):
            # Use Content Optimization Agent
            agent = enhanced_orchestrator.sub_agents.get('content')
            agent_context = {
                'url': audit.website_url,
                'crawl_data': {'pages': []},  # Simplified
                'keyword_data': audit.keyword_data or {}
            }
            result = await agent.analyze(agent_context) if agent else None
            ai_response = result.get('analysis', 'Content analysis not available') if result else 'Agent unavailable'
            
        elif any(word in user_query_lower for word in ['backlink', 'link', 'linking', 'authority']):
            # Use Backlink Analysis Agent
            agent = enhanced_orchestrator.sub_agents.get('backlink')
            agent_context = {
                'url': audit.website_url,
                'backlink_data': audit.backlink_data or {}
            }
            result = await agent.analyze(agent_context) if agent else None
            ai_response = result.get('analysis', 'Backlink analysis not available') if result else 'Agent unavailable'
            
        elif any(word in user_query_lower for word in ['performance', 'speed', 'slow', 'fast', 'web vitals', 'cwv']):
            # Use Performance Agent
            agent = enhanced_orchestrator.sub_agents.get('performance')
            agent_context = {
                'url': audit.website_url,
                'lighthouse_data': audit.lighthouse_data or {}
            }
            result = await agent.analyze(agent_context) if agent else None
            ai_response = result.get('analysis', 'Performance analysis not available') if result else 'Agent unavailable'
            
        elif any(word in user_query_lower for word in ['technical', 'crawl', 'index', 'robots', 'sitemap']):
            # Use Technical SEO Agent
            agent = enhanced_orchestrator.sub_agents.get('technical')
            agent_context = {
                'url': audit.website_url,
                'crawl_data': {'pages': []},
                'lighthouse_data': audit.lighthouse_data or {}
            }
            result = await agent.analyze(agent_context) if agent else None
            ai_response = result.get('analysis', 'Technical analysis not available') if result else 'Agent unavailable'
            
        else:
            # Use general LLM for generic questions
            llm_client = await get_active_llm_client(db)
            
            # Build context from audit data
            context_prompt = f"""You are an expert SEO consultant. Answer the user's question about their website.

Website: {audit.website_url}
Overall SEO Score: {audit.overall_score}/100
Pages Crawled: {audit.pages_crawled}
Checks Passed: {audit.checks_passed}
Checks Failed: {audit.checks_failed}

User Question: {message_data.content}

Provide a helpful, specific answer focused on improving their SEO and ranking higher in both search engines and LLM recommendations (Claude, GPT, Gemini). Keep response under 300 words."""
            
            ai_response = llm_client.generate(context_prompt, max_tokens=500)
        
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
    
    # Clear orchestrator
    if audit_id in orchestrators:
        del orchestrators[audit_id]
    
    return {"message": "Chat history cleared successfully"}
