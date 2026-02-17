"""LLM Settings Management Routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import List, Optional
from pydantic import BaseModel
from database import get_db
from models import LLMSetting, LLMProvider, User, UserRole
from auth import get_current_user

router = APIRouter(prefix="/admin/llm-settings", tags=["llm-settings"])


class LLMSettingCreate(BaseModel):
    provider: LLMProvider
    model_name: str
    api_key_ref: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 4096
    top_p: float = 1.0
    description: Optional[str] = None


class LLMSettingUpdate(BaseModel):
    model_name: Optional[str] = None
    api_key_ref: Optional[str] = None
    base_url: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    top_p: Optional[float] = None
    description: Optional[str] = None


class LLMSettingResponse(BaseModel):
    id: str
    provider: str
    model_name: str
    api_key_ref: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float
    max_tokens: int
    top_p: float
    is_active: bool
    description: Optional[str] = None
    
    class Config:
        from_attributes = True


@router.get("/active", response_model=Optional[LLMSettingResponse])
async def get_active_llm(db: AsyncSession = Depends(get_db)):
    """Get the currently active LLM configuration (public for backend use)"""
    result = await db.execute(
        select(LLMSetting).where(LLMSetting.is_active == True)
    )
    llm_setting = result.scalar_one_or_none()
    return llm_setting


@router.get("/", response_model=List[LLMSettingResponse])
async def list_llm_settings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all LLM settings (superadmin only)"""
    if current_user.role != UserRole.SUPERADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superadmin can access LLM settings"
        )
    
    result = await db.execute(select(LLMSetting).order_by(LLMSetting.created_at.desc()))
    settings = result.scalars().all()
    return settings


@router.post("/", response_model=LLMSettingResponse, status_code=status.HTTP_201_CREATED)
async def create_llm_setting(
    setting_data: LLMSettingCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new LLM setting (superadmin only)"""
    if current_user.role != UserRole.SUPERADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superadmin can create LLM settings"
        )
    
    setting = LLMSetting(**setting_data.model_dump())
    db.add(setting)
    await db.commit()
    await db.refresh(setting)
    
    return setting


@router.put("/{setting_id}", response_model=LLMSettingResponse)
async def update_llm_setting(
    setting_id: str,
    setting_data: LLMSettingUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update an LLM setting (superadmin only)"""
    if current_user.role != UserRole.SUPERADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superadmin can update LLM settings"
        )
    
    result = await db.execute(select(LLMSetting).where(LLMSetting.id == setting_id))
    setting = result.scalar_one_or_none()
    
    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="LLM setting not found"
        )
    
    # Update only provided fields
    update_data = setting_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(setting, key, value)
    
    await db.commit()
    await db.refresh(setting)
    
    return setting


@router.post("/{setting_id}/activate")
async def activate_llm_setting(
    setting_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Activate an LLM setting (superadmin only) - deactivates all others"""
    if current_user.role != UserRole.SUPERADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superadmin can activate LLM settings"
        )
    
    # Check if setting exists
    result = await db.execute(select(LLMSetting).where(LLMSetting.id == setting_id))
    setting = result.scalar_one_or_none()
    
    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="LLM setting not found"
        )
    
    # Deactivate all settings
    await db.execute(update(LLMSetting).values(is_active=False))
    
    # Activate the selected setting
    setting.is_active = True
    await db.commit()
    await db.refresh(setting)
    
    return {
        "message": "LLM setting activated successfully",
        "provider": setting.provider,
        "model": setting.model_name
    }


@router.delete("/{setting_id}")
async def delete_llm_setting(
    setting_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete an LLM setting (superadmin only)"""
    if current_user.role != UserRole.SUPERADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superadmin can delete LLM settings"
        )
    
    result = await db.execute(select(LLMSetting).where(LLMSetting.id == setting_id))
    setting = result.scalar_one_or_none()
    
    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="LLM setting not found"
        )
    
    if setting.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete the active LLM setting. Activate another setting first."
        )
    
    await db.delete(setting)
    await db.commit()
    
    return {"message": "LLM setting deleted successfully"}


@router.get("/models/{provider}")
async def get_provider_models(
    provider: str,
    current_user: User = Depends(get_current_user)
):
    """Get available models for a provider (superadmin only)"""
    if current_user.role != UserRole.SUPERADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superadmin can access this endpoint"
        )
    
    # Model lists for each provider
    models = {
        "groq": [
            {"id": "llama-3.3-70b-versatile", "name": "Llama 3.3 70B Versatile", "context": "128K"},
            {"id": "llama-3.1-70b-versatile", "name": "Llama 3.1 70B Versatile", "context": "128K"},
            {"id": "llama-3.1-8b-instant", "name": "Llama 3.1 8B Instant", "context": "128K"},
            {"id": "mixtral-8x7b-32768", "name": "Mixtral 8x7B", "context": "32K"},
            {"id": "gemma2-9b-it", "name": "Gemma 2 9B", "context": "8K"},
        ],
        "openai": [
            {"id": "gpt-4o", "name": "GPT-4o", "context": "128K"},
            {"id": "gpt-4o-mini", "name": "GPT-4o Mini", "context": "128K"},
            {"id": "gpt-4-turbo", "name": "GPT-4 Turbo", "context": "128K"},
            {"id": "gpt-4", "name": "GPT-4", "context": "8K"},
            {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "context": "16K"},
        ],
        "anthropic": [
            {"id": "claude-3-5-sonnet-20241022", "name": "Claude 3.5 Sonnet", "context": "200K"},
            {"id": "claude-3-5-haiku-20241022", "name": "Claude 3.5 Haiku", "context": "200K"},
            {"id": "claude-3-opus-20240229", "name": "Claude 3 Opus", "context": "200K"},
            {"id": "claude-3-sonnet-20240229", "name": "Claude 3 Sonnet", "context": "200K"},
        ],
        "gemini": [
            {"id": "gemini-2.0-flash-exp", "name": "Gemini 2.0 Flash (Experimental)", "context": "1M"},
            {"id": "gemini-1.5-pro", "name": "Gemini 1.5 Pro", "context": "2M"},
            {"id": "gemini-1.5-flash", "name": "Gemini 1.5 Flash", "context": "1M"},
            {"id": "gemini-1.0-pro", "name": "Gemini 1.0 Pro", "context": "32K"},
        ],
        "ollama": [
            {"id": "llama3.2", "name": "Llama 3.2", "context": "128K"},
            {"id": "llama3.1", "name": "Llama 3.1", "context": "128K"},
            {"id": "mistral", "name": "Mistral", "context": "32K"},
            {"id": "mixtral", "name": "Mixtral", "context": "32K"},
            {"id": "phi3", "name": "Phi-3", "context": "128K"},
            {"id": "gemma2", "name": "Gemma 2", "context": "8K"},
        ]
    }
    
    return {"provider": provider, "models": models.get(provider.lower(), [])}
