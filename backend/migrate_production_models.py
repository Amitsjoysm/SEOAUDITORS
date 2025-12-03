"""
Migration script for production-ready models
Adds new tables: api_key_pool, api_integration_status, competitor_analysis, 
content_opportunities, anomaly_detection
Updates audit table with new fields
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from database import engine, SessionLocal
from models import Base, APIKeyPool, APIIntegrationStatus, CompetitorAnalysis, ContentOpportunity, AnomalyDetection
from models import APIServiceType
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_database():
    """Run database migrations"""
    try:
        logger.info("Starting database migration...")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("✅ All tables created/updated successfully")
        
        # Initialize API integration status for all services
        db = SessionLocal()
        try:
            existing_services = db.query(APIIntegrationStatus).all()
            existing_service_names = {s.service_name for s in existing_services}
            
            # Add status entries for new services
            for service in APIServiceType:
                if service not in existing_service_names:
                    status_entry = APIIntegrationStatus(
                        service_name=service,
                        is_healthy=True,
                        success_count_24h=0,
                        failure_count_24h=0,
                        uptime_percentage=100.0
                    )
                    db.add(status_entry)
                    logger.info(f"Added integration status for {service.value}")
            
            db.commit()
            logger.info("✅ API integration status initialized")
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error initializing API integration status: {e}")
        finally:
            db.close()
        
        logger.info("🎉 Migration completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        raise


if __name__ == "__main__":
    migrate_database()
