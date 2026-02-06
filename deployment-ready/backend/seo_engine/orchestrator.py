"""AI Orchestrator for SEO Analysis using Groq API"""
import os
from typing import List, Dict, Any, Optional
import logging
from groq import Groq
import json
import asyncio
from functools import wraps
import time

logger = logging.getLogger(__name__)

# Groq API configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "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")
EXA_API_KEY = os.getenv("EXA_API_KEY", "28a8cf69-fb6d-45db-8c2a-7f832d29aec3")


def retry_on_failure(max_retries=3, delay=1):
    """Decorator for retry logic (Parlant.io-style reliability)"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        logger.error(f"Failed after {max_retries} attempts: {str(e)}")
                        raise
                    logger.warning(f"Attempt {attempt + 1} failed: {str(e)}. Retrying...")
                    await asyncio.sleep(delay * (attempt + 1))
            return None
        return wrapper
    return decorator


class SEOOrchestrator:
    """Orchestrator agent for SEO analysis and recommendations"""
    
    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY)
        self.model = "llama-3.3-70b-versatile"  # Fast, capable model
        self.conversation_history: List[Dict[str, str]] = []
        self.max_context_length = 8000  # tokens
    
    def _manage_context(self, new_message: str) -> List[Dict[str, str]]:
        """Manage conversation context to stay within token limits"""
        # Add new message
        self.conversation_history.append({"role": "user", "content": new_message})
        
        # Estimate token count (rough: 1 token ≈ 4 chars)
        total_chars = sum(len(msg["content"]) for msg in self.conversation_history)
        estimated_tokens = total_chars // 4
        
        # If exceeding limit, keep system message and recent messages
        if estimated_tokens > self.max_context_length:
            # Keep last N messages that fit
            kept_messages = []
            char_count = 0
            for msg in reversed(self.conversation_history):
                msg_chars = len(msg["content"])
                if char_count + msg_chars < self.max_context_length * 4:
                    kept_messages.insert(0, msg)
                    char_count += msg_chars
                else:
                    break
            self.conversation_history = kept_messages
        
        return self.conversation_history
    
    @retry_on_failure(max_retries=3, delay=2)
    async def analyze_audit_results(self, audit_results: List[Dict[str, Any]]) -> str:
        """Analyze audit results and provide comprehensive insights"""
        # Prepare summary of results
        failed_checks = [r for r in audit_results if r.get('status') == 'fail']
        warning_checks = [r for r in audit_results if r.get('status') == 'warning']
        passed_checks = [r for r in audit_results if r.get('status') == 'pass']
        
        summary = f"""
SEO Audit Results Summary:
- Total Checks: {len(audit_results)}
- Failed: {len(failed_checks)}
- Warnings: {len(warning_checks)}
- Passed: {len(passed_checks)}

Top Issues:
"""
        for check in failed_checks[:5]:
            summary += f"\n- {check.get('check_name')}: {check.get('cons', [])[0] if check.get('cons') else 'Issue detected'}"
        
        prompt = f"""
You are an expert SEO consultant analyzing a comprehensive website audit.

{summary}

Provide:
1. Executive Summary (2-3 sentences)
2. Top 3 Critical Issues requiring immediate attention
3. Quick Wins (3-5 easy fixes with high impact)
4. Long-term Recommendations
5. Estimated Impact on Rankings

Be specific, actionable, and prioritize by impact.
"""
        
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert SEO consultant providing actionable insights."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            analysis = response.choices[0].message.content
            logger.info("Successfully generated AI analysis")
            return analysis
            
        except Exception as e:
            logger.error(f"Error in AI analysis: {str(e)}")
            return "Unable to generate AI analysis. Please review the detailed check results."
    
    @retry_on_failure(max_retries=3, delay=2)
    async def chat(self, user_message: str, audit_context: Optional[Dict[str, Any]] = None) -> str:
        """Interactive chat about SEO audit results"""
        # Build context-aware prompt
        system_prompt = """You are an expert SEO consultant helping users understand and improve their website's SEO.
Provide specific, actionable advice. Reference the audit results when relevant.
Be concise but thorough. Use bullet points for clarity."""
        
        # Add audit context if provided
        if audit_context:
            context_summary = f"""
Current Audit Context:
- Website: {audit_context.get('website_url', 'N/A')}
- Overall Score: {audit_context.get('overall_score', 'N/A')}/100
- Failed Checks: {audit_context.get('checks_failed', 0)}
- Pages Crawled: {audit_context.get('pages_crawled', 0)}
"""
            system_prompt += f"\n\n{context_summary}"
        
        # Manage conversation context
        messages = self._manage_context(user_message)
        
        # Add system prompt at the start
        full_messages = [{"role": "system", "content": system_prompt}] + messages
        
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=full_messages,
                temperature=0.8,
                max_tokens=1500
            )
            
            assistant_message = response.choices[0].message.content
            
            # Add assistant response to history
            self.conversation_history.append({"role": "assistant", "content": assistant_message})
            
            return assistant_message
            
        except Exception as e:
            logger.error(f"Error in chat: {str(e)}")
            return "I'm having trouble processing your request. Please try rephrasing or ask a different question."
    
    async def research_topic(self, topic: str, use_exa: bool = True) -> str:
        """Research SEO topic using Exa.ai research agent"""
        try:
            if use_exa:
                # Import research agent
                from .research_agent import research_agent
                
                # Delegate to research agent
                logger.info(f"Delegating research to Exa.ai agent for topic: {topic}")
                research_results = await research_agent.research_keyword_trends(topic)
                
                # Combine Exa research with Groq analysis
                exa_insights = f"""
Research Results from Exa.ai:
- Keyword: {research_results.get('keyword')}
- Sources Found: {len(research_results.get('sources', []))}

Top Sources:
"""
                for source in research_results.get('sources', [])[:5]:
                    exa_insights += f"\n- {source.get('title')} ({source.get('url')})"
                
                # Now synthesize with Groq
                prompt = f"""
Based on the latest research data:

{exa_insights}

Provide comprehensive information about: {topic}

Include:
1. Current best practices (2024-2025)
2. Key insights from the research
3. Common mistakes to avoid
4. Implementation steps
5. Tools and resources
6. Expected results/timeline

Be detailed and actionable.
"""
            else:
                # Fallback to direct Groq query
                prompt = f"""
Research and provide comprehensive information about this SEO topic:

Topic: {topic}

Include:
1. Current best practices (2024-2025)
2. Common mistakes to avoid
3. Implementation steps
4. Tools and resources
5. Expected results/timeline

Be detailed and actionable.
"""
            
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an SEO research expert providing up-to-date, comprehensive information based on latest data."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error in research: {str(e)}")
            return "Unable to complete research. Please try again."
    
    async def delegate_to_research_agent(self, task: str, **kwargs) -> Dict[str, Any]:
        """Delegate specialized tasks to the research sub-agent"""
        try:
            from .research_agent import research_agent
            
            logger.info(f"Delegating task to research agent: {task}")
            
            if task == "keyword_trends":
                return await research_agent.research_keyword_trends(kwargs.get('keyword', ''))
            elif task == "competitor_analysis":
                return await research_agent.analyze_competitors(
                    kwargs.get('domain', ''),
                    kwargs.get('keywords', [])
                )
            elif task == "backlink_opportunities":
                return await research_agent.find_backlink_opportunities(
                    kwargs.get('topic', ''),
                    kwargs.get('industry', '')
                )
            elif task == "content_ideas":
                return await research_agent.get_content_ideas(
                    kwargs.get('niche', ''),
                    kwargs.get('keywords', [])
                )
            elif task == "technical_updates":
                return await research_agent.research_technical_seo_updates()
            else:
                return {"error": f"Unknown task: {task}"}
                
        except Exception as e:
            logger.error(f"Error delegating to research agent: {str(e)}")
            return {"error": str(e)}
    
    def reset_conversation(self):
        """Reset conversation history"""
        self.conversation_history = []
        logger.info("Conversation history reset")
