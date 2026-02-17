"""SEO Settings Management Routes (Superadmin only)"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import Optional
from pydantic import BaseModel
import logging

from database import get_db
from models import SEOSettings, User, UserRole
from auth import get_current_user

router = APIRouter(prefix="/admin/seo-settings", tags=["Admin - SEO Settings"])
logger = logging.getLogger(__name__)


class SEOSettingsCreate(BaseModel):
    # Meta Tags
    site_title: Optional[str] = None
    site_description: Optional[str] = None
    site_keywords: Optional[str] = None
    author: Optional[str] = None
    
    # Open Graph
    og_title: Optional[str] = None
    og_description: Optional[str] = None
    og_image: Optional[str] = None
    og_url: Optional[str] = None
    og_type: Optional[str] = "website"
    og_site_name: Optional[str] = None
    
    # Twitter Card
    twitter_card: Optional[str] = "summary_large_image"
    twitter_site: Optional[str] = None
    twitter_creator: Optional[str] = None
    twitter_title: Optional[str] = None
    twitter_description: Optional[str] = None
    twitter_image: Optional[str] = None
    
    # Schema.org
    organization_name: Optional[str] = None
    organization_logo: Optional[str] = None
    organization_description: Optional[str] = None
    organization_url: Optional[str] = None
    organization_email: Optional[str] = None
    organization_phone: Optional[str] = None
    organization_social_profiles: Optional[list] = None
    
    # Analytics
    google_analytics_id: Optional[str] = None
    google_tag_manager_id: Optional[str] = None
    google_site_verification: Optional[str] = None
    facebook_domain_verification: Optional[str] = None
    
    # Additional Settings
    robots_txt_content: Optional[str] = None
    sitemap_enabled: Optional[bool] = True
    canonical_url: Optional[str] = None
    language_code: Optional[str] = "en"
    
    # Performance
    enable_lazy_loading: Optional[bool] = True
    enable_image_optimization: Optional[bool] = True
    enable_minification: Optional[bool] = True
    enable_compression: Optional[bool] = True


class SEOSettingsUpdate(BaseModel):
    # All fields optional for updates
    site_title: Optional[str] = None
    site_description: Optional[str] = None
    site_keywords: Optional[str] = None
    author: Optional[str] = None
    og_title: Optional[str] = None
    og_description: Optional[str] = None
    og_image: Optional[str] = None
    og_url: Optional[str] = None
    og_type: Optional[str] = None
    og_site_name: Optional[str] = None
    twitter_card: Optional[str] = None
    twitter_site: Optional[str] = None
    twitter_creator: Optional[str] = None
    twitter_title: Optional[str] = None
    twitter_description: Optional[str] = None
    twitter_image: Optional[str] = None
    organization_name: Optional[str] = None
    organization_logo: Optional[str] = None
    organization_description: Optional[str] = None
    organization_url: Optional[str] = None
    organization_email: Optional[str] = None
    organization_phone: Optional[str] = None
    organization_social_profiles: Optional[list] = None
    google_analytics_id: Optional[str] = None
    google_tag_manager_id: Optional[str] = None
    google_site_verification: Optional[str] = None
    facebook_domain_verification: Optional[str] = None
    robots_txt_content: Optional[str] = None
    sitemap_enabled: Optional[bool] = None
    canonical_url: Optional[str] = None
    language_code: Optional[str] = None
    enable_lazy_loading: Optional[bool] = None
    enable_image_optimization: Optional[bool] = None
    enable_minification: Optional[bool] = None
    enable_compression: Optional[bool] = None


class SEOSettingsResponse(BaseModel):
    id: str
    site_title: Optional[str] = None
    site_description: Optional[str] = None
    site_keywords: Optional[str] = None
    author: Optional[str] = None
    og_title: Optional[str] = None
    og_description: Optional[str] = None
    og_image: Optional[str] = None
    og_url: Optional[str] = None
    og_type: Optional[str] = None
    og_site_name: Optional[str] = None
    twitter_card: Optional[str] = None
    twitter_site: Optional[str] = None
    twitter_creator: Optional[str] = None
    twitter_title: Optional[str] = None
    twitter_description: Optional[str] = None
    twitter_image: Optional[str] = None
    organization_name: Optional[str] = None
    organization_logo: Optional[str] = None
    organization_description: Optional[str] = None
    organization_url: Optional[str] = None
    organization_email: Optional[str] = None
    organization_phone: Optional[str] = None
    organization_social_profiles: Optional[list] = None
    google_analytics_id: Optional[str] = None
    google_tag_manager_id: Optional[str] = None
    google_site_verification: Optional[str] = None
    facebook_domain_verification: Optional[str] = None
    robots_txt_content: Optional[str] = None
    sitemap_enabled: Optional[bool] = None
    canonical_url: Optional[str] = None
    language_code: Optional[str] = None
    enable_lazy_loading: Optional[bool] = None
    enable_image_optimization: Optional[bool] = None
    enable_minification: Optional[bool] = None
    enable_compression: Optional[bool] = None
    is_active: bool
    
    class Config:
        from_attributes = True


@router.get("/active", response_model=Optional[SEOSettingsResponse])
async def get_active_seo_settings(db: AsyncSession = Depends(get_db)):
    """Get the active SEO settings (public endpoint for frontend use)"""
    result = await db.execute(
        select(SEOSettings).where(SEOSettings.is_active == True)
    )
    settings = result.scalar_one_or_none()
    return settings


@router.get("/", response_model=SEOSettingsResponse)
async def get_seo_settings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current SEO settings (superadmin only)"""
    if current_user.role != UserRole.SUPERADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superadmin can access SEO settings"
        )
    
    result = await db.execute(
        select(SEOSettings).where(SEOSettings.is_active == True)
    )
    settings = result.scalar_one_or_none()
    
    if not settings:
        # Create default settings if none exist
        settings = SEOSettings(
            site_title="MJ SEO - AI-Powered SEO Audit Platform",
            site_description="Production-ready SEO audit platform with 132+ comprehensive checks, AI-powered insights, and detailed reports",
            author="MJ SEO",
            og_type="website",
            og_site_name="MJ SEO",
            twitter_card="summary_large_image",
            organization_name="MJ SEO",
            sitemap_enabled=True,
            language_code="en",
            enable_lazy_loading=True,
            enable_image_optimization=True,
            enable_minification=True,
            enable_compression=True,
            is_active=True,
            last_updated_by=current_user.id
        )
        db.add(settings)
        await db.commit()
        await db.refresh(settings)
    
    return settings


@router.post("/", response_model=SEOSettingsResponse, status_code=status.HTTP_201_CREATED)
async def create_seo_settings(
    settings_data: SEOSettingsCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create new SEO settings (superadmin only)"""
    if current_user.role != UserRole.SUPERADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superadmin can create SEO settings"
        )
    
    # Deactivate all existing settings
    await db.execute(update(SEOSettings).values(is_active=False))
    
    # Create new settings
    settings = SEOSettings(
        **settings_data.model_dump(exclude_unset=True),
        is_active=True,
        last_updated_by=current_user.id
    )
    db.add(settings)
    await db.commit()
    await db.refresh(settings)
    
    logger.info(f"SEO settings created by {current_user.email}")
    return settings


@router.put("/{settings_id}", response_model=SEOSettingsResponse)
async def update_seo_settings(
    settings_id: str,
    settings_data: SEOSettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update SEO settings (superadmin only)"""
    if current_user.role != UserRole.SUPERADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superadmin can update SEO settings"
        )
    
    result = await db.execute(select(SEOSettings).where(SEOSettings.id == settings_id))
    settings = result.scalar_one_or_none()
    
    if not settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SEO settings not found"
        )
    
    # Update fields
    update_data = settings_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(settings, field, value)
    
    settings.last_updated_by = current_user.id
    await db.commit()
    await db.refresh(settings)
    
    logger.info(f"SEO settings updated by {current_user.email}")
    return settings


@router.delete("/{settings_id}")
async def delete_seo_settings(
    settings_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete SEO settings (superadmin only)"""
    if current_user.role != UserRole.SUPERADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superadmin can delete SEO settings"
        )
    
    result = await db.execute(select(SEOSettings).where(SEOSettings.id == settings_id))
    settings = result.scalar_one_or_none()
    
    if not settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SEO settings not found"
        )
    
    if settings.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete active SEO settings"
        )
    
    await db.delete(settings)
    await db.commit()
    
    logger.info(f"SEO settings deleted by {current_user.email}")
    return {"message": "SEO settings deleted successfully"}
