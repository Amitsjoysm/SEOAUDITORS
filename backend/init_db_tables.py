"""Database initialization script with default data"""
import asyncio
from sqlalchemy import select
from database import engine, Base, get_db
from models import Plan, Theme, User, UserRole, LLMSetting, LLMProvider
from passlib.context import CryptContext
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def init_database():
    """Initialize database tables and seed default data"""
    logger.info("Starting database initialization...")
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✅ Database tables created")
    
    # Seed default data
    async for db in get_db():
        try:
            # Check if plans already exist
            result = await db.execute(select(Plan))
            existing_plans = result.scalars().all()
            
            if not existing_plans:
                logger.info("Seeding default plans...")
                plans = [
                    Plan(
                        name="free",
                        display_name="Free",
                        description="Perfect for trying out our SEO audit tool",
                        price=0.0,
                        max_audits_per_month=2,
                        max_pages_per_audit=5,
                        features=["2 audits per month", "5 pages per audit", "Basic SEO checks", "Email support"],
                        is_active=True
                    ),
                    Plan(
                        name="basic",
                        display_name="Basic",
                        description="Great for small websites and blogs",
                        price=29.99,
                        max_audits_per_month=10,
                        max_pages_per_audit=20,
                        stripe_price_id="price_basic_placeholder",
                        features=["10 audits per month", "20 pages per audit", "All SEO checks", "Priority support", "PDF reports"],
                        is_active=True
                    ),
                    Plan(
                        name="pro",
                        display_name="Pro",
                        description="Perfect for growing businesses",
                        price=79.99,
                        max_audits_per_month=50,
                        max_pages_per_audit=100,
                        stripe_price_id="price_pro_placeholder",
                        features=["50 audits per month", "100 pages per audit", "All SEO checks", "Priority support", "PDF + DOCX reports", "AI insights", "API access"],
                        is_active=True
                    ),
                    Plan(
                        name="enterprise",
                        display_name="Enterprise",
                        description="For agencies and large websites",
                        price=199.99,
                        max_audits_per_month=999999,  # Unlimited
                        max_pages_per_audit=500,
                        stripe_price_id="price_enterprise_placeholder",
                        features=["Unlimited audits", "500 pages per audit", "All SEO checks", "24/7 support", "Custom reports", "White label", "API access", "Dedicated account manager"],
                        is_active=True
                    )
                ]
                
                for plan in plans:
                    db.add(plan)
                
                await db.commit()
                logger.info("✅ Default plans created")
            else:
                logger.info("Plans already exist, skipping...")
            
            # Check if themes already exist
            result = await db.execute(select(Theme))
            existing_themes = result.scalars().all()
            
            if not existing_themes:
                logger.info("Seeding default themes...")
                themes = [
                    Theme(
                        name="Lavender Dream",
                        is_active=True,
                        primary_color="#d8b4fe",
                        secondary_color="#fbbf24",
                        accent_color="#a78bfa",
                        background_color="#0f172a",
                        surface_color="#1e293b",
                        text_primary="#f8fafc",
                        text_secondary="#cbd5e1",
                        border_radius="0.75rem",
                        font_family="Inter, system-ui, sans-serif"
                    ),
                    Theme(
                        name="Ocean Breeze",
                        is_active=False,
                        primary_color="#7dd3fc",
                        secondary_color="#34d399",
                        accent_color="#38bdf8",
                        background_color="#0f172a",
                        surface_color="#1e293b",
                        text_primary="#f8fafc",
                        text_secondary="#cbd5e1",
                        border_radius="0.75rem",
                        font_family="Inter, system-ui, sans-serif"
                    ),
                    Theme(
                        name="Sunset Glow",
                        is_active=False,
                        primary_color="#fb923c",
                        secondary_color="#fbbf24",
                        accent_color="#f472b6",
                        background_color="#0f172a",
                        surface_color="#1e293b",
                        text_primary="#f8fafc",
                        text_secondary="#cbd5e1",
                        border_radius="0.75rem",
                        font_family="Inter, system-ui, sans-serif"
                    ),
                    Theme(
                        name="Mint Fresh",
                        is_active=False,
                        primary_color="#6ee7b7",
                        secondary_color="#a3e635",
                        accent_color="#34d399",
                        background_color="#0f172a",
                        surface_color="#1e293b",
                        text_primary="#f8fafc",
                        text_secondary="#cbd5e1",
                        border_radius="0.75rem",
                        font_family="Inter, system-ui, sans-serif"
                    ),
                    Theme(
                        name="Rose Garden",
                        is_active=False,
                        primary_color="#fda4af",
                        secondary_color="#f9a8d4",
                        accent_color="#fb7185",
                        background_color="#0f172a",
                        surface_color="#1e293b",
                        text_primary="#f8fafc",
                        text_secondary="#cbd5e1",
                        border_radius="0.75rem",
                        font_family="Inter, system-ui, sans-serif"
                    )
                ]
                
                for theme in themes:
                    db.add(theme)
                
                await db.commit()
                logger.info("✅ Default themes created")
            else:
                logger.info("Themes already exist, skipping...")
            
            # Check if superadmin exists
            result = await db.execute(select(User).where(User.email == "superadmin@test.com"))
            superadmin = result.scalar_one_or_none()
            
            if not superadmin:
                logger.info("Creating superadmin account...")
                superadmin = User(
                    email="superadmin@test.com",
                    password_hash=pwd_context.hash("test123"),
                    full_name="Super Admin",
                    role=UserRole.SUPERADMIN,
                    is_active=True
                )
                db.add(superadmin)
                await db.commit()
                logger.info("✅ Superadmin account created (superadmin@test.com / test123)")
            else:
                logger.info("Superadmin already exists, skipping...")
            
            # Check if default LLM setting exists
            result = await db.execute(select(LLMSetting))
            existing_llm = result.scalars().all()
            
            if not existing_llm:
                logger.info("Creating default LLM setting...")
                default_llm = LLMSetting(
                    provider=LLMProvider.GROQ,
                    model_name="llama-3.3-70b-versatile",
                    api_key_ref="GROQ_API_KEY",
                    temperature=0.7,
                    max_tokens=4096,
                    top_p=1.0,
                    is_active=True,
                    description="Default Groq Llama 3.3 70B model for SEO analysis"
                )
                db.add(default_llm)
                await db.commit()
                logger.info("✅ Default LLM setting created")
            else:
                logger.info("LLM settings already exist, skipping...")
            
            logger.info("\n" + "="*50)
            logger.info("✅ Database initialization completed successfully!")
            logger.info("="*50)
            logger.info("\nDefault credentials:")
            logger.info("  Superadmin: superadmin@test.com / test123")
            logger.info("  Test User: test@example.com / test123")
            logger.info("\nDefault LLM: Groq Llama 3.3 70B")
            logger.info("="*50 + "\n")
            
        except Exception as e:
            logger.error(f"Error during database initialization: {str(e)}")
            await db.rollback()
            raise
        finally:
            await db.close()
            break


if __name__ == "__main__":
    asyncio.run(init_database())
