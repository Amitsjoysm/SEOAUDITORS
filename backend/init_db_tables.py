"""Initialize database tables and seed data"""
import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import select
from database import engine, Base, AsyncSessionLocal
from models import User, Plan, Subscription, UserRole, SubscriptionStatus
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
    
    logger.info("\n=== Database initialization complete ===")
    logger.info("Superadmin: superadmin@test.com / test123")
    logger.info("Test User: test@example.com / test123")


if __name__ == "__main__":
    asyncio.run(init_database())
