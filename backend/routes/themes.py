"""Theme Management Routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import List, Optional
from pydantic import BaseModel
from database import get_db
from models import Theme, User, UserRole
from auth import get_current_user

router = APIRouter(prefix="/themes", tags=["themes"])


class ThemeCreate(BaseModel):
    name: str
    primary_color: str = "#a78bfa"
    secondary_color: str = "#fbbf24"
    accent_color: str = "#34d399"
    background_color: str = "#0f172a"
    surface_color: str = "#1e293b"
    text_primary: str = "#f8fafc"
    text_secondary: str = "#cbd5e1"
    border_radius: str = "0.75rem"
    font_family: str = "Inter, system-ui, sans-serif"
    custom_css: str = None


class ThemeUpdate(BaseModel):
    name: str = None
    primary_color: str = None
    secondary_color: str = None
    accent_color: str = None
    background_color: str = None
    surface_color: str = None
    text_primary: str = None
    text_secondary: str = None
    border_radius: str = None
    font_family: str = None
    custom_css: str = None


class ThemeResponse(BaseModel):
    id: str
    name: str
    is_active: bool
    primary_color: str
    secondary_color: str
    accent_color: str
    background_color: str
    surface_color: str
    text_primary: str
    text_secondary: str
    border_radius: str
    font_family: str
    custom_css: Optional[str] = None
    
    class Config:
        from_attributes = True


@router.get("/active", response_model=ThemeResponse)
async def get_active_theme(db: AsyncSession = Depends(get_db)):
    """Get the currently active theme (public endpoint)"""
    result = await db.execute(
        select(Theme).where(Theme.is_active == True)
    )
    theme = result.scalar_one_or_none()
    
    if not theme:
        # Return default theme if none is active
        return ThemeResponse(
            id="default",
            name="Default",
            is_active=True,
            primary_color="#a78bfa",
            secondary_color="#fbbf24",
            accent_color="#34d399",
            background_color="#0f172a",
            surface_color="#1e293b",
            text_primary="#f8fafc",
            text_secondary="#cbd5e1",
            border_radius="0.75rem",
            font_family="Inter, system-ui, sans-serif"
        )
    
    return theme


@router.get("/", response_model=List[ThemeResponse])
async def list_themes(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all themes (superadmin only)"""
    if current_user.role != UserRole.SUPERADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superadmin can access themes"
        )
    
    result = await db.execute(select(Theme).order_by(Theme.created_at.desc()))
    themes = result.scalars().all()
    return themes


@router.post("/", response_model=ThemeResponse, status_code=status.HTTP_201_CREATED)
async def create_theme(
    theme_data: ThemeCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new theme (superadmin only)"""
    if current_user.role != UserRole.SUPERADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superadmin can create themes"
        )
    
    # Check if theme name already exists
    result = await db.execute(
        select(Theme).where(Theme.name == theme_data.name)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Theme with this name already exists"
        )
    
    theme = Theme(**theme_data.model_dump())
    db.add(theme)
    await db.commit()
    await db.refresh(theme)
    
    return theme


@router.put("/{theme_id}", response_model=ThemeResponse)
async def update_theme(
    theme_id: str,
    theme_data: ThemeUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a theme (superadmin only)"""
    if current_user.role != UserRole.SUPERADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superadmin can update themes"
        )
    
    result = await db.execute(select(Theme).where(Theme.id == theme_id))
    theme = result.scalar_one_or_none()
    
    if not theme:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Theme not found"
        )
    
    # Update only provided fields
    update_data = theme_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(theme, key, value)
    
    await db.commit()
    await db.refresh(theme)
    
    return theme


@router.post("/{theme_id}/activate")
async def activate_theme(
    theme_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Activate a theme (superadmin only) - deactivates all others"""
    if current_user.role != UserRole.SUPERADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superadmin can activate themes"
        )
    
    # Check if theme exists
    result = await db.execute(select(Theme).where(Theme.id == theme_id))
    theme = result.scalar_one_or_none()
    
    if not theme:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Theme not found"
        )
    
    # Deactivate all themes
    await db.execute(update(Theme).values(is_active=False))
    
    # Activate the selected theme
    theme.is_active = True
    await db.commit()
    await db.refresh(theme)
    
    return {"message": "Theme activated successfully", "theme": theme.name}


@router.delete("/{theme_id}")
async def delete_theme(
    theme_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a theme (superadmin only)"""
    if current_user.role != UserRole.SUPERADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superadmin can delete themes"
        )
    
    result = await db.execute(select(Theme).where(Theme.id == theme_id))
    theme = result.scalar_one_or_none()
    
    if not theme:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Theme not found"
        )
    
    if theme.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete the active theme. Activate another theme first."
        )
    
    await db.delete(theme)
    await db.commit()
    
    return {"message": "Theme deleted successfully"}
