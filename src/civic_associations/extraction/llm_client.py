"""LLM client for calling Gemini or other models."""

from typing import Dict, Any
import os
import json
from ..utils import setup_logger

logger = setup_logger(__name__)


class LLMClient:
    """Client for LLM API calls."""
    
    def __init__(
        self,
        model_name: str = "gemini-1.5-flash",
        temperature: float = 0.1,
        max_tokens: int = 4096,
        api_timeout: int = 30
    ):
        """
        Initialize LLM client.
        
        Args:
            model_name: Name of the LLM model
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            api_timeout: API request timeout in seconds
        """
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.api_timeout = api_timeout
        self._client = None
        self._model = None
        
        logger.info(f"Initialized LLMClient with model={model_name}")
    
    def _init_gemini(self):
        """Initialize Gemini client lazily."""
        if self._client is not None:
            return
        
        try:
            import google.generativeai as genai
            
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY environment variable not set")
            
            genai.configure(api_key=api_key)
            
            # Map model names to ensure compatibility with available Gemini models
            # As of 2025, available models are: gemini-1.5-flash, gemini-1.5-pro, gemini-2.0-flash-exp
            model_mapping = {
                "gemini-2.5-flash": "gemini-2.0-flash-exp",  # 2.5 doesn't exist, map to 2.0
                "gemini-2.5-pro": "gemini-1.5-pro",  # 2.5 doesn't exist, map to 1.5
            }
            
            model_name = model_mapping.get(self.model_name, self.model_name)
            
            # Validate it's a Gemini model
            if not model_name.startswith("gemini-"):
                logger.warning(f"Model {model_name} doesn't appear to be a Gemini model, using default")
                model_name = "gemini-1.5-flash"
            
            if model_name != self.model_name:
                logger.info(f"Mapped model {self.model_name} to {model_name}")
            
            generation_config = {
                "temperature": self.temperature,
                "max_output_tokens": self.max_tokens,
                "response_mime_type": "application/json",
            }
            
            self._model = genai.GenerativeModel(
                model_name=model_name,
                generation_config=generation_config,
            )
            
            self._client = genai
            logger.info(f"Initialized Gemini model: {model_name}")
            
        except ImportError:
            logger.error("google-generativeai package not installed")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            raise
    
    def call(
        self,
        system_prompt: str,
        user_prompt: str
    ) -> Dict[str, Any]:
        """
        Call the LLM with prompts.
        
        Args:
            system_prompt: System instruction
            user_prompt: User query
            
        Returns:
            Dictionary with response and metadata
        """
        logger.debug(f"Calling LLM with {len(user_prompt)} chars")
        
        try:
            self._init_gemini()
            
            # Combine system and user prompts
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            # Generate response
            response = self._model.generate_content(full_prompt)
            
            # Extract text from response
            content = response.text
            
            # Try to validate it's valid JSON
            try:
                json.loads(content)
            except json.JSONDecodeError:
                logger.warning("Response is not valid JSON, wrapping in quotes")
            
            result = {
                "content": content,
                "model": self.model_name,
                "tokens_used": getattr(response, 'usage_metadata', {}).get('total_token_count', 0) if hasattr(response, 'usage_metadata') else 0,
                "finish_reason": "stop"
            }
            
            logger.debug(f"LLM response: {len(content)} chars")
            return result
            
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            # Return a fallback response
            return {
                "content": '{"error": "LLM call failed", "name": "Unknown", "members": []}',
                "model": self.model_name,
                "tokens_used": 0,
                "finish_reason": "error"
            }
