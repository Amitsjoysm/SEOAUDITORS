"""Add more light theme variations"""
import asyncio
from sqlalchemy import select
from database import get_db
from models import Theme
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def add_light_themes():
    """Add light theme variations"""
    logger.info("Adding light theme variations...")
    
    light_themes = [
        {
            "name": "Ocean Light",
            "description": "Clean ocean-inspired light theme",
            "primary_color": "#0369a1",  # sky-700 (4.52:1 on white - AA compliant)
            "secondary_color": "#0284c7",  # sky-600
            "accent_color": "#7c3aed",  # violet-600
            "background_color": "#ffffff",
            "surface_color": "#f0f9ff",  # sky-50
            "text_primary": "#0c4a6e",  # sky-900
            "text_secondary": "#334155",  # slate-700
            "border_radius": "0.75rem",
            "font_family": "Inter, system-ui, sans-serif"
        },
        {
            "name": "Lavender Light",
            "description": "Soft lavender and purple light theme",
            "primary_color": "#7c3aed",  # violet-600 (4.54:1 on white)
            "secondary_color": "#a78bfa",  # violet-400
            "accent_color": "#06b6d4",  # cyan-500
            "background_color": "#fefefe",
            "surface_color": "#faf5ff",  # purple-50
            "text_primary": "#111827",  # gray-900
            "text_secondary": "#374151",  # gray-700
            "border_radius": "0.75rem",
            "font_family": "Inter, system-ui, sans-serif"
        },
        {
            "name": "Forest Light",
            "description": "Natural green and earth tones",
            "primary_color": "#047857",  # emerald-700 (5.08:1 on white)
            "secondary_color": "#10b981",  # emerald-500
            "accent_color": "#6366f1",  # indigo-500
            "background_color": "#ffffff",
            "surface_color": "#f0fdf4",  # green-50
            "text_primary": "#064e3b",  # emerald-900
            "text_secondary": "#374151",  # gray-700
            "border_radius": "0.75rem",
            "font_family": "Inter, system-ui, sans-serif"
        }
    ]
    
    async for db in get_db():
        try:
            for theme_data in light_themes:
                # Check if theme already exists
                result = await db.execute(
                    select(Theme).where(Theme.name == theme_data["name"])
                )
                existing = result.scalar_one_or_none()
                
                if existing:
                    logger.info(f"Theme '{theme_data['name']}' already exists, skipping...")
                    continue
                
                # Create new theme
                theme = Theme(
                    name=theme_data["name"],
                    is_active=False,
                    primary_color=theme_data["primary_color"],
                    secondary_color=theme_data["secondary_color"],
                    accent_color=theme_data["accent_color"],
                    background_color=theme_data["background_color"],
                    surface_color=theme_data["surface_color"],
                    text_primary=theme_data["text_primary"],
                    text_secondary=theme_data["text_secondary"],
                    border_radius=theme_data["border_radius"],
                    font_family=theme_data["font_family"]
                )
                
                db.add(theme)
                logger.info(f"✅ Created theme: {theme_data['name']}")
            
            await db.commit()
            logger.info("✅ All light themes added successfully!")
            
        except Exception as e:
            logger.error(f"Error adding themes: {e}")
            await db.rollback()
            raise
        finally:
            break


if __name__ == "__main__":
    asyncio.run(add_light_themes())
