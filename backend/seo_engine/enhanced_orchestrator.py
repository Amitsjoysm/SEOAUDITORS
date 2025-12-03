"""
Enhanced SEO Orchestrator with Sub-Agents
Coordinates multiple specialized agents for comprehensive SEO analysis.
Integrates with all external APIs (DataForSEO, Lighthouse, GSC, GA, Exa.ai)
"""
import asyncio
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from seo_engine.multi_llm_client import get_active_llm_client
from services.dataforseo_service import get_dataforseo_client
from services.lighthouse_service import lighthouse_service
from seo_engine.research_agent import ResearchAgent

logger = logging.getLogger(__name__)


class SEOSubAgent:
    """Base class for specialized SEO sub-agents"""
    
    def __init__(self, name: str, llm_client):
        self.name = name
        self.llm_client = llm_client
    
    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Override in subclasses"""
        raise NotImplementedError


class TechnicalSEOAgent(SEOSubAgent):
    """Analyzes technical SEO issues"""
    
    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze technical SEO aspects"""
        url = context.get('url')
        crawl_data = context.get('crawl_data', {})
        lighthouse_data = context.get('lighthouse_data', {})
        
        prompt = f"""You are a Technical SEO expert. Analyze this website's technical SEO.

URL: {url}

Crawl Data Summary:
- Pages crawled: {len(crawl_data.get('pages', []))}
- Has robots.txt: {crawl_data.get('has_robots', False)}
- Has sitemap: {crawl_data.get('has_sitemap', False)}
- HTTPS: {crawl_data.get('is_https', False)}

Lighthouse Technical Scores:
- Performance: {lighthouse_data.get('performance_score')}
- Accessibility: {lighthouse_data.get('accessibility_score')}
- Best Practices: {lighthouse_data.get('best_practices_score')}
- SEO: {lighthouse_data.get('seo_score')}

Provide a concise technical SEO analysis with:
1. Critical issues
2. Technical strengths
3. Priority improvements
4. Implementation difficulty (easy/medium/hard)

Keep response under 300 words."""
        
        try:
            response = await self.llm_client.generate(prompt, max_tokens=500)
            return {
                "success": True,
                "agent": self.name,
                "analysis": response,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Technical SEO Agent error: {e}")
            return {"success": False, "error": str(e)}


class ContentOptimizationAgent(SEOSubAgent):
    """Analyzes content quality and optimization opportunities"""
    
    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze content optimization opportunities"""
        url = context.get('url')
        crawl_data = context.get('crawl_data', {})
        keyword_data = context.get('keyword_data', {})
        
        prompt = f"""You are a Content SEO expert specializing in creating content that ranks high in LLM recommendations and search results.

URL: {url}

Content Overview:
- Pages: {len(crawl_data.get('pages', []))}
- Average word count: {crawl_data.get('avg_word_count', 'N/A')}
- Has blog: {crawl_data.get('has_blog', False)}

Target Keywords: {', '.join(keyword_data.get('keywords', [])[:5])}

Analyze and provide:
1. Content gaps (missing topics that competitors cover)
2. Content quality assessment
3. LLM optimization tips (how to make content LLM-friendly for Claude, GPT, Gemini recommendations)
4. Quick wins for better rankings
5. Content that will bring organic traffic

Focus on actionable recommendations that help this site rank higher in AI/LLM recommendations.
Keep response under 300 words."""
        
        try:
            response = await self.llm_client.generate(prompt, max_tokens=500)
            return {
                "success": True,
                "agent": self.name,
                "analysis": response,
                "llm_focus": True,  # Flag for LLM optimization
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Content Optimization Agent error: {e}")
            return {"success": False, "error": str(e)}


class CompetitorAnalysisAgent(SEOSubAgent):
    """Analyzes competitors and identifies opportunities"""
    
    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze competitors"""
        url = context.get('url')
        competitor_data = context.get('competitor_data', {})
        serp_data = context.get('serp_data', {})
        
        competitors = competitor_data.get('competitors', [])[:5]
        
        prompt = f"""You are a Competitive SEO analyst. Analyze competitors for {url}.

Top 5 Competitors:
{chr(10).join([f"- {comp.get('domain', 'N/A')} (DA: {comp.get('domain_authority', 'N/A')})" for comp in competitors])}

SERP Analysis:
- Target ranking: {serp_data.get('current_position', 'Not ranking')}
- Featured snippets captured: {serp_data.get('has_featured_snippet', False)}

Provide:
1. What competitors do better
2. Keyword gaps we can exploit
3. Content opportunities they're missing
4. Backlink opportunities
5. Quick wins to outrank them

Keep response under 300 words."""
        
        try:
            response = await self.llm_client.generate(prompt, max_tokens=500)
            return {
                "success": True,
                "agent": self.name,
                "analysis": response,
                "competitive_intel": True,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Competitor Analysis Agent error: {e}")
            return {"success": False, "error": str(e)}


class BacklinkAnalysisAgent(SEOSubAgent):
    """Analyzes backlink profile and opportunities"""
    
    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze backlinks"""
        url = context.get('url')
        backlink_data = context.get('backlink_data', {})
        
        prompt = f"""You are a Backlink SEO expert. Analyze backlink profile for {url}.

Backlink Summary:
- Total backlinks: {backlink_data.get('total_backlinks', 0)}
- Referring domains: {backlink_data.get('referring_domains', 0)}
- Domain authority: {backlink_data.get('domain_authority', 'N/A')}
- Toxic links: {backlink_data.get('toxic_links', 0)}

Provide:
1. Backlink profile health assessment
2. Link building opportunities
3. Toxic links to disavow (if any)
4. Anchor text optimization
5. Strategies to acquire high-quality backlinks

Keep response under 250 words."""
        
        try:
            response = await self.llm_client.generate(prompt, max_tokens=400)
            return {
                "success": True,
                "agent": self.name,
                "analysis": response,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Backlink Analysis Agent error: {e}")
            return {"success": False, "error": str(e)}


class PerformanceAgent(SEOSubAgent):
    """Analyzes site performance and Core Web Vitals"""
    
    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze performance"""
        url = context.get('url')
        lighthouse_data = context.get('lighthouse_data', {})
        cwv = lighthouse_data.get('core_web_vitals', {})
        
        prompt = f"""You are a Web Performance expert. Analyze performance for {url}.

Lighthouse Performance Score: {lighthouse_data.get('performance_score')}/100

Core Web Vitals:
- LCP: {cwv.get('lcp', {}).get('display_value', 'N/A')}
- FID: {cwv.get('fid', {}).get('display_value', 'N/A')}
- CLS: {cwv.get('cls', {}).get('display_value', 'N/A')}
- FCP: {cwv.get('fcp', {}).get('display_value', 'N/A')}
- TTI: {cwv.get('tti', {}).get('display_value', 'N/A')}

Top Opportunities:
{chr(10).join([f"- {opp.get('title')}" for opp in lighthouse_data.get('opportunities', [])[:5]])}

Provide:
1. Performance bottlenecks
2. Priority optimizations
3. Expected impact of fixes
4. Implementation steps

Keep response under 250 words."""
        
        try:
            response = await self.llm_client.generate(prompt, max_tokens=400)
            return {
                "success": True,
                "agent": self.name,
                "analysis": response,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Performance Agent error: {e}")
            return {"success": False, "error": str(e)}


class KeywordResearchAgent(SEOSubAgent):
    """Identifies keyword opportunities"""
    
    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze keyword opportunities"""
        url = context.get('url')
        keyword_data = context.get('keyword_data', {})
        
        prompt = f"""You are a Keyword Research expert. Find keyword opportunities for {url}.

Current Keywords:
{chr(10).join([f"- {kw.get('keyword', 'N/A')} (Vol: {kw.get('search_volume', 'N/A')}, Diff: {kw.get('difficulty', 'N/A')})" for kw in keyword_data.get('keywords', [])[:10]])}

Keyword Gaps (competitors rank, we don't):
{chr(10).join([f"- {gap.get('keyword', 'N/A')}" for gap in keyword_data.get('gaps', [])[:10]])}

Provide:
1. High-opportunity keywords (high volume, low competition)
2. Long-tail keywords to target
3. Featured snippet opportunities
4. Content strategy for top keywords
5. Keywords for LLM optimization (terms that AI models reference frequently)

Keep response under 300 words."""
        
        try:
            response = await self.llm_client.generate(prompt, max_tokens=500)
            return {
                "success": True,
                "agent": self.name,
                "analysis": response,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Keyword Research Agent error: {e}")
            return {"success": False, "error": str(e)}


class EnhancedSEOOrchestrator:
    """
    Enhanced orchestrator that coordinates all sub-agents and API integrations
    Main goal: Help users rank higher in search and LLM recommendations
    """
    
    def __init__(self):
        self.llm_client = None
        self.sub_agents: Dict[str, SEOSubAgent] = {}
        self.research_agent = None
    
    async def initialize(self, db):
        """Initialize orchestrator with LLM and sub-agents"""
        try:
            # Get active LLM
            self.llm_client = await get_active_llm_client(db)
            
            # Initialize research agent
            self.research_agent = ResearchAgent()
            
            # Initialize sub-agents
            self.sub_agents = {
                "technical": TechnicalSEOAgent("Technical SEO Agent", self.llm_client),
                "content": ContentOptimizationAgent("Content Optimization Agent", self.llm_client),
                "competitor": CompetitorAnalysisAgent("Competitor Analysis Agent", self.llm_client),
                "backlink": BacklinkAnalysisAgent("Backlink Analysis Agent", self.llm_client),
                "performance": PerformanceAgent("Performance Agent", self.llm_client),
                "keyword": KeywordResearchAgent("Keyword Research Agent", self.llm_client),
            }
            
            logger.info("Enhanced SEO Orchestrator initialized with 6 sub-agents")
            
        except Exception as e:
            logger.error(f"Error initializing orchestrator: {e}")
            raise
    
    async def run_comprehensive_analysis(
        self,
        url: str,
        crawl_data: Dict[str, Any],
        db
    ) -> Dict[str, Any]:
        """
        Run comprehensive SEO analysis using all sub-agents and APIs
        This is the main orchestration method
        """
        start_time = time.time()
        logger.info(f"Starting comprehensive analysis for {url}")
        
        try:
            # Ensure orchestrator is initialized
            if not self.llm_client:
                await self.initialize(db)
            
            # Step 1: Gather data from external APIs concurrently
            api_tasks = []
            
            # Lighthouse analysis
            api_tasks.append(self._run_lighthouse(url))
            
            # DataForSEO analyses
            dataforseo_client = await get_dataforseo_client()
            api_tasks.append(self._run_dataforseo_serp(url, dataforseo_client))
            api_tasks.append(self._run_dataforseo_competitors(url, dataforseo_client))
            api_tasks.append(self._run_dataforseo_backlinks(url, dataforseo_client))
            api_tasks.append(self._run_dataforseo_keywords(url, crawl_data, dataforseo_client))
            
            # Run all API calls concurrently
            api_results = await asyncio.gather(*api_tasks, return_exceptions=True)
            
            lighthouse_data, serp_data, competitor_data, backlink_data, keyword_data = api_results
            
            # Handle exceptions
            lighthouse_data = lighthouse_data if not isinstance(lighthouse_data, Exception) else {}
            serp_data = serp_data if not isinstance(serp_data, Exception) else {}
            competitor_data = competitor_data if not isinstance(competitor_data, Exception) else {}
            backlink_data = backlink_data if not isinstance(backlink_data, Exception) else {}
            keyword_data = keyword_data if not isinstance(keyword_data, Exception) else {}
            
            # Step 2: Create context for sub-agents
            context = {
                "url": url,
                "crawl_data": crawl_data,
                "lighthouse_data": lighthouse_data,
                "serp_data": serp_data,
                "competitor_data": competitor_data,
                "backlink_data": backlink_data,
                "keyword_data": keyword_data,
            }
            
            # Step 3: Run sub-agents concurrently
            agent_tasks = [
                agent.analyze(context)
                for agent in self.sub_agents.values()
            ]
            
            agent_results = await asyncio.gather(*agent_tasks, return_exceptions=True)
            
            # Step 4: Synthesize results
            synthesis = await self._synthesize_results(url, context, agent_results)
            
            execution_time = time.time() - start_time
            
            return {
                "success": True,
                "url": url,
                "api_data": {
                    "lighthouse": lighthouse_data,
                    "serp": serp_data,
                    "competitors": competitor_data,
                    "backlinks": backlink_data,
                    "keywords": keyword_data,
                },
                "agent_analyses": {
                    agent.name: result
                    for agent, result in zip(self.sub_agents.values(), agent_results)
                    if not isinstance(result, Exception)
                },
                "synthesis": synthesis,
                "execution_time_seconds": round(execution_time, 2),
                "timestamp": datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Orchestrator error: {e}")
            return {
                "success": False,
                "error": str(e),
                "url": url
            }
    
    async def _run_lighthouse(self, url: str) -> Dict[str, Any]:
        """Run Lighthouse audit"""
        try:
            result = await lighthouse_service.run_audit(url)
            return result if result.get('success') else {}
        except Exception as e:
            logger.error(f"Lighthouse error: {e}")
            return {}
    
    async def _run_dataforseo_serp(self, url: str, client) -> Dict[str, Any]:
        """Get SERP data from DataForSEO"""
        try:
            # Extract domain from URL
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
            
            # For now, do a basic search with domain name
            result = await client.get_serp_rankings(domain)
            return result.get('data', {}) if result.get('success') else {}
        except Exception as e:
            logger.error(f"SERP analysis error: {e}")
            return {}
    
    async def _run_dataforseo_competitors(self, url: str, client) -> Dict[str, Any]:
        """Get competitors from DataForSEO"""
        try:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
            
            result = await client.get_competitors(domain)
            return result.get('data', {}) if result.get('success') else {}
        except Exception as e:
            logger.error(f"Competitor analysis error: {e}")
            return {}
    
    async def _run_dataforseo_backlinks(self, url: str, client) -> Dict[str, Any]:
        """Get backlink data from DataForSEO"""
        try:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
            
            result = await client.get_backlinks_summary(domain)
            return result.get('data', {}) if result.get('success') else {}
        except Exception as e:
            logger.error(f"Backlink analysis error: {e}")
            return {}
    
    async def _run_dataforseo_keywords(self, url: str, crawl_data: Dict, client) -> Dict[str, Any]:
        """Get keyword data from DataForSEO"""
        try:
            # Extract keywords from crawl data
            keywords = []
            for page in crawl_data.get('pages', [])[:5]:
                if page.get('title'):
                    keywords.append(page['title'])
            
            if not keywords:
                keywords = [url]
            
            result = await client.get_keyword_data(keywords[:10])
            return result.get('data', {}) if result.get('success') else {}
        except Exception as e:
            logger.error(f"Keyword analysis error: {e}")
            return {}
    
    async def _synthesize_results(
        self,
        url: str,
        context: Dict[str, Any],
        agent_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Synthesize all agent results into actionable recommendations"""
        prompt = f"""You are the Master SEO Strategist synthesizing insights from 6 specialist agents for {url}.

Agent Insights:
{chr(10).join([f"{i+1}. {result.get('agent', 'Unknown')}: {result.get('analysis', 'No analysis')[:200]}..." for i, result in enumerate(agent_results) if isinstance(result, dict) and result.get('success')])}

Based on ALL agent analyses, create:

1. **Executive Summary** (3 sentences max)
2. **Top 5 Priority Actions** (ranked by impact)
3. **Quick Wins** (can be done in < 1 day)
4. **Long-term Strategy** (3-6 months)
5. **LLM Optimization Tips** (how to make this site rank higher in Claude, GPT, Gemini recommendations)
6. **Expected Organic Traffic Increase** (realistic estimate if actions are taken)

Keep total response under 400 words. Be specific and actionable."""
        
        try:
            synthesis = await self.llm_client.generate(prompt, max_tokens=700)
            return {
                "synthesis": synthesis,
                "generated_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Synthesis error: {e}")
            return {"synthesis": "Error generating synthesis", "error": str(e)}
    
    async def generate_content_brief(
        self,
        keyword: str,
        competitor_data: Dict[str, Any],
        keyword_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate AI-powered content brief for a keyword"""
        prompt = f"""Create a detailed content brief for the keyword: "{keyword}"

Search Volume: {keyword_data.get('search_volume', 'N/A')}
Keyword Difficulty: {keyword_data.get('difficulty', 'N/A')}
CPC: ${keyword_data.get('cpc', 'N/A')}

Top 3 Competitors:
{chr(10).join([f"- {comp.get('url', 'N/A')}: {comp.get('title', 'N/A')}" for comp in competitor_data.get('top_results', [])[:3]])}

Generate:
1. **Recommended Title** (SEO + LLM optimized)
2. **Meta Description** (155 characters)
3. **Content Structure** (H2 and H3 headings)
4. **Word Count Target**
5. **Key Points to Cover**
6. **LSI Keywords to Include**
7. **Internal/External Linking Strategy**
8. **LLM Optimization**: How to structure content so AI models (GPT, Claude, Gemini) recommend this page

Keep response under 500 words."""
        
        try:
            brief = await self.llm_client.generate(prompt, max_tokens=800)
            return {
                "success": True,
                "keyword": keyword,
                "brief": brief,
                "generated_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Content brief error: {e}")
            return {"success": False, "error": str(e)}


# Global instance
enhanced_orchestrator = EnhancedSEOOrchestrator()
