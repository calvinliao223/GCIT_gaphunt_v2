#!/usr/bin/env python3
"""
HashiCorp Vault integration for Gap Hunter Bot
Securely retrieve API keys from Vault
"""

import os
import hvac
import logging
from typing import Dict, Optional

class VaultSecretManager:
    """Manage secrets using HashiCorp Vault"""
    
    def __init__(self, vault_url: str = None, vault_token: str = None):
        self.vault_url = vault_url or os.getenv('VAULT_ADDR', 'http://localhost:8200')
        self.vault_token = vault_token or os.getenv('VAULT_TOKEN')
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Vault client"""
        try:
            self.client = hvac.Client(url=self.vault_url, token=self.vault_token)
            
            # Verify authentication
            if not self.client.is_authenticated():
                raise Exception("Vault authentication failed")
                
            logging.info("✅ Connected to HashiCorp Vault")
            
        except Exception as e:
            logging.error(f"❌ Vault connection failed: {e}")
            self.client = None
    
    def get_secret(self, path: str, key: str) -> Optional[str]:
        """Get a specific secret from Vault"""
        if not self.client:
            return None
            
        try:
            response = self.client.secrets.kv.v2.read_secret_version(path=path)
            secrets = response['data']['data']
            return secrets.get(key)
            
        except Exception as e:
            logging.error(f"❌ Failed to retrieve secret {key} from {path}: {e}")
            return None
    
    def get_all_api_keys(self) -> Dict[str, str]:
        """Get all API keys for Gap Hunter Bot"""
        api_keys = {}
        
        # Define secret paths and keys
        secret_mappings = {
            'OPENAI_API_KEY': ('gaphunter/llm-providers', 'openai_key'),
            'ANTHROPIC_API_KEY': ('gaphunter/llm-providers', 'anthropic_key'),
            'GEMINI_API_KEY': ('gaphunter/llm-providers', 'gemini_key'),
            'GOOGLE_API_KEY': ('gaphunter/research-apis', 'google_key'),
            'S2_API_KEY': ('gaphunter/research-apis', 's2_key'),
            'CORE_API_KEY': ('gaphunter/research-apis', 'core_key'),
            'CONTACT_EMAIL': ('gaphunter/config', 'contact_email')
        }
        
        for env_var, (path, key) in secret_mappings.items():
            secret_value = self.get_secret(path, key)
            if secret_value:
                api_keys[env_var] = secret_value
                # Set environment variable for the application
                os.environ[env_var] = secret_value
                logging.info(f"✅ Retrieved {env_var} from Vault")
            else:
                logging.warning(f"⚠️ Could not retrieve {env_var} from Vault")
        
        return api_keys
    
    def store_secret(self, path: str, secrets: Dict[str, str]):
        """Store secrets in Vault (for initial setup)"""
        if not self.client:
            raise Exception("Vault client not initialized")
        
        try:
            self.client.secrets.kv.v2.create_or_update_secret(
                path=path,
                secret=secrets
            )
            logging.info(f"✅ Stored secrets at {path}")
            
        except Exception as e:
            logging.error(f"❌ Failed to store secrets at {path}: {e}")
            raise

def setup_vault_secrets():
    """Initial setup of secrets in Vault"""
    vault = VaultSecretManager()
    
    # LLM Provider secrets
    llm_secrets = {
        'openai_key': input("Enter OpenAI API Key: "),
        'anthropic_key': input("Enter Anthropic API Key: "),
        'gemini_key': input("Enter Gemini API Key: ")
    }
    vault.store_secret('gaphunter/llm-providers', llm_secrets)
    
    # Research API secrets
    research_secrets = {
        'google_key': input("Enter Google API Key: "),
        's2_key': input("Enter Semantic Scholar API Key: "),
        'core_key': input("Enter CORE API Key: ")
    }
    vault.store_secret('gaphunter/research-apis', research_secrets)
    
    # Configuration
    config_secrets = {
        'contact_email': input("Enter Contact Email: ")
    }
    vault.store_secret('gaphunter/config', config_secrets)
    
    print("✅ All secrets stored in Vault")

def load_secrets_from_vault():
    """Load secrets from Vault into environment variables"""
    vault = VaultSecretManager()
    api_keys = vault.get_all_api_keys()
    
    if api_keys:
        print(f"✅ Loaded {len(api_keys)} API keys from Vault")
        return True
    else:
        print("❌ Failed to load API keys from Vault")
        return False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        setup_vault_secrets()
    else:
        load_secrets_from_vault()
