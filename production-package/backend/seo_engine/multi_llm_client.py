"""Multi-LLM Client supporting Groq, OpenAI, Anthropic, Gemini, and Ollama"""
import os
import logging
from typing import List, Dict, Any, Optional
from groq import Groq
from openai import OpenAI
try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None
try:
    import google.generativeai as genai
except ImportError:
    genai = None

logger = logging.getLogger(__name__)


class MultiLLMClient:
    """Unified client for multiple LLM providers"""
    
    def __init__(self, provider: str, model: str, api_key: str = None, 
                 base_url: str = None, temperature: float = 0.7, 
                 max_tokens: int = 4096, top_p: float = 1.0):
        """
        Initialize multi-LLM client
        
        Args:
            provider: One of 'groq', 'openai', 'anthropic', 'gemini', 'ollama'
            model: Model name/ID for the provider
            api_key: API key (optional, can use from env)
            base_url: Base URL (for Ollama or custom endpoints)
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            top_p: Nucleus sampling parameter
        """
        self.provider = provider.lower()
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.base_url = base_url
        
        # Initialize the appropriate client
        if self.provider == "groq":
            self.client = Groq(api_key=api_key or os.getenv("GROQ_API_KEY"))
        elif self.provider == "openai":
            self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        elif self.provider == "anthropic":
            if Anthropic is None:
                raise ImportError("anthropic package not installed")
            self.client = Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
        elif self.provider == "gemini":
            if genai is None:
                raise ImportError("google-generativeai package not installed")
            genai.configure(api_key=api_key or os.getenv("GEMINI_API_KEY"))
            self.client = genai.GenerativeModel(model)
        elif self.provider == "ollama":
            self.client = OpenAI(
                api_key="ollama",  # Ollama doesn't need a real key
                base_url=base_url or "http://localhost:11434/v1"
            )
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def generate(self, prompt_or_messages, system_prompt: str = None, max_tokens: int = None) -> str:
        """
        Generate completion from prompt or messages
        
        Args:
            prompt_or_messages: Either a string prompt OR list of message dicts with 'role' and 'content'
            system_prompt: Optional system prompt to prepend
            max_tokens: Override max_tokens for this call
            
        Returns:
            Generated text response
        """
        try:
            # Convert string prompt to messages format
            if isinstance(prompt_or_messages, str):
                messages = [{"role": "user", "content": prompt_or_messages}]
            else:
                messages = prompt_or_messages
            
            # Use provided max_tokens or default
            original_max_tokens = self.max_tokens
            if max_tokens:
                self.max_tokens = max_tokens
            
            # Generate
            if self.provider in ["groq", "openai", "ollama"]:
                result = self._generate_openai_compatible(messages, system_prompt)
            elif self.provider == "anthropic":
                result = self._generate_anthropic(messages, system_prompt)
            elif self.provider == "gemini":
                result = self._generate_gemini(messages, system_prompt)
            
            # Restore original max_tokens
            self.max_tokens = original_max_tokens
            
            return result
        except Exception as e:
            logger.error(f"Error generating with {self.provider}: {str(e)}")
            raise
    
    def _generate_openai_compatible(self, messages: List[Dict[str, str]], 
                                   system_prompt: str = None) -> str:
        """Generate using OpenAI-compatible API (Groq, OpenAI, Ollama)"""
        # Prepare messages
        formatted_messages = []
        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})
        formatted_messages.extend(messages)
        
        # Make API call
        response = self.client.chat.completions.create(
            model=self.model,
            messages=formatted_messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            top_p=self.top_p
        )
        
        return response.choices[0].message.content
    
    def _generate_anthropic(self, messages: List[Dict[str, str]], 
                           system_prompt: str = None) -> str:
        """Generate using Anthropic API"""
        # Anthropic uses system parameter separately
        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            top_p=self.top_p,
            system=system_prompt or "",
            messages=messages
        )
        
        return response.content[0].text
    
    def _generate_gemini(self, messages: List[Dict[str, str]], 
                        system_prompt: str = None) -> str:
        """Generate using Google Gemini API"""
        # Gemini uses a different message format
        # Combine system prompt and messages into a single prompt
        prompt_parts = []
        if system_prompt:
            prompt_parts.append(f"System: {system_prompt}\n")
        
        for msg in messages:
            role = "User" if msg["role"] == "user" else "Assistant"
            prompt_parts.append(f"{role}: {msg['content']}\n")
        
        prompt = "\n".join(prompt_parts)
        
        # Generate response
        response = self.client.generate_content(
            prompt,
            generation_config={
                "temperature": self.temperature,
                "max_output_tokens": self.max_tokens,
                "top_p": self.top_p
            }
        )
        
        return response.text
    
    def __str__(self):
        return f"MultiLLMClient(provider={self.provider}, model={self.model})"


async def get_active_llm_client(db):
    """
    Get the active LLM client from database settings
    Returns MultiLLMClient instance configured with active LLM
    """
    from sqlalchemy import select
    from models import LLMSetting
    import os
    
    try:
        # Get active LLM setting from database
        result = await db.execute(
            select(LLMSetting).where(LLMSetting.is_active == True)
        )
        llm_setting = result.scalar_one_or_none()
        
        if llm_setting:
            # Get API key from environment (referenced by api_key_ref)
            api_key = os.getenv(llm_setting.api_key_ref) if llm_setting.api_key_ref else None
            
            client = MultiLLMClient(
                provider=llm_setting.provider.value,
                model=llm_setting.model_name,
                api_key=api_key,
                base_url=llm_setting.base_url,
                temperature=llm_setting.temperature,
                max_tokens=llm_setting.max_tokens,
                top_p=llm_setting.top_p
            )
            
            logger.info(f"Using LLM: {llm_setting.provider.value} - {llm_setting.model_name}")
            return client
        
        else:
            # Fallback to default Groq
            logger.warning("No active LLM setting found, using default Groq")
            return MultiLLMClient(
                provider="groq",
                model="llama-3.3-70b-versatile",
                api_key=os.getenv("GROQ_API_KEY"),
                temperature=0.7,
                max_tokens=4096
            )
    
    except Exception as e:
        logger.error(f"Error getting active LLM: {e}")
        # Fallback to default
        return MultiLLMClient(
            provider="groq",
            model="llama-3.3-70b-versatile",
            api_key=os.getenv("GROQ_API_KEY"),
            temperature=0.7,
            max_tokens=4096
        )

