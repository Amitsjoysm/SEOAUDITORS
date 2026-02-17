"""AI Orchestrator for SEO Analysis with Multi-LLM Support"""
import os
from typing import List, Dict, Any, Optional
import logging
import asyncio
from functools import wraps
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models import LLMSetting, EnvironmentKey
from seo_engine.multi_llm_client import MultiLLMClient
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

# Fallback configuration
DEFAULT_PROVIDER = "groq"
DEFAULT_MODEL = "llama-3.3-70b-versatile"
DEFAULT_API_KEY = os.getenv("GROQ_API_KEY", "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")
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


class SEOOrchestratorV2:
    """Orchestrator agent for SEO analysis with multi-LLM support"""
    
    def __init__(self, db_session: AsyncSession = None):
        self.db_session = db_session
        self.client = None
        self.conversation_history: List[Dict[str, str]] = []
        self.max_context_length = 8000  # tokens
        self._initialized = False
    
    async def _initialize_client(self):
        """Initialize LLM client from database settings"""
        if self._initialized and self.client:
            return
        
        try:
            if self.db_session:
                # Fetch active LLM setting from database
                result = await self.db_session.execute(
                    select(LLMSetting).where(LLMSetting.is_active == True)
                )
                llm_setting = result.scalar_one_or_none()
                
                if llm_setting:
                    # Get API key from environment or environment keys table
                    api_key = None
                    if llm_setting.api_key_ref:
                        api_key = await self._get_api_key(llm_setting.api_key_ref)
                    
                    if not api_key:
                        # Fallback to environment variable
                        api_key = os.getenv(llm_setting.api_key_ref or f"{llm_setting.provider.upper()}_API_KEY")
                    
                    # Initialize multi-LLM client
                    self.client = MultiLLMClient(
                        provider=llm_setting.provider.value,
                        model=llm_setting.model_name,
                        api_key=api_key,
                        base_url=llm_setting.base_url,
                        temperature=llm_setting.temperature,
                        max_tokens=llm_setting.max_tokens,
                        top_p=llm_setting.top_p
                    )
                    logger.info(f"Initialized LLM client: {llm_setting.provider.value} - {llm_setting.model_name}")
                    self._initialized = True
                    return
        except Exception as e:
            logger.warning(f"Could not load LLM settings from database: {str(e)}")
        
        # Fallback to default Groq configuration
        logger.info("Using fallback Groq configuration")
        self.client = MultiLLMClient(
            provider=DEFAULT_PROVIDER,
            model=DEFAULT_MODEL,
            api_key=DEFAULT_API_KEY
        )
        self._initialized = True
    
    async def _get_api_key(self, key_name: str) -> Optional[str]:
        """Get API key from environment keys table"""
        try:
            result = await self.db_session.execute(
                select(EnvironmentKey).where(EnvironmentKey.key_name == key_name)
            )
            env_key = result.scalar_one_or_none()
            
            if env_key and env_key.is_active:
                # Decrypt the key value
                secret_key = os.getenv("SECRET_KEY", "default-secret-key-change-in-production").encode()
                cipher = Fernet(secret_key[:32].ljust(32, b'='))
                decrypted = cipher.decrypt(env_key.key_value.encode()).decode()
                return decrypted
        except Exception as e:
            logger.error(f"Error fetching API key {key_name}: {str(e)}")
        
        return None
    
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
        await self._initialize_client()
        
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
            messages = [{"role": "user", "content": prompt}]
            system_prompt = "You are an expert SEO consultant providing actionable insights."
            
            analysis = await asyncio.to_thread(
                self.client.generate,
                messages,
                system_prompt
            )
            
            logger.info("Successfully generated AI analysis")
            return analysis
            
        except Exception as e:
            logger.error(f"Error in AI analysis: {str(e)}")
            return "Unable to generate AI analysis. Please review the detailed check results."
    
    @retry_on_failure(max_retries=3, delay=2)
    async def chat(self, user_message: str, audit_context: Optional[Dict[str, Any]] = None) -> str:
        """Interactive chat about SEO audit results"""
        await self._initialize_client()
        
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
        
        try:
            response_text = await asyncio.to_thread(
                self.client.generate,
                messages,
                system_prompt
            )
            
            # Add assistant response to history
            self.conversation_history.append({"role": "assistant", "content": response_text})
            
            return response_text
            
        except Exception as e:
            logger.error(f"Error in chat: {str(e)}")
            return "I apologize, but I'm having trouble processing your request. Please try again."
    
    @retry_on_failure(max_retries=2, delay=1)
    async def research_topic(self, topic: str) -> str:
        """Research SEO topics using Exa.ai"""
        await self._initialize_client()
        
        # This would integrate with Exa.ai for research
        # For now, use the LLM to provide insights
        prompt = f"""
As an SEO expert, provide comprehensive insights about: {topic}

Include:
1. Current best practices
2. Latest trends and algorithm updates
3. Common mistakes to avoid
4. Recommended strategies
5. Tools and resources

Be specific and up-to-date.
"""
        
        try:
            messages = [{"role": "user", "content": prompt}]
            system_prompt = "You are an SEO research expert with deep knowledge of current trends and best practices."
            
            response = await asyncio.to_thread(
                self.client.generate,
                messages,
                system_prompt
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error in research: {str(e)}")
            return "Unable to complete research. Please try again."
