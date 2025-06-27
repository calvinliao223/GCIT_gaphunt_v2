#!/usr/bin/env python3
"""
Secure configuration loader for Gap Hunter Bot
Handles both local development (.env) and production (environment variables)
"""

import os
from pathlib import Path
import streamlit as st

def load_env_file_safely():
    """
    Load environment variables from .env file for local development only.
    In production, this file won't exist and environment variables will be used directly.
    """
    env_file = Path(__file__).parent.parent / ".env"
    
    # Only load .env file if it exists (local development)
    if env_file.exists():
        print("🔧 Loading local .env file for development")
        with open(env_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    # Remove quotes if present
                    value = value.strip('"\'')
                    # Only set if not already in environment (production takes precedence)
                    if key not in os.environ:
                        os.environ[key] = value
        return True
    else:
        print("🌐 Using production environment variables")
        return False

def get_api_key(key_name, required=True):
    """
    Safely get API key from multiple sources (DevOps-friendly).

    Priority order:
    1. Docker secrets (files in /run/secrets/)
    2. Kubernetes secrets (files in /var/secrets/)
    3. Environment variables
    4. Vault (if configured)

    Args:
        key_name (str): Name of the environment variable
        required (bool): Whether this key is required for the app to function

    Returns:
        str: API key value or None if not found and not required
    """
    value = None
    source = "unknown"

    # 1. Try Docker secrets
    docker_secret_file = f"/run/secrets/{key_name.lower()}"
    if os.path.exists(docker_secret_file):
        try:
            with open(docker_secret_file, 'r') as f:
                value = f.read().strip()
                source = "Docker secrets"
        except Exception as e:
            print(f"⚠️ Error reading Docker secret {docker_secret_file}: {e}")

    # 2. Try Kubernetes secrets
    if not value:
        k8s_secret_file = f"/var/secrets/{key_name.lower()}"
        if os.path.exists(k8s_secret_file):
            try:
                with open(k8s_secret_file, 'r') as f:
                    value = f.read().strip()
                    source = "Kubernetes secrets"
            except Exception as e:
                print(f"⚠️ Error reading K8s secret {k8s_secret_file}: {e}")

    # 3. Try environment variable with _FILE suffix (points to secret file)
    if not value:
        file_env_var = f"{key_name}_FILE"
        secret_file_path = os.getenv(file_env_var)
        if secret_file_path and os.path.exists(secret_file_path):
            try:
                with open(secret_file_path, 'r') as f:
                    value = f.read().strip()
                    source = f"Secret file ({file_env_var})"
            except Exception as e:
                print(f"⚠️ Error reading secret file {secret_file_path}: {e}")

    # 4. Try regular environment variable
    if not value:
        value = os.getenv(key_name)
        if value:
            source = "Environment variable"

    # 5. Try HashiCorp Vault (if available)
    if not value:
        try:
            from vault.vault_config import VaultSecretManager
            vault = VaultSecretManager()
            if vault.client:
                # Map environment variable names to Vault paths
                vault_mappings = {
                    'OPENAI_API_KEY': ('gaphunter/llm-providers', 'openai_key'),
                    'ANTHROPIC_API_KEY': ('gaphunter/llm-providers', 'anthropic_key'),
                    'GEMINI_API_KEY': ('gaphunter/llm-providers', 'gemini_key'),
                }
                if key_name in vault_mappings:
                    path, key = vault_mappings[key_name]
                    value = vault.get_secret(path, key)
                    if value:
                        source = "HashiCorp Vault"
        except ImportError:
            pass  # Vault not available
        except Exception as e:
            print(f"⚠️ Vault error for {key_name}: {e}")

    if value:
        print(f"✅ {key_name}: Loaded from {source}")
    elif required:
        if hasattr(st, 'error'):  # If running in Streamlit context
            st.error(f"❌ Missing required API key: {key_name}")
            st.info("Please set this in your deployment platform's secret management")
        else:
            print(f"❌ Missing required API key: {key_name}")
        return None

    return value

def validate_api_keys():
    """
    Validate that all required API keys are available.
    
    Returns:
        dict: Status of each API key
    """
    # Core required keys for basic functionality
    core_keys = {
        "GOOGLE_API_KEY": "Google API (for research databases)",
        "S2_API_KEY": "Semantic Scholar API", 
        "CORE_API_KEY": "CORE API"
    }
    
    # LLM provider keys (at least one required)
    llm_keys = {
        "OPENAI_API_KEY": "OpenAI",
        "ANTHROPIC_API_KEY": "Anthropic Claude",
        "GEMINI_API_KEY": "Google Gemini"
    }
    
    status = {
        "core_keys": {},
        "llm_keys": {},
        "all_core_available": True,
        "llm_providers_available": 0
    }
    
    # Check core keys
    for key, description in core_keys.items():
        available = bool(get_api_key(key, required=False))
        status["core_keys"][key] = {
            "available": available,
            "description": description
        }
        if not available:
            status["all_core_available"] = False
    
    # Check LLM provider keys
    for key, description in llm_keys.items():
        available = bool(get_api_key(key, required=False))
        status["llm_keys"][key] = {
            "available": available,
            "description": description
        }
        if available:
            status["llm_providers_available"] += 1
    
    return status

def get_secure_config():
    """
    Get secure configuration for the application.
    
    Returns:
        dict: Configuration with masked API keys for logging
    """
    config = {
        "api_keys": {},
        "contact_email": get_api_key("CONTACT_EMAIL", required=False) or "contact@example.com"
    }
    
    # Get all API keys
    api_keys = [
        "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY",
        "GOOGLE_API_KEY", "S2_API_KEY", "CORE_API_KEY"
    ]
    
    for key in api_keys:
        value = get_api_key(key, required=False)
        if value:
            # Store full value for use
            config["api_keys"][key] = value
            # Create masked version for logging
            masked = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
            print(f"✅ {key}: {masked}")
        else:
            print(f"❌ {key}: Not set")
    
    return config

def display_security_status():
    """Display security status in Streamlit interface"""
    if not hasattr(st, 'sidebar'):
        return
    
    with st.sidebar.expander("🔐 Security Status"):
        status = validate_api_keys()
        
        st.write("**Core APIs:**")
        for key, info in status["core_keys"].items():
            icon = "✅" if info["available"] else "❌"
            st.write(f"{icon} {info['description']}")
        
        st.write("**LLM Providers:**")
        for key, info in status["llm_keys"].items():
            icon = "✅" if info["available"] else "❌"
            st.write(f"{icon} {info['description']}")
        
        if status["all_core_available"] and status["llm_providers_available"] > 0:
            st.success(f"🔐 Secure: {status['llm_providers_available']} LLM provider(s) available")
        else:
            st.warning("⚠️ Some API keys missing")

# Initialize configuration on import
load_env_file_safely()
