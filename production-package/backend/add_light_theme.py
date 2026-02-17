"""Script to add light theme to existing database"""
import asyncio
from sqlalchemy import select
from database import get_db
from models import Theme
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def add_light_theme():
    """Add light theme to database"""
    logger.info("Adding Light Serenity theme...")
    
    async for db in get_db():
        try:
            # Check if light theme already exists
            result = await db.execute(
                select(Theme).where(Theme.name == "Light Serenity")
            )
            existing_theme = result.scalar_one_or_none()
            
            if existing_theme:
                logger.info("Light Serenity theme already exists, skipping...")
                return
            
            # Create new light theme
            light_theme = Theme(
                name="Light Serenity",
                is_active=False,
                primary_color="#0891b2",
                secondary_color="#06b6d4",
                accent_color="#a78bfa",
                background_color="#ffffff",
                surface_color="#f8f9fa",
                text_primary="#111827",
                text_secondary="#374151",
                border_radius="0.75rem",
                font_family="Inter, system-ui, sans-serif"
            )
            
            db.add(light_theme)
            await db.commit()
            logger.info("✅ Light Serenity theme created successfully!")
            
        except Exception as e:
            logger.error(f"Error adding light theme: {e}")
            await db.rollback()
            raise
        finally:
            break


if __name__ == "__main__":
    asyncio.run(add_light_theme())
