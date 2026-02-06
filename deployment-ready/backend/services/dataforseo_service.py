"""
DataForSEO API Integration
Provides comprehensive SEO data:
- SERP rankings and competitors
- Keyword data (volume, difficulty, CPC)
- Backlink analysis
- On-page SEO analysis
- Domain analytics

API Documentation: https://docs.dataforseo.com/v3/
"""
import os
import base64
import aiohttp
import asyncio
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DataForSEOClient:
    """
    DataForSEO API client for SEO data
    """
    
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.base_url = "https://api.dataforseo.com/v3"
        
        # Create auth header
        credentials = f"{username}:{password}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        self.headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/json"
        }
    
    async def _make_request(
        self,
        endpoint: str,
        method: str = "POST",
        data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make API request with error handling"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            start_time = time.time()
            
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method,
                    url,
                    headers=self.headers,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    response_time = (time.time() - start_time) * 1000  # ms
                    
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "success": True,
                            "data": result,
                            "response_time_ms": response_time
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"DataForSEO API error: {response.status} - {error_text}")
                        return {
                            "success": False,
                            "error": f"API returned status {response.status}: {error_text}",
                            "response_time_ms": response_time
                        }
        
        except asyncio.TimeoutError:
            return {"success": False, "error": "Request timeout"}
        except Exception as e:
            logger.error(f"DataForSEO request error: {e}")
            return {"success": False, "error": str(e)}
    
    # ========================================================================
    # SERP API - Get search rankings and competitors
    # ========================================================================
    
    async def get_serp_rankings(
        self,
        keyword: str,
        location_code: int = 2840,  # USA
        language_code: str = "en",
        device: str = "desktop"
    ) -> Dict[str, Any]:
        """
        Get SERP rankings for a keyword
        Returns top 100 organic results with URLs, titles, descriptions
        """
        endpoint = "/serp/google/organic/live/advanced"
        
        data = [{
            "keyword": keyword,
            "location_code": location_code,
            "language_code": language_code,
            "device": device,
            "calculate_rectangles": True
        }]
        
        return await self._make_request(endpoint, data=data)
    
    async def get_serp_features(
        self,
        keyword: str,
        location_code: int = 2840
    ) -> Dict[str, Any]:
        """Get SERP features (featured snippets, PAA, knowledge graph, etc.)"""
        endpoint = "/serp/google/organic/live/advanced"
        
        data = [{
            "keyword": keyword,
            "location_code": location_code,
            "depth": 100
        }]
        
        return await self._make_request(endpoint, data=data)
    
    # ========================================================================
    # Keywords API - Keyword research and opportunities
    # ========================================================================
    
    async def get_keyword_data(
        self,
        keywords: List[str],
        location_code: int = 2840
    ) -> Dict[str, Any]:
        """
        Get search volume, CPC, competition for keywords
        """
        endpoint = "/keywords_data/google/search_volume/live"
        
        data = [{
            "keywords": keywords,
            "location_code": location_code
        }]
        
        return await self._make_request(endpoint, data=data)
    
    async def get_keyword_ideas(
        self,
        keyword: str,
        location_code: int = 2840,
        include_seed_keyword: bool = True
    ) -> Dict[str, Any]:
        """Get keyword ideas and related keywords"""
        endpoint = "/keywords_data/google/keyword_ideas/live"
        
        data = [{
            "keyword": keyword,
            "location_code": location_code,
            "include_seed_keyword": include_seed_keyword,
            "limit": 100
        }]
        
        return await self._make_request(endpoint, data=data)
    
    async def get_keyword_suggestions(
        self,
        keyword: str,
        location_code: int = 2840
    ) -> Dict[str, Any]:
        """Get autocomplete keyword suggestions"""
        endpoint = "/keywords_data/google/autocomplete/live"
        
        data = [{
            "keyword": keyword,
            "location_code": location_code
        }]
        
        return await self._make_request(endpoint, data=data)
    
    # ========================================================================
    # Backlinks API - Backlink analysis
    # ========================================================================
    
    async def get_backlinks_summary(
        self,
        target: str,
        target_type: str = "domain"  # domain, subdomain, url, url_path
    ) -> Dict[str, Any]:
        """
        Get backlink summary (total backlinks, referring domains, etc.)
        """
        endpoint = "/backlinks/summary/live"
        
        data = [{
            "target": target,
            "mode": target_type,
            "internal_list_limit": 10,
            "backlinks_status_type": "all"
        }]
        
        return await self._make_request(endpoint, data=data)
    
    async def get_backlinks_list(
        self,
        target: str,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get list of backlinks"""
        endpoint = "/backlinks/backlinks/live"
        
        data = [{
            "target": target,
            "mode": "domain",
            "limit": limit,
            "offset": offset,
            "order_by": ["rank,desc"],
            "backlinks_status_type": "all"
        }]
        
        return await self._make_request(endpoint, data=data)
    
    async def get_referring_domains(
        self,
        target: str,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Get list of referring domains"""
        endpoint = "/backlinks/referring_domains/live"
        
        data = [{
            "target": target,
            "mode": "domain",
            "limit": limit,
            "order_by": ["rank,desc"]
        }]
        
        return await self._make_request(endpoint, data=data)
    
    async def get_anchors(
        self,
        target: str,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Get anchor text distribution"""
        endpoint = "/backlinks/anchors/live"
        
        data = [{
            "target": target,
            "mode": "domain",
            "limit": limit
        }]
        
        return await self._make_request(endpoint, data=data)
    
    # ========================================================================
    # On-Page API - Technical SEO analysis
    # ========================================================================
    
    async def create_onpage_task(
        self,
        target: str,
        max_crawl_pages: int = 100
    ) -> Dict[str, Any]:
        """
        Create on-page crawl task
        This is async - need to check status and get results later
        """
        endpoint = "/on_page/task_post"
        
        data = [{
            "target": target,
            "max_crawl_pages": max_crawl_pages,
            "load_resources": True,
            "enable_javascript": True,
            "custom_js": "",
            "store_raw_html": False
        }]
        
        return await self._make_request(endpoint, data=data)
    
    async def get_onpage_summary(
        self,
        task_id: str
    ) -> Dict[str, Any]:
        """Get on-page crawl summary"""
        endpoint = f"/on_page/summary/{task_id}"
        
        return await self._make_request(endpoint, method="GET")
    
    async def get_onpage_pages(
        self,
        task_id: str,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Get crawled pages from on-page task"""
        endpoint = f"/on_page/pages"
        
        data = [{
            "id": task_id,
            "limit": limit,
            "filters": [
                ["resource_type", "=", "html"]
            ]
        }]
        
        return await self._make_request(endpoint, data=data)
    
    # ========================================================================
    # Domain Analytics API - Competitor analysis
    # ========================================================================
    
    async def get_domain_overview(
        self,
        target: str,
        location_code: int = 2840
    ) -> Dict[str, Any]:
        """
        Get domain overview (organic traffic, rankings, competitors)
        """
        endpoint = "/dataforseo_labs/google/domain_metrics/live"
        
        data = [{
            "target": target,
            "location_code": location_code
        }]
        
        return await self._make_request(endpoint, data=data)
    
    async def get_domain_rank_overview(
        self,
        targets: List[str],
        location_code: int = 2840
    ) -> Dict[str, Any]:
        """Get ranking metrics for multiple domains"""
        endpoint = "/dataforseo_labs/google/bulk_traffic_estimation/live"
        
        data = [{
            "targets": targets,
            "location_code": location_code
        }]
        
        return await self._make_request(endpoint, data=data)
    
    async def get_competitors(
        self,
        target: str,
        location_code: int = 2840,
        limit: int = 20
    ) -> Dict[str, Any]:
        """Get competitor domains"""
        endpoint = "/dataforseo_labs/google/competitors_domain/live"
        
        data = [{
            "target": target,
            "location_code": location_code,
            "limit": limit
        }]
        
        return await self._make_request(endpoint, data=data)
    
    async def get_keyword_gaps(
        self,
        target: str,
        competitor: str,
        location_code: int = 2840
    ) -> Dict[str, Any]:
        """Find keyword gaps between target and competitor"""
        endpoint = "/dataforseo_labs/google/keywords_for_site/live"
        
        # Get keywords for both domains
        data = [{
            "target": target,
            "location_code": location_code,
            "filters": [
                ["keyword_data.keyword_info.search_volume", ">", 100]
            ],
            "limit": 100
        }]
        
        return await self._make_request(endpoint, data=data)


# Helper function to get client with stored credentials
async def get_dataforseo_client(username: str = None, password: str = None) -> DataForSEOClient:
    """Get DataForSEO client with credentials"""
    if not username:
        username = os.getenv("DATAFORSEO_USERNAME", "evelyene@devbaytech.com")
    if not password:
        password = os.getenv("DATAFORSEO_PASSWORD", "6ecff7f6476fd099")
    
    return DataForSEOClient(username, password)
