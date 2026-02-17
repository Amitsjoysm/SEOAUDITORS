"""API Token management routes for MCP server access"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import logging
import uuid
import secrets
from datetime import datetime, timezone

from database import get_db
from models import User, APIToken
from schemas import APITokenCreate, APITokenResponse
from auth import get_current_user

router = APIRouter(prefix="/api-tokens", tags=["API Tokens"])
logger = logging.getLogger(__name__)


def generate_api_token() -> str:
    """Generate a secure API token"""
    return f"mjseo_{secrets.token_urlsafe(32)}"


@router.post("/", response_model=APITokenResponse, status_code=status.HTTP_201_CREATED)
async def create_api_token(
    token_data: APITokenCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new API token for MCP server or external integrations"""
    # Generate unique token
    token_string = generate_api_token()
    
    # Create token record
    api_token = APIToken(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        token=token_string,
        name=token_data.name,
        is_active=True,
        created_at=datetime.now(timezone.utc)
    )
    
    db.add(api_token)
    await db.commit()
    await db.refresh(api_token)
    
    logger.info(f"API token created for user {current_user.email}: {token_data.name}")
    
    return api_token


@router.get("/", response_model=List[APITokenResponse])
async def get_api_tokens(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all API tokens for current user"""
    result = await db.execute(
        select(APIToken)
        .where(APIToken.user_id == current_user.id)
        .order_by(APIToken.created_at.desc())
    )
    tokens = result.scalars().all()
    return tokens


@router.delete("/{token_id}")
async def delete_api_token(
    token_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete an API token"""
    result = await db.execute(
        select(APIToken)
        .where(APIToken.id == token_id, APIToken.user_id == current_user.id)
    )
    token = result.scalar_one_or_none()
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API token not found"
        )
    
    await db.delete(token)
    await db.commit()
    
    logger.info(f"API token deleted: {token.name}")
    
    return {"message": "API token deleted successfully"}


@router.patch("/{token_id}/toggle")
async def toggle_api_token(
    token_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Toggle API token active status"""
    result = await db.execute(
        select(APIToken)
        .where(APIToken.id == token_id, APIToken.user_id == current_user.id)
    )
    token = result.scalar_one_or_none()
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API token not found"
        )
    
    token.is_active = not token.is_active
    await db.commit()
    await db.refresh(token)
    
    logger.info(f"API token toggled: {token.name} - Active: {token.is_active}")
    
    return token
