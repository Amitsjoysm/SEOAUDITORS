"""Environment Keys Management Routes (Superadmin only)"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import logging
import os

from database import get_db
from models import User, EnvironmentKey
from schemas import (
    EnvironmentKeyCreate,
    EnvironmentKeyUpdate,
    EnvironmentKeyResponse,
    EnvironmentKeyWithValue
)
from auth import get_current_superadmin
from utils.encryption import encryption_service

router = APIRouter(prefix="/admin/env-keys", tags=["Admin - Environment Keys"])
logger = logging.getLogger(__name__)


@router.get("", response_model=List[EnvironmentKeyResponse])
async def list_environment_keys(
    include_inactive: bool = False,
    current_user: User = Depends(get_current_superadmin),
    db: AsyncSession = Depends(get_db)
):
    """List all environment keys (without values for security)"""
    query = select(EnvironmentKey)
    if not include_inactive:
        query = query.where(EnvironmentKey.is_active == True)
    
    result = await db.execute(query.order_by(EnvironmentKey.category, EnvironmentKey.key_name))
    keys = result.scalars().all()
    return keys


@router.get("/{key_id}", response_model=EnvironmentKeyWithValue)
async def get_environment_key(
    key_id: str,
    current_user: User = Depends(get_current_superadmin),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific environment key with decrypted value"""
    result = await db.execute(select(EnvironmentKey).where(EnvironmentKey.id == key_id))
    key = result.scalar_one_or_none()
    
    if not key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Environment key not found"
        )
    
    # Decrypt the value before returning
    decrypted_value = encryption_service.decrypt(key.key_value)
    
    return EnvironmentKeyWithValue(
        id=key.id,
        key_name=key.key_name,
        key_value=decrypted_value,
        description=key.description,
        category=key.category,
        is_active=key.is_active,
        last_updated_by=key.last_updated_by,
        created_at=key.created_at,
        updated_at=key.updated_at
    )


@router.post("", response_model=EnvironmentKeyResponse, status_code=status.HTTP_201_CREATED)
async def create_environment_key(
    key_data: EnvironmentKeyCreate,
    current_user: User = Depends(get_current_superadmin),
    db: AsyncSession = Depends(get_db)
):
    """Create a new environment key"""
    # Check if key already exists
    result = await db.execute(
        select(EnvironmentKey).where(EnvironmentKey.key_name == key_data.key_name)
    )
    existing_key = result.scalar_one_or_none()
    
    if existing_key:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Environment key '{key_data.key_name}' already exists"
        )
    
    # Encrypt the value
    encrypted_value = encryption_service.encrypt(key_data.key_value)
    
    # Create new key
    new_key = EnvironmentKey(
        key_name=key_data.key_name,
        key_value=encrypted_value,
        description=key_data.description,
        category=key_data.category,
        last_updated_by=current_user.id,
        is_active=True
    )
    
    db.add(new_key)
    await db.commit()
    await db.refresh(new_key)
    
    # Also update the actual environment variable for runtime use
    os.environ[key_data.key_name] = key_data.key_value
    
    logger.info(f"Environment key created: {key_data.key_name} by {current_user.email}")
    return new_key


@router.put("/{key_id}", response_model=EnvironmentKeyResponse)
async def update_environment_key(
    key_id: str,
    key_data: EnvironmentKeyUpdate,
    current_user: User = Depends(get_current_superadmin),
    db: AsyncSession = Depends(get_db)
):
    """Update an environment key"""
    result = await db.execute(select(EnvironmentKey).where(EnvironmentKey.id == key_id))
    key = result.scalar_one_or_none()
    
    if not key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Environment key not found"
        )
    
    # Update fields
    update_data = key_data.model_dump(exclude_unset=True)
    
    # Encrypt new value if provided
    if 'key_value' in update_data and update_data['key_value']:
        update_data['key_value'] = encryption_service.encrypt(update_data['key_value'])
        # Update runtime environment variable
        os.environ[key.key_name] = key_data.key_value
    
    for field, value in update_data.items():
        setattr(key, field, value)
    
    key.last_updated_by = current_user.id
    
    await db.commit()
    await db.refresh(key)
    
    logger.info(f"Environment key updated: {key.key_name} by {current_user.email}")
    return key


@router.delete("/{key_id}")
async def delete_environment_key(
    key_id: str,
    current_user: User = Depends(get_current_superadmin),
    db: AsyncSession = Depends(get_db)
):
    """Delete an environment key"""
    result = await db.execute(select(EnvironmentKey).where(EnvironmentKey.id == key_id))
    key = result.scalar_one_or_none()
    
    if not key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Environment key not found"
        )
    
    key_name = key.key_name
    await db.delete(key)
    await db.commit()
    
    # Remove from runtime environment
    if key_name in os.environ:
        del os.environ[key_name]
    
    logger.info(f"Environment key deleted: {key_name} by {current_user.email}")
    return {"message": f"Environment key '{key_name}' deleted successfully"}


@router.post("/{key_id}/toggle")
async def toggle_environment_key(
    key_id: str,
    current_user: User = Depends(get_current_superadmin),
    db: AsyncSession = Depends(get_db)
):
    """Toggle active status of an environment key"""
    result = await db.execute(select(EnvironmentKey).where(EnvironmentKey.id == key_id))
    key = result.scalar_one_or_none()
    
    if not key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Environment key not found"
        )
    
    key.is_active = not key.is_active
    key.last_updated_by = current_user.id
    await db.commit()
    
    logger.info(f"Environment key toggled: {key.key_name} -> {key.is_active} by {current_user.email}")
    return {"key_name": key.key_name, "is_active": key.is_active}


@router.post("/initialize-defaults")
async def initialize_default_keys(
    current_user: User = Depends(get_current_superadmin),
    db: AsyncSession = Depends(get_db)
):
    """Initialize environment keys from current .env file"""
    # Define keys to import from environment
    default_keys = {
        "STRIPE_SECRET_KEY": {
            "category": "payment",
            "description": "Stripe API secret key for payment processing"
        },
        "STRIPE_PUBLISHABLE_KEY": {
            "category": "payment",
            "description": "Stripe publishable key (client-side)"
        },
        "STRIPE_WEBHOOK_SECRET": {
            "category": "payment",
            "description": "Stripe webhook signing secret"
        },
        "RAZORPAY_KEY_ID": {
            "category": "payment",
            "description": "Razorpay key ID for payment processing"
        },
        "RAZORPAY_KEY_SECRET": {
            "category": "payment",
            "description": "Razorpay secret key"
        },
        "GROQ_API_KEY": {
            "category": "ai",
            "description": "Groq API key for LLM (Llama 3.3 70B)"
        },
        "EXA_API_KEY": {
            "category": "ai",
            "description": "Exa.ai API key for research tasks"
        },
        "SECRET_KEY": {
            "category": "other",
            "description": "Application secret key for JWT and encryption"
        }
    }
    
    created_keys = []
    
    for key_name, metadata in default_keys.items():
        # Check if already exists
        result = await db.execute(
            select(EnvironmentKey).where(EnvironmentKey.key_name == key_name)
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            continue
        
        # Get value from environment
        env_value = os.getenv(key_name, "")
        if not env_value or env_value.startswith("placeholder") or "REPLACE" in env_value:
            continue  # Skip placeholder values
        
        # Encrypt and store
        encrypted_value = encryption_service.encrypt(env_value)
        
        new_key = EnvironmentKey(
            key_name=key_name,
            key_value=encrypted_value,
            description=metadata["description"],
            category=metadata["category"],
            last_updated_by=current_user.id,
            is_active=True
        )
        
        db.add(new_key)
        created_keys.append(key_name)
    
    await db.commit()
    
    logger.info(f"Initialized {len(created_keys)} default environment keys by {current_user.email}")
    return {
        "message": f"Initialized {len(created_keys)} environment keys",
        "keys": created_keys
    }
