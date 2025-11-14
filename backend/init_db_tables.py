"""Initialize database tables and seed data"""
import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import select
from database import engine, Base, AsyncSessionLocal
from models import User, Plan, Subscription, UserRole, SubscriptionStatus, Theme
from auth import get_password_hash
import uuid
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init_database():
    """Initialize database with tables and seed data"""
    logger.info("Creating database tables...")
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("Tables created successfully")
    
    # Seed data
    async with AsyncSessionLocal() as db:
        # Create plans
        plans_data = [
            {
                "name": "free",
                "display_name": "Free",
                "description": "Perfect for trying out MJ SEO",
                "price": 0.0,
                "max_audits_per_month": 2,
                "max_pages_per_audit": 10,
                "features": [
                    "2 audits per month",
                    "10 pages per audit",
                    "Basic SEO checks",
                    "PDF reports"
                ]
            },
            {
                "name": "basic",
                "display_name": "Basic",
                "description": "For small businesses and startups",
                "price": 29.0,
                "stripe_price_id": os.getenv("STRIPE_PRICE_BASIC", "price_REPLACE_WITH_YOUR_BASIC_PRICE_ID"),
                "max_audits_per_month": 10,
                "max_pages_per_audit": 15,
                "features": [
                    "10 audits per month",
                    "15 pages per audit",
                    "All 132 SEO checks",
                    "PDF & DOCX reports",
                    "Email support"
                ]
            },
            {
                "name": "pro",
                "display_name": "Pro",
                "description": "For growing businesses and agencies",
                "price": 99.0,
                "stripe_price_id": os.getenv("STRIPE_PRICE_PRO", "price_REPLACE_WITH_YOUR_PRO_PRICE_ID"),
                "max_audits_per_month": 50,
                "max_pages_per_audit": 20,
                "features": [
                    "50 audits per month",
                    "20 pages per audit",
                    "All 132 SEO checks",
                    "AI-powered insights",
                    "Chat with AI expert",
                    "PDF & DOCX reports",
                    "Priority support",
                    "API access"
                ]
            },
            {
                "name": "enterprise",
                "display_name": "Enterprise",
                "description": "For large organizations",
                "price": 299.0,
                "stripe_price_id": os.getenv("STRIPE_PRICE_ENTERPRISE", "price_REPLACE_WITH_YOUR_ENTERPRISE_PRICE_ID"),
                "max_audits_per_month": 999999,  # Unlimited
                "max_pages_per_audit": 20,
                "features": [
                    "Unlimited audits",
                    "20 pages per audit",
                    "All 132 SEO checks",
                    "AI-powered insights",
                    "Chat with AI expert",
                    "PDF & DOCX reports",
                    "Dedicated support",
                    "API access",
                    "Custom integrations",
                    "White-label reports"
                ]
            }
        ]
        
        created_plans = {}
        for plan_data in plans_data:
            plan = Plan(
                id=str(uuid.uuid4()),
                **plan_data,
                is_active=True
            )
            db.add(plan)
            created_plans[plan_data['name']] = plan
        
        await db.commit()
        logger.info(f"Created {len(plans_data)} plans")
        
        # Create superadmin user
        superadmin = User(
            id=str(uuid.uuid4()),
            email="superadmin@test.com",
            password_hash=get_password_hash("test123"),
            full_name="Super Admin",
            role=UserRole.SUPERADMIN,
            is_active=True
        )
        db.add(superadmin)
        
        # Give superadmin enterprise plan
        admin_subscription = Subscription(
            id=str(uuid.uuid4()),
            user_id=superadmin.id,
            plan_id=created_plans['enterprise'].id,
            status=SubscriptionStatus.ACTIVE,
            audits_used_this_month=0
        )
        db.add(admin_subscription)
        
        await db.commit()
        logger.info("Created superadmin user: superadmin@test.com / test123")
        
        # Create a test user
        test_user = User(
            id=str(uuid.uuid4()),
            email="test@example.com",
            password_hash=get_password_hash("test123"),
            full_name="Test User",
            role=UserRole.USER,
            is_active=True
        )
        db.add(test_user)
        
        # Give test user free plan
        test_subscription = Subscription(
            id=str(uuid.uuid4()),
            user_id=test_user.id,
            plan_id=created_plans['free'].id,
            status=SubscriptionStatus.ACTIVE,
            audits_used_this_month=0
        )
        db.add(test_subscription)
        
        await db.commit()
        logger.info("Created test user: test@example.com / test123")
        
        # Create default themes
        themes_data = [
            {
                "name": "Lavender Dream",
                "primary_color": "#a78bfa",  # Soft purple
                "secondary_color": "#fbbf24",  # Soft amber
                "accent_color": "#34d399",  # Soft emerald
                "background_color": "#0f172a",
                "surface_color": "#1e293b",
                "text_primary": "#f8fafc",
                "text_secondary": "#cbd5e1",
                "is_active": True  # Default active theme
            },
            {
                "name": "Ocean Breeze",
                "primary_color": "#60a5fa",  # Soft blue
                "secondary_color": "#a78bfa",  # Soft purple
                "accent_color": "#34d399",  # Soft emerald
                "background_color": "#0c4a6e",
                "surface_color": "#075985",
                "text_primary": "#f0f9ff",
                "text_secondary": "#bae6fd"
            },
            {
                "name": "Sunset Glow",
                "primary_color": "#fb923c",  # Soft orange
                "secondary_color": "#f472b6",  # Soft pink
                "accent_color": "#fbbf24",  # Soft amber
                "background_color": "#431407",
                "surface_color": "#7c2d12",
                "text_primary": "#fff7ed",
                "text_secondary": "#fed7aa"
            },
            {
                "name": "Mint Fresh",
                "primary_color": "#34d399",  # Soft emerald
                "secondary_color": "#60a5fa",  # Soft blue
                "accent_color": "#a78bfa",  # Soft purple
                "background_color": "#022c22",
                "surface_color": "#064e3b",
                "text_primary": "#ecfdf5",
                "text_secondary": "#a7f3d0"
            },
            {
                "name": "Rose Garden",
                "primary_color": "#f472b6",  # Soft pink
                "secondary_color": "#a78bfa",  # Soft purple
                "accent_color": "#fb923c",  # Soft orange
                "background_color": "#4c0519",
                "surface_color": "#831843",
                "text_primary": "#fdf2f8",
                "text_secondary": "#fbcfe8"
            }
        ]
        
        for theme_data in themes_data:
            theme = Theme(
                id=str(uuid.uuid4()),
                **theme_data
            )
            db.add(theme)
        
        await db.commit()
        logger.info(f"Created {len(themes_data)} default themes")
    
    logger.info("\n=== Database initialization complete ===")
    logger.info("Superadmin: superadmin@test.com / test123")
    logger.info("Test User: test@example.com / test123")
    logger.info("Default theme: Lavender Dream (active)")


if __name__ == "__main__":
    asyncio.run(init_database())
