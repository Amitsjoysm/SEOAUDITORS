"""
API Integration Status Routes
Monitor health, uptime, and performance of all API integrations
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Any
from pydantic import BaseModel
from datetime import datetime

from database import get_db
from auth import get_current_user, require_superadmin
from models import User, APIIntegrationStatus, APIServiceType
from services.lighthouse_service import lighthouse_service
from services.dataforseo_service import get_dataforseo_client

router = APIRouter(prefix="/admin/integrations", tags=["Admin - Integrations"])


# Schemas
class IntegrationStatusResponse(BaseModel):
    id: str
    service_name: str
    is_healthy: bool
    last_check_at: datetime | None
    success_count_24h: int
    failure_count_24h: int
    avg_response_time_ms: float | None
    uptime_percentage: float | None
    error_message: str | None
    last_error_at: datetime | None
    total_requests_today: int
    cost_today: float
    
    class Config:
        from_attributes = True


class IntegrationTestResult(BaseModel):
    service_name: str
    success: bool
    response_time_ms: float | None = None
    error: str | None = None
    details: Dict[str, Any] | None = None


# Routes
@router.get("/", response_model=List[IntegrationStatusResponse])
async def list_integration_status(
    current_user: User = Depends(require_superadmin),
    db: AsyncSession = Depends(get_db)
):
    """Get status of all API integrations"""
    result = await db.execute(
        select(APIIntegrationStatus).order_by(APIIntegrationStatus.service_name)
    )
    statuses = result.scalars().all()
    
    return [IntegrationStatusResponse.from_orm(status) for status in statuses]


@router.get("/{service_name}", response_model=IntegrationStatusResponse)
async def get_integration_status(
    service_name: APIServiceType,
    current_user: User = Depends(require_superadmin),
    db: AsyncSession = Depends(get_db)
):
    """Get status of specific integration"""
    result = await db.execute(
        select(APIIntegrationStatus)
        .where(APIIntegrationStatus.service_name == service_name)
    )
    status = result.scalar_one_or_none()
    
    if not status:
        raise HTTPException(status_code=404, detail="Integration status not found")
    
    return IntegrationStatusResponse.from_orm(status)


@router.post("/test/{service_name}", response_model=IntegrationTestResult)
async def test_integration(
    service_name: APIServiceType,
    current_user: User = Depends(require_superadmin),
    db: AsyncSession = Depends(get_db)
):
    """Test specific API integration"""
    import time
    
    start_time = time.time()
    
    try:
        if service_name == APIServiceType.LIGHTHOUSE:
            # Test Lighthouse
            installed = await lighthouse_service.check_lighthouse_installed()
            response_time = (time.time() - start_time) * 1000
            
            if installed:
                return IntegrationTestResult(
                    service_name=service_name.value,
                    success=True,
                    response_time_ms=response_time,
                    details={"status": "Lighthouse CLI is installed and ready"}
                )
            else:
                return IntegrationTestResult(
                    service_name=service_name.value,
                    success=False,
                    error="Lighthouse CLI not installed"
                )
        
        elif service_name == APIServiceType.DATAFORSEO:
            # Test DataForSEO
            client = await get_dataforseo_client()
            result = await client.get_serp_rankings("test query", location_code=2840)
            response_time = (time.time() - start_time) * 1000
            
            if result.get('success'):
                return IntegrationTestResult(
                    service_name=service_name.value,
                    success=True,
                    response_time_ms=response_time,
                    details={"status": "DataForSEO API is working"}
                )
            else:
                return IntegrationTestResult(
                    service_name=service_name.value,
                    success=False,
                    response_time_ms=response_time,
                    error=result.get('error', 'Unknown error')
                )
        
        elif service_name == APIServiceType.EXA_AI:
            # Test Exa.ai
            import os
            exa_key = os.getenv("EXA_API_KEY")
            if exa_key:
                return IntegrationTestResult(
                    service_name=service_name.value,
                    success=True,
                    response_time_ms=(time.time() - start_time) * 1000,
                    details={"status": "Exa.ai API key is configured"}
                )
            else:
                return IntegrationTestResult(
                    service_name=service_name.value,
                    success=False,
                    error="Exa.ai API key not configured"
                )
        
        elif service_name in [APIServiceType.GOOGLE_SEARCH_CONSOLE, APIServiceType.GOOGLE_ANALYTICS]:
            # Test Google APIs (OAuth flow required)
            return IntegrationTestResult(
                service_name=service_name.value,
                success=False,
                error="OAuth authentication required. Not yet implemented."
            )
        
        else:
            # Generic test for other services
            return IntegrationTestResult(
                service_name=service_name.value,
                success=False,
                error="Test not implemented for this service"
            )
    
    except Exception as e:
        return IntegrationTestResult(
            service_name=service_name.value,
            success=False,
            error=str(e)
        )


@router.get("/dashboard/overview")
async def get_dashboard_overview(
    current_user: User = Depends(require_superadmin),
    db: AsyncSession = Depends(get_db)
):
    """Get overview dashboard data for all integrations"""
    result = await db.execute(select(APIIntegrationStatus))
    statuses = result.scalars().all()
    
    total_services = len(statuses)
    healthy_services = sum(1 for s in statuses if s.is_healthy)
    unhealthy_services = total_services - healthy_services
    
    total_requests_today = sum(s.total_requests_today for s in statuses)
    total_successes = sum(s.success_count_24h for s in statuses)
    total_failures = sum(s.failure_count_24h for s in statuses)
    total_cost_today = sum(s.cost_today for s in statuses)
    
    # Calculate overall uptime
    if total_successes + total_failures > 0:
        overall_uptime = (total_successes / (total_successes + total_failures)) * 100
    else:
        overall_uptime = 100.0
    
    # Get services by health status
    healthy_list = [
        {"name": s.service_name.value, "uptime": s.uptime_percentage}
        for s in statuses if s.is_healthy
    ]
    
    unhealthy_list = [
        {
            "name": s.service_name.value,
            "error": s.error_message,
            "last_error": s.last_error_at.isoformat() if s.last_error_at else None
        }
        for s in statuses if not s.is_healthy
    ]
    
    # Get average response times
    avg_response_times = [
        {
            "service": s.service_name.value,
            "avg_ms": s.avg_response_time_ms
        }
        for s in statuses if s.avg_response_time_ms
    ]
    avg_response_times.sort(key=lambda x: x['avg_ms'] or 0)
    
    return {
        "summary": {
            "total_services": total_services,
            "healthy_services": healthy_services,
            "unhealthy_services": unhealthy_services,
            "overall_uptime_percentage": round(overall_uptime, 2),
            "total_requests_today": total_requests_today,
            "total_successes_24h": total_successes,
            "total_failures_24h": total_failures,
            "total_cost_today": round(total_cost_today, 2)
        },
        "healthy_services": healthy_list,
        "unhealthy_services": unhealthy_list,
        "avg_response_times": avg_response_times[:10],
        "timestamp": datetime.utcnow().isoformat()
    }


@router.post("/reset-daily-stats")
async def reset_daily_stats(
    current_user: User = Depends(require_superadmin),
    db: AsyncSession = Depends(get_db)
):
    """Reset daily statistics for all integrations (run via cron)"""
    result = await db.execute(select(APIIntegrationStatus))
    statuses = result.scalars().all()
    
    for status in statuses:
        status.success_count_24h = 0
        status.failure_count_24h = 0
        status.total_requests_today = 0
        status.cost_today = 0.0
    
    await db.commit()
    
    return {
        "message": "Daily statistics reset successfully",
        "services_reset": len(statuses)
    }
