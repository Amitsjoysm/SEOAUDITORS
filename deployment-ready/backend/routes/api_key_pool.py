"""
API Key Pool Management Routes
Admin-only routes for managing multiple API keys per service with rotation
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from pydantic import BaseModel
from datetime import datetime

from database import get_db
from auth import get_current_user, require_superadmin
from models import User, APIKeyPool, APIServiceType
from utils.encryption import EncryptionService

router = APIRouter(prefix="/admin/api-keys", tags=["Admin - API Keys"])
encryption_service = EncryptionService()


# Schemas
class APIKeyCreate(BaseModel):
    service_name: APIServiceType
    api_key: str
    api_username: str | None = None
    quota_limit: int | None = None
    priority: int = 1
    notes: str | None = None


class APIKeyUpdate(BaseModel):
    api_key: str | None = None
    api_username: str | None = None
    is_active: bool | None = None
    quota_limit: int | None = None
    priority: int | None = None
    notes: str | None = None


class APIKeyResponse(BaseModel):
    id: str
    service_name: str
    api_username: str | None
    is_active: bool
    quota_limit: int | None
    quota_used: int
    priority: int
    last_used_at: datetime | None
    health_status: str
    consecutive_failures: int
    notes: str | None
    created_at: datetime
    
    class Config:
        from_attributes = True


class APIKeyWithValue(APIKeyResponse):
    api_key: str  # Decrypted key value


# Routes
@router.get("/", response_model=List[APIKeyResponse])
async def list_api_keys(
    service_name: APIServiceType | None = None,
    current_user: User = Depends(require_superadmin),
    db: AsyncSession = Depends(get_db)
):
    """List all API keys (values hidden)"""
    query = select(APIKeyPool)
    
    if service_name:
        query = query.where(APIKeyPool.service_name == service_name)
    
    query = query.order_by(APIKeyPool.service_name, APIKeyPool.priority)
    
    result = await db.execute(query)
    keys = result.scalars().all()
    
    return [APIKeyResponse.from_orm(key) for key in keys]


@router.get("/{key_id}", response_model=APIKeyWithValue)
async def get_api_key(
    key_id: str,
    current_user: User = Depends(require_superadmin),
    db: AsyncSession = Depends(get_db)
):
    """Get specific API key with decrypted value"""
    result = await db.execute(
        select(APIKeyPool).where(APIKeyPool.id == key_id)
    )
    key_entry = result.scalar_one_or_none()
    
    if not key_entry:
        raise HTTPException(status_code=404, detail="API key not found")
    
    # Decrypt key value
    decrypted_key = encryption_service.decrypt(key_entry.api_key)
    
    return APIKeyWithValue(
        **{**key_entry.__dict__, "api_key": decrypted_key}
    )


@router.post("/", response_model=APIKeyResponse)
async def create_api_key(
    key_data: APIKeyCreate,
    current_user: User = Depends(require_superadmin),
    db: AsyncSession = Depends(get_db)
):
    """Add new API key to pool"""
    # Encrypt the API key
    encrypted_key = encryption_service.encrypt(key_data.api_key)
    
    new_key = APIKeyPool(
        service_name=key_data.service_name,
        api_key=encrypted_key,
        api_username=key_data.api_username,
        quota_limit=key_data.quota_limit,
        priority=key_data.priority,
        notes=key_data.notes,
        added_by=current_user.id,
        is_active=True,
        health_status="healthy",
        quota_used=0,
        consecutive_failures=0
    )
    
    db.add(new_key)
    await db.commit()
    await db.refresh(new_key)
    
    return APIKeyResponse.from_orm(new_key)


@router.put("/{key_id}", response_model=APIKeyResponse)
async def update_api_key(
    key_id: str,
    key_data: APIKeyUpdate,
    current_user: User = Depends(require_superadmin),
    db: AsyncSession = Depends(get_db)
):
    """Update API key"""
    result = await db.execute(
        select(APIKeyPool).where(APIKeyPool.id == key_id)
    )
    key_entry = result.scalar_one_or_none()
    
    if not key_entry:
        raise HTTPException(status_code=404, detail="API key not found")
    
    # Update fields
    if key_data.api_key:
        key_entry.api_key = encryption_service.encrypt(key_data.api_key)
    if key_data.api_username is not None:
        key_entry.api_username = key_data.api_username
    if key_data.is_active is not None:
        key_entry.is_active = key_data.is_active
    if key_data.quota_limit is not None:
        key_entry.quota_limit = key_data.quota_limit
    if key_data.priority is not None:
        key_entry.priority = key_data.priority
    if key_data.notes is not None:
        key_entry.notes = key_data.notes
    
    await db.commit()
    await db.refresh(key_entry)
    
    return APIKeyResponse.from_orm(key_entry)


@router.delete("/{key_id}")
async def delete_api_key(
    key_id: str,
    current_user: User = Depends(require_superadmin),
    db: AsyncSession = Depends(get_db)
):
    """Delete API key"""
    result = await db.execute(
        select(APIKeyPool).where(APIKeyPool.id == key_id)
    )
    key_entry = result.scalar_one_or_none()
    
    if not key_entry:
        raise HTTPException(status_code=404, detail="API key not found")
    
    await db.delete(key_entry)
    await db.commit()
    
    return {"message": "API key deleted successfully"}


@router.post("/{key_id}/toggle")
async def toggle_api_key(
    key_id: str,
    current_user: User = Depends(require_superadmin),
    db: AsyncSession = Depends(get_db)
):
    """Toggle API key active status"""
    result = await db.execute(
        select(APIKeyPool).where(APIKeyPool.id == key_id)
    )
    key_entry = result.scalar_one_or_none()
    
    if not key_entry:
        raise HTTPException(status_code=404, detail="API key not found")
    
    key_entry.is_active = not key_entry.is_active
    await db.commit()
    
    return {
        "message": f"API key {'activated' if key_entry.is_active else 'deactivated'}",
        "is_active": key_entry.is_active
    }


@router.post("/{key_id}/reset-quota")
async def reset_quota(
    key_id: str,
    current_user: User = Depends(require_superadmin),
    db: AsyncSession = Depends(get_db)
):
    """Reset quota usage for API key"""
    result = await db.execute(
        select(APIKeyPool).where(APIKeyPool.id == key_id)
    )
    key_entry = result.scalar_one_or_none()
    
    if not key_entry:
        raise HTTPException(status_code=404, detail="API key not found")
    
    key_entry.quota_used = 0
    key_entry.quota_reset_at = datetime.utcnow()
    await db.commit()
    
    return {"message": "Quota reset successfully"}


@router.post("/initialize-from-env")
async def initialize_from_env(
    current_user: User = Depends(require_superadmin),
    db: AsyncSession = Depends(get_db)
):
    """Initialize API keys from environment variables"""
    import os
    
    keys_added = []
    
    # DataForSEO
    dataforseo_user = os.getenv("DATAFORSEO_USERNAME")
    dataforseo_pass = os.getenv("DATAFORSEO_PASSWORD")
    if dataforseo_user and dataforseo_pass:
        encrypted_pass = encryption_service.encrypt(dataforseo_pass)
        key = APIKeyPool(
            service_name=APIServiceType.DATAFORSEO,
            api_key=encrypted_pass,
            api_username=dataforseo_user,
            priority=1,
            notes="Initialized from environment",
            added_by=current_user.id,
            is_active=True,
            health_status="healthy"
        )
        db.add(key)
        keys_added.append("DATAFORSEO")
    
    # Groq
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key:
        encrypted_key = encryption_service.encrypt(groq_key)
        key = APIKeyPool(
            service_name=APIServiceType.GROQ,
            api_key=encrypted_key,
            priority=1,
            notes="Initialized from environment",
            added_by=current_user.id,
            is_active=True,
            health_status="healthy"
        )
        db.add(key)
        keys_added.append("GROQ")
    
    # Exa
    exa_key = os.getenv("EXA_API_KEY")
    if exa_key:
        encrypted_key = encryption_service.encrypt(exa_key)
        key = APIKeyPool(
            service_name=APIServiceType.EXA_AI,
            api_key=encrypted_key,
            priority=1,
            notes="Initialized from environment",
            added_by=current_user.id,
            is_active=True,
            health_status="healthy"
        )
        db.add(key)
        keys_added.append("EXA_AI")
    
    await db.commit()
    
    return {
        "message": f"Initialized {len(keys_added)} API keys from environment",
        "keys_added": keys_added
    }
