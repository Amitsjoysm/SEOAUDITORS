"""
API Integration Manager
Centralized management for all external API integrations with:
- API key pool management and rotation
- Health monitoring and circuit breaker
- Rate limiting and caching
- Error handling and retry logic
"""
import os
import asyncio
import time
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from models import APIKeyPool, APIIntegrationStatus, APIServiceType
from utils.encryption import EncryptionService

logger = logging.getLogger(__name__)


class CircuitBreaker:
    """Circuit breaker pattern for API failures"""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half_open
    
    def call_failed(self):
        """Record a failure"""
        self.failures += 1
        self.last_failure_time = time.time()
        
        if self.failures >= self.failure_threshold:
            self.state = "open"
            logger.warning(f"Circuit breaker opened after {self.failures} failures")
    
    def call_succeeded(self):
        """Record a success"""
        self.failures = 0
        self.state = "closed"
    
    def can_attempt(self) -> bool:
        """Check if we can attempt a call"""
        if self.state == "closed":
            return True
        
        if self.state == "open":
            # Check if timeout has passed
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "half_open"
                return True
            return False
        
        # half_open - try one request
        return True


class APIIntegrationManager:
    """
    Manages all external API integrations with:
    - Key rotation
    - Health monitoring
    - Rate limiting
    - Caching
    - Circuit breaker pattern
    """
    
    def __init__(self):
        self.encryption_service = EncryptionService()
        self.circuit_breakers: Dict[APIServiceType, CircuitBreaker] = {}
        self.request_times: Dict[APIServiceType, List[float]] = {}
        self.cache: Dict[str, Any] = {}
    
    def get_circuit_breaker(self, service: APIServiceType) -> CircuitBreaker:
        """Get or create circuit breaker for service"""
        if service not in self.circuit_breakers:
            self.circuit_breakers[service] = CircuitBreaker()
        return self.circuit_breakers[service]
    
    async def get_api_key(
        self, 
        db: AsyncSession, 
        service: APIServiceType
    ) -> Optional[Dict[str, str]]:
        """
        Get an API key from the pool with round-robin rotation
        Returns dict with 'api_key' and optionally 'api_username'
        """
        try:
            # Get all active keys for this service, ordered by priority and last used
            result = await db.execute(
                select(APIKeyPool)
                .where(
                    APIKeyPool.service_name == service,
                    APIKeyPool.is_active == True,
                    APIKeyPool.health_status == "healthy"
                )
                .order_by(
                    APIKeyPool.priority.asc(),
                    APIKeyPool.last_used_at.asc().nullsfirst()
                )
            )
            keys = result.scalars().all()
            
            if not keys:
                logger.warning(f"No active API keys found for {service.value}")
                return None
            
            # Get the first available key (highest priority, least recently used)
            key_entry = keys[0]
            
            # Check quota
            if key_entry.quota_limit and key_entry.quota_used >= key_entry.quota_limit:
                logger.warning(f"Quota exceeded for key {key_entry.id}")
                return await self._get_fallback_key(db, service, [key_entry.id])
            
            # Update last used time
            key_entry.last_used_at = datetime.utcnow()
            await db.commit()
            
            # Decrypt and return key
            decrypted_key = self.encryption_service.decrypt(key_entry.api_key)
            
            result = {"api_key": decrypted_key}
            if key_entry.api_username:
                result["api_username"] = key_entry.api_username
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting API key for {service.value}: {e}")
            return None
    
    async def _get_fallback_key(
        self, 
        db: AsyncSession, 
        service: APIServiceType, 
        exclude_ids: List[str]
    ) -> Optional[Dict[str, str]]:
        """Get a fallback key excluding specified IDs"""
        try:
            result = await db.execute(
                select(APIKeyPool)
                .where(
                    APIKeyPool.service_name == service,
                    APIKeyPool.is_active == True,
                    APIKeyPool.health_status == "healthy",
                    ~APIKeyPool.id.in_(exclude_ids)
                )
                .order_by(APIKeyPool.priority.asc())
            )
            keys = result.scalars().all()
            
            if not keys:
                return None
            
            key_entry = keys[0]
            key_entry.last_used_at = datetime.utcnow()
            await db.commit()
            
            decrypted_key = self.encryption_service.decrypt(key_entry.api_key)
            result = {"api_key": decrypted_key}
            if key_entry.api_username:
                result["api_username"] = key_entry.api_username
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting fallback key: {e}")
            return None
    
    async def record_success(
        self, 
        db: AsyncSession, 
        service: APIServiceType,
        response_time_ms: float,
        key_id: Optional[str] = None
    ):
        """Record successful API call"""
        try:
            # Update circuit breaker
            circuit_breaker = self.get_circuit_breaker(service)
            circuit_breaker.call_succeeded()
            
            # Update integration status
            result = await db.execute(
                select(APIIntegrationStatus)
                .where(APIIntegrationStatus.service_name == service)
            )
            status = result.scalar_one_or_none()
            
            if status:
                status.success_count_24h += 1
                status.total_requests_today += 1
                status.is_healthy = True
                status.last_check_at = datetime.utcnow()
                
                # Update average response time
                if status.avg_response_time_ms:
                    status.avg_response_time_ms = (status.avg_response_time_ms + response_time_ms) / 2
                else:
                    status.avg_response_time_ms = response_time_ms
                
                # Update uptime percentage
                total_requests = status.success_count_24h + status.failure_count_24h
                if total_requests > 0:
                    status.uptime_percentage = (status.success_count_24h / total_requests) * 100
                
                await db.commit()
            
            # Update quota if key_id provided
            if key_id:
                result = await db.execute(
                    select(APIKeyPool).where(APIKeyPool.id == key_id)
                )
                key_entry = result.scalar_one_or_none()
                if key_entry:
                    key_entry.quota_used += 1
                    key_entry.consecutive_failures = 0
                    key_entry.health_status = "healthy"
                    await db.commit()
            
        except Exception as e:
            logger.error(f"Error recording success for {service.value}: {e}")
    
    async def record_failure(
        self, 
        db: AsyncSession, 
        service: APIServiceType,
        error_message: str,
        key_id: Optional[str] = None
    ):
        """Record failed API call"""
        try:
            # Update circuit breaker
            circuit_breaker = self.get_circuit_breaker(service)
            circuit_breaker.call_failed()
            
            # Update integration status
            result = await db.execute(
                select(APIIntegrationStatus)
                .where(APIIntegrationStatus.service_name == service)
            )
            status = result.scalar_one_or_none()
            
            if status:
                status.failure_count_24h += 1
                status.total_requests_today += 1
                status.error_message = error_message
                status.last_error_at = datetime.utcnow()
                status.last_check_at = datetime.utcnow()
                
                # Mark as unhealthy if failure rate is too high
                total_requests = status.success_count_24h + status.failure_count_24h
                if total_requests >= 10 and status.failure_count_24h / total_requests > 0.3:
                    status.is_healthy = False
                
                # Update uptime percentage
                if total_requests > 0:
                    status.uptime_percentage = (status.success_count_24h / total_requests) * 100
                
                await db.commit()
            
            # Update key health if key_id provided
            if key_id:
                result = await db.execute(
                    select(APIKeyPool).where(APIKeyPool.id == key_id)
                )
                key_entry = result.scalar_one_or_none()
                if key_entry:
                    key_entry.consecutive_failures += 1
                    
                    # Mark key as failed if too many consecutive failures
                    if key_entry.consecutive_failures >= 5:
                        key_entry.health_status = "failed"
                        logger.warning(f"API key {key_id} marked as failed")
                    elif key_entry.consecutive_failures >= 3:
                        key_entry.health_status = "degraded"
                    
                    await db.commit()
            
        except Exception as e:
            logger.error(f"Error recording failure for {service.value}: {e}")
    
    def is_rate_limited(self, service: APIServiceType, max_per_minute: int = 60) -> bool:
        """Check if service is rate limited"""
        if service not in self.request_times:
            self.request_times[service] = []
        
        now = time.time()
        # Remove requests older than 1 minute
        self.request_times[service] = [
            t for t in self.request_times[service] 
            if now - t < 60
        ]
        
        if len(self.request_times[service]) >= max_per_minute:
            return True
        
        self.request_times[service].append(now)
        return False
    
    def get_from_cache(self, cache_key: str) -> Optional[Any]:
        """Get value from cache"""
        if cache_key in self.cache:
            value, expiry = self.cache[cache_key]
            if time.time() < expiry:
                return value
            else:
                del self.cache[cache_key]
        return None
    
    def set_cache(self, cache_key: str, value: Any, ttl_seconds: int = 3600):
        """Set value in cache"""
        expiry = time.time() + ttl_seconds
        self.cache[cache_key] = (value, expiry)


# Global instance
api_manager = APIIntegrationManager()
