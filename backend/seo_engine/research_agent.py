"""Research Agent using Exa.ai for SEO insights and competitive analysis"""
import os
import logging
from typing import List, Dict, Any, Optional
from exa_py import Exa
import asyncio

logger = logging.getLogger(__name__)

EXA_API_KEY = os.getenv("EXA_API_KEY", "28a8cf69-fb6d-45db-8c2a-7f832d29aec3")


class SEOResearchAgent:
    """Sub-agent for conducting SEO research using Exa.ai"""
    
    def __init__(self):
        self.exa = Exa(api_key=EXA_API_KEY)
        self.max_results = 10
    
    async def research_keyword_trends(self, keyword: str) -> Dict[str, Any]:
        """Research trending content and insights for a keyword"""
        try:
            # Run in thread pool as Exa is synchronous
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None,
                lambda: self.exa.search(
                    f"SEO best practices for {keyword}",
                    num_results=5,
                    use_autoprompt=True
                )
            )
            
            insights = {
                "keyword": keyword,
                "trending_topics": [],
                "best_practices": [],
                "sources": []
            }
            
            for result in results.results:
                insights["sources"].append({
                    "title": result.title,
                    "url": result.url,
                    "published_date": getattr(result, 'published_date', None)
                })
            
            logger.info(f"Research completed for keyword: {keyword}")
            return insights
            
        except Exception as e:
            logger.error(f"Research failed for {keyword}: {str(e)}")
            return {
                "keyword": keyword,
                "error": str(e),
                "trending_topics": [],
                "best_practices": [],
                "sources": []
            }
    
    async def analyze_competitors(self, domain: str, keywords: List[str]) -> Dict[str, Any]:
        """Analyze competitor content and strategies"""
        try:
            loop = asyncio.get_event_loop()
            
            # Search for competitor content
            search_query = f"site:{domain} {' OR '.join(keywords[:3])}"
            results = await loop.run_in_executor(
                None,
                lambda: self.exa.search(
                    search_query,
                    num_results=5
                )
            )
            
            analysis = {
                "domain": domain,
                "keywords_analyzed": keywords,
                "top_content": [],
                "content_gaps": [],
                "opportunities": []
            }
            
            for result in results.results:
                analysis["top_content"].append({
                    "title": result.title,
                    "url": result.url
                })
            
            return analysis
            
        except Exception as e:
            logger.error(f"Competitor analysis failed for {domain}: {str(e)}")
            return {
                "domain": domain,
                "error": str(e),
                "top_content": [],
                "content_gaps": [],
                "opportunities": []
            }
    
    async def find_backlink_opportunities(self, topic: str, industry: str) -> List[Dict[str, str]]:
        """Find potential backlink opportunities in an industry"""
        try:
            loop = asyncio.get_event_loop()
            
            search_query = f"{industry} {topic} guest post OR contribute OR write for us"
            results = await loop.run_in_executor(
                None,
                lambda: self.exa.search(
                    search_query,
                    num_results=self.max_results,
                    use_autoprompt=True
                )
            )
            
            opportunities = []
            for result in results.results:
                opportunities.append({
                    "title": result.title,
                    "url": result.url,
                    "opportunity_type": "Guest Post" if "guest" in result.title.lower() else "Contribution"
                })
            
            logger.info(f"Found {len(opportunities)} backlink opportunities for {topic}")
            return opportunities
            
        except Exception as e:
            logger.error(f"Backlink research failed: {str(e)}")
            return []
    
    async def get_content_ideas(self, niche: str, keywords: List[str]) -> Dict[str, Any]:
        """Generate content ideas based on trending topics in a niche"""
        try:
            loop = asyncio.get_event_loop()
            
            # Search for trending content
            search_query = f"{niche} latest trends {' '.join(keywords[:3])}"
            results = await loop.run_in_executor(
                None,
                lambda: self.exa.search(
                    search_query,
                    num_results=10,
                    use_autoprompt=True
                )
            )
            
            content_ideas = {
                "niche": niche,
                "trending_topics": [],
                "content_formats": [],
                "suggested_titles": []
            }
            
            for result in results.results:
                content_ideas["trending_topics"].append(result.title)
                
                # Extract content format from title
                title_lower = result.title.lower()
                if "guide" in title_lower:
                    content_ideas["content_formats"].append("Comprehensive Guide")
                elif "how to" in title_lower:
                    content_ideas["content_formats"].append("Tutorial/How-To")
                elif "best" in title_lower or "top" in title_lower:
                    content_ideas["content_formats"].append("Listicle/Comparison")
            
            # Deduplicate formats
            content_ideas["content_formats"] = list(set(content_ideas["content_formats"]))
            
            return content_ideas
            
        except Exception as e:
            logger.error(f"Content ideas generation failed: {str(e)}")
            return {
                "niche": niche,
                "error": str(e),
                "trending_topics": [],
                "content_formats": [],
                "suggested_titles": []
            }
    
    async def research_technical_seo_updates(self) -> Dict[str, Any]:
        """Research latest technical SEO updates and best practices"""
        try:
            loop = asyncio.get_event_loop()
            
            results = await loop.run_in_executor(
                None,
                lambda: self.exa.search(
                    "latest technical SEO updates 2024 Google algorithm",
                    num_results=8,
                    use_autoprompt=True
                )
            )
            
            updates = {
                "latest_updates": [],
                "best_practices": [],
                "sources": []
            }
            
            for result in results.results:
                updates["latest_updates"].append(result.title)
                updates["sources"].append({
                    "title": result.title,
                    "url": result.url
                })
            
            return updates
            
        except Exception as e:
            logger.error(f"Technical SEO research failed: {str(e)}")
            return {
                "latest_updates": [],
                "best_practices": [],
                "sources": [],
                "error": str(e)
            }


# Global research agent instance
research_agent = SEOResearchAgent()
