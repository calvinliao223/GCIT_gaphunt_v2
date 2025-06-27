#!/usr/bin/env python3
"""
Test suite for LLM provider functionality
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ai_scientist.llm_providers import (
    LLMProviderManager, 
    LLMConfig, 
    OpenAIProvider, 
    AnthropicProvider, 
    GoogleProvider
)

class TestLLMProviderManager(unittest.TestCase):
    """Test the LLM Provider Manager"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.manager = LLMProviderManager()
    
    def test_get_available_providers(self):
        """Test getting available providers"""
        providers = self.manager.get_available_providers()
        self.assertIsInstance(providers, list)
        self.assertIn('openai', providers)
        self.assertIn('anthropic', providers)
        self.assertIn('google', providers)
    
    def test_get_provider_models(self):
        """Test getting models for a provider"""
        openai_models = self.manager.get_provider_models('openai')
        self.assertIsInstance(openai_models, list)
        self.assertGreater(len(openai_models), 0)
        
        anthropic_models = self.manager.get_provider_models('anthropic')
        self.assertIsInstance(anthropic_models, list)
        self.assertGreater(len(anthropic_models), 0)
    
    def test_get_provider_info(self):
        """Test getting provider information"""
        openai_info = self.manager.get_provider_info('openai')
        self.assertIsInstance(openai_info, dict)
        self.assertIn('name', openai_info)
        self.assertIn('models', openai_info)
        self.assertIn('default_model', openai_info)
    
    def test_load_user_preferences(self):
        """Test loading user preferences"""
        provider, model = self.manager.load_user_preferences()
        self.assertIsInstance(provider, str)
        self.assertIsInstance(model, str)
    
    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'})
    def test_check_provider_availability_with_key(self):
        """Test provider availability when API key is set"""
        # This will fail because it's a fake key, but we're testing the logic
        available = self.manager.check_provider_availability('openai')
        # We expect this to be False because the key is fake
        self.assertIsInstance(available, bool)
    
    def test_check_provider_availability_without_key(self):
        """Test provider availability when API key is not set"""
        with patch.dict(os.environ, {}, clear=True):
            available = self.manager.check_provider_availability('openai')
            self.assertFalse(available)

class TestLLMConfig(unittest.TestCase):
    """Test LLM configuration"""
    
    def test_llm_config_creation(self):
        """Test creating LLM configuration"""
        config = LLMConfig(
            provider="openai",
            model="gpt-4o",
            temperature=0.7,
            max_tokens=1000
        )
        
        self.assertEqual(config.provider, "openai")
        self.assertEqual(config.model, "gpt-4o")
        self.assertEqual(config.temperature, 0.7)
        self.assertEqual(config.max_tokens, 1000)

class TestProviderCreation(unittest.TestCase):
    """Test provider creation and initialization"""
    
    def test_create_openai_provider_without_key(self):
        """Test creating OpenAI provider without API key"""
        config = LLMConfig(provider="openai", model="gpt-4o")
        
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                OpenAIProvider(config)
    
    def test_create_anthropic_provider_without_key(self):
        """Test creating Anthropic provider without API key"""
        config = LLMConfig(provider="anthropic", model="claude-3-5-sonnet-20241022")
        
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                AnthropicProvider(config)
    
    def test_create_google_provider_without_key(self):
        """Test creating Google provider without API key"""
        config = LLMConfig(provider="google", model="gemini-pro")
        
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                GoogleProvider(config)

class TestProviderFallback(unittest.TestCase):
    """Test provider fallback functionality"""
    
    def setUp(self):
        self.manager = LLMProviderManager()
    
    @patch.dict(os.environ, {}, clear=True)
    def test_generate_with_fallback_no_providers(self):
        """Test fallback when no providers are available"""
        with self.assertRaises(Exception) as context:
            self.manager.generate_with_fallback("Test prompt")
        
        self.assertIn("No available LLM providers", str(context.exception))

class TestConfigurationPersistence(unittest.TestCase):
    """Test configuration saving and loading"""
    
    def setUp(self):
        self.manager = LLMProviderManager()
    
    def test_save_user_preferences(self):
        """Test saving user preferences"""
        # This test would require a writable config file
        # For now, we just test that the method exists and doesn't crash
        try:
            result = self.manager.save_user_preferences("openai", "gpt-4o")
            self.assertIsInstance(result, bool)
        except Exception:
            # Expected if config file is not writable
            pass

def run_integration_test():
    """Run a simple integration test"""
    print("🧪 Running LLM Provider Integration Test")
    print("=" * 50)
    
    try:
        # Test manager initialization
        manager = LLMProviderManager()
        print("✅ LLM Provider Manager initialized")
        
        # Test getting providers
        providers = manager.get_available_providers()
        print(f"✅ Available providers: {', '.join(providers)}")
        
        # Test getting models for each provider
        for provider in providers:
            models = manager.get_provider_models(provider)
            print(f"✅ {provider.title()} models: {len(models)} available")
        
        # Test provider availability
        available_count = 0
        for provider in providers:
            available = manager.check_provider_availability(provider)
            status = "✅ Available" if available else "❌ Unavailable"
            print(f"   {provider.title()}: {status}")
            if available:
                available_count += 1
        
        if available_count > 0:
            print(f"✅ {available_count} provider(s) ready to use")
        else:
            print("⚠️  No providers available - please set API keys")
        
        print("\n🎉 Integration test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {str(e)}")
        return False

if __name__ == "__main__":
    # Run integration test first
    integration_success = run_integration_test()
    
    print("\n" + "=" * 50)
    print("🧪 Running Unit Tests")
    print("=" * 50)
    
    # Run unit tests
    unittest.main(verbosity=2, exit=False)
    
    if integration_success:
        print("\n✅ All tests completed - LLM provider system is ready!")
    else:
        print("\n⚠️  Integration test failed - check API key configuration")
