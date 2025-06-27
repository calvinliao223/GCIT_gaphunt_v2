#!/usr/bin/env python3
"""
LLM Provider Management System
Unified interface for multiple LLM providers (OpenAI, Anthropic, Google Gemini)
"""

import os
import yaml
import time
import logging
from typing import Dict, Any, Optional, List, Tuple
from abc import ABC, abstractmethod
from dataclasses import dataclass
import openai
import anthropic
try:
    import google.generativeai as genai
except ImportError:
    genai = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class LLMConfig:
    """Configuration for LLM providers"""
    provider: str
    model: str
    temperature: float = 0.7
    max_tokens: int = 4000
    api_key: Optional[str] = None

class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.client = None
        self._initialize_client()
    
    @abstractmethod
    def _initialize_client(self):
        """Initialize the provider-specific client"""
        pass
    
    @abstractmethod
    def generate_response(self, prompt: str, system_message: str = "", **kwargs) -> str:
        """Generate a response from the LLM"""
        pass

    def generate_response_with_fallback(self, prompt: str, system_message: str = "", max_retries: int = 3, **kwargs) -> str:
        """Generate response with retry logic and error handling"""
        last_error = None

        for attempt in range(max_retries):
            try:
                return self.generate_response(prompt, system_message, **kwargs)
            except Exception as e:
                last_error = e
                logger.warning(f"Attempt {attempt + 1} failed for {self.config.provider}: {str(e)}")

                # Handle rate limiting with exponential backoff
                if "rate" in str(e).lower() or "quota" in str(e).lower():
                    wait_time = (2 ** attempt) * 1  # 1, 2, 4 seconds
                    logger.info(f"Rate limited, waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue

                # For other errors, wait briefly before retry
                if attempt < max_retries - 1:
                    time.sleep(1)

        # If all retries failed, raise the last error
        raise last_error
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available (API key set, etc.)"""
        pass

class OpenAIProvider(BaseLLMProvider):
    """OpenAI provider implementation"""
    
    def _initialize_client(self):
        api_key = self.config.api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key not found")
        self.client = openai.OpenAI(api_key=api_key)
    
    def generate_response(self, prompt: str, system_message: str = "", **kwargs) -> str:
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            **kwargs
        )
        return response.choices[0].message.content
    
    def is_available(self) -> bool:
        return bool(self.config.api_key or os.getenv("OPENAI_API_KEY"))

class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude provider implementation"""
    
    def _initialize_client(self):
        api_key = self.config.api_key or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("Anthropic API key not found")
        self.client = anthropic.Anthropic(api_key=api_key)
    
    def generate_response(self, prompt: str, system_message: str = "", **kwargs) -> str:
        messages = [{"role": "user", "content": prompt}]
        
        response = self.client.messages.create(
            model=self.config.model,
            messages=messages,
            system=system_message if system_message else None,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            **kwargs
        )
        return response.content[0].text
    
    def is_available(self) -> bool:
        return bool(self.config.api_key or os.getenv("ANTHROPIC_API_KEY"))

class GoogleProvider(BaseLLMProvider):
    """Google Gemini provider implementation"""
    
    def _initialize_client(self):
        if genai is None:
            raise ImportError("google-generativeai package not installed")
        
        api_key = self.config.api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("Google/Gemini API key not found")
        
        genai.configure(api_key=api_key)
        self.client = genai.GenerativeModel(self.config.model)
    
    def generate_response(self, prompt: str, system_message: str = "", **kwargs) -> str:
        full_prompt = f"{system_message}\n\n{prompt}" if system_message else prompt
        
        generation_config = genai.types.GenerationConfig(
            temperature=self.config.temperature,
            max_output_tokens=self.config.max_tokens,
        )
        
        response = self.client.generate_content(
            full_prompt,
            generation_config=generation_config,
            **kwargs
        )
        return response.text
    
    def is_available(self) -> bool:
        return bool(
            genai is not None and 
            (self.config.api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))
        )

class LLMProviderManager:
    """Manager for LLM providers with configuration loading and provider selection"""
    
    def __init__(self, config_path: str = "config/bfts_config.yaml"):
        self.config_path = config_path
        self.providers_config = {}
        self.current_provider = None
        self.load_config()
    
    def load_config(self):
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
                self.providers_config = config.get('llm_providers', {})
        except FileNotFoundError:
            # Use default configuration if file not found
            self.providers_config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default provider configuration"""
        return {
            'default_provider': 'openai',
            'providers': {
                'openai': {
                    'name': 'OpenAI',
                    'models': ['gpt-4o', 'gpt-4o-mini', 'gpt-3.5-turbo'],
                    'default_model': 'gpt-4o',
                    'api_key_env': 'OPENAI_API_KEY'
                },
                'anthropic': {
                    'name': 'Anthropic Claude',
                    'models': ['claude-3-5-sonnet-20241022', 'claude-3-haiku-20240307'],
                    'default_model': 'claude-3-5-sonnet-20241022',
                    'api_key_env': 'ANTHROPIC_API_KEY'
                },
                'google': {
                    'name': 'Google Gemini',
                    'models': ['gemini-pro', 'gemini-pro-vision'],
                    'default_model': 'gemini-pro',
                    'api_key_env': 'GEMINI_API_KEY'
                }
            }
        }
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers"""
        return list(self.providers_config.get('providers', {}).keys())
    
    def get_provider_models(self, provider: str) -> List[str]:
        """Get available models for a provider"""
        provider_config = self.providers_config.get('providers', {}).get(provider, {})
        return provider_config.get('models', [])
    
    def get_provider_info(self, provider: str) -> Dict[str, Any]:
        """Get provider information"""
        return self.providers_config.get('providers', {}).get(provider, {})
    
    def create_provider(self, provider: str, model: str = None, **kwargs) -> BaseLLMProvider:
        """Create a provider instance"""
        provider_info = self.get_provider_info(provider)
        if not provider_info:
            raise ValueError(f"Provider {provider} not found in configuration")
        
        model = model or provider_info.get('default_model')
        if not model:
            raise ValueError(f"No model specified for provider {provider}")
        
        config = LLMConfig(
            provider=provider,
            model=model,
            **kwargs
        )
        
        if provider == 'openai':
            return OpenAIProvider(config)
        elif provider == 'anthropic':
            return AnthropicProvider(config)
        elif provider == 'google':
            return GoogleProvider(config)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def set_current_provider(self, provider: str, model: str = None, **kwargs):
        """Set the current active provider"""
        self.current_provider = self.create_provider(provider, model, **kwargs)
        return self.current_provider
    
    def get_current_provider(self) -> Optional[BaseLLMProvider]:
        """Get the current active provider"""
        if self.current_provider is None:
            # Initialize with default provider
            default_provider = self.providers_config.get('default_provider', 'openai')
            try:
                self.set_current_provider(default_provider)
            except Exception:
                # If default provider fails, try others
                for provider in self.get_available_providers():
                    try:
                        self.set_current_provider(provider)
                        break
                    except Exception:
                        continue
        
        return self.current_provider
    
    def check_provider_availability(self, provider: str) -> bool:
        """Check if a provider is available"""
        try:
            provider_instance = self.create_provider(provider)
            return provider_instance.is_available()
        except Exception:
            return False

    def save_user_preferences(self, provider: str, model: str):
        """Save user preferences to configuration file"""
        try:
            # Load current config
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)

            # Update provider preferences
            if 'llm_providers' not in config:
                config['llm_providers'] = self._get_default_config()

            config['llm_providers']['default_provider'] = provider

            # Update default model for the provider
            if 'providers' in config['llm_providers'] and provider in config['llm_providers']['providers']:
                config['llm_providers']['providers'][provider]['default_model'] = model

            # Save updated config
            with open(self.config_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, indent=2)

            # Update internal config
            self.providers_config = config.get('llm_providers', {})

            return True
        except Exception as e:
            print(f"Error saving preferences: {e}")
            return False

    def load_user_preferences(self) -> Tuple[str, str]:
        """Load user preferences from configuration"""
        default_provider = self.providers_config.get('default_provider', 'openai')
        provider_info = self.get_provider_info(default_provider)
        default_model = provider_info.get('default_model', '')
        return default_provider, default_model

    def generate_with_fallback(self, prompt: str, system_message: str = "", preferred_provider: str = None, **kwargs) -> Tuple[str, str]:
        """Generate response with automatic fallback to other providers if the preferred one fails"""
        providers_to_try = []

        # Start with preferred provider if specified
        if preferred_provider and preferred_provider in self.get_available_providers():
            providers_to_try.append(preferred_provider)

        # Add other available providers as fallbacks
        for provider in self.get_available_providers():
            if provider not in providers_to_try and self.check_provider_availability(provider):
                providers_to_try.append(provider)

        last_error = None
        for provider in providers_to_try:
            try:
                logger.info(f"Trying provider: {provider}")
                provider_instance = self.create_provider(provider)
                response = provider_instance.generate_response_with_fallback(prompt, system_message, **kwargs)
                return response, provider
            except Exception as e:
                last_error = e
                logger.warning(f"Provider {provider} failed: {str(e)}")
                continue

        # If all providers failed
        if last_error:
            raise Exception(f"All LLM providers failed. Last error: {str(last_error)}")
        else:
            raise Exception("No available LLM providers found")

# Global instance for easy access
llm_manager = LLMProviderManager()
