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
    
    def generate(self, messages: List[Dict[str, str]], system_prompt: str = None) -> str:
        """
        Generate completion from messages
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            system_prompt: Optional system prompt to prepend
            
        Returns:
            Generated text response
        """
        try:
            if self.provider in ["groq", "openai", "ollama"]:
                return self._generate_openai_compatible(messages, system_prompt)
            elif self.provider == "anthropic":
                return self._generate_anthropic(messages, system_prompt)
            elif self.provider == "gemini":
                return self._generate_gemini(messages, system_prompt)
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
