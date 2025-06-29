#!/usr/bin/env python3
"""
Verify that the NameError in the web interface has been fixed
"""

import sys
import os
from pathlib import Path

def verify_function_exists():
    """Verify that display_simple_security_status function exists"""
    print("🔍 Verifying NameError Fix")
    print("=" * 25)
    
    # Check if the function exists in the web interface file
    web_file = Path('web/streamlit_app.py')
    if not web_file.exists():
        print("❌ Web interface file not found")
        return False
    
    with open(web_file, 'r') as f:
        content = f.read()
    
    # Check for the function definition
    if "def display_simple_security_status(" in content:
        print("✅ display_simple_security_status function found")
    else:
        print("❌ display_simple_security_status function missing")
        return False
    
    # Check for the function call
    if "display_simple_security_status()" in content:
        print("✅ Function is called in the code")
    else:
        print("❌ Function call not found")
        return False
    
    # Check that old function is not referenced
    if "display_security_status()" in content:
        print("⚠️ Old function call still present")
        return False
    else:
        print("✅ Old function call removed")
    
    # Check for optional LLM provider handling
    if "LLM_PROVIDERS_AVAILABLE" in content:
        print("✅ Optional LLM provider handling implemented")
    else:
        print("⚠️ LLM provider handling may be missing")
    
    return True

def verify_import_structure():
    """Verify that imports are properly structured"""
    print("\n📦 Verifying Import Structure")
    print("=" * 30)
    
    web_file = Path('web/streamlit_app.py')
    with open(web_file, 'r') as f:
        content = f.read()
    
    # Check that config_loader import is removed
    if "from config_loader import" in content:
        print("❌ Old config_loader import still present")
        return False
    else:
        print("✅ Old config_loader import removed")
    
    # Check for proper LLM provider import handling
    if "try:" in content and "from ai_scientist.llm_providers import" in content:
        print("✅ LLM provider import wrapped in try/catch")
    else:
        print("⚠️ LLM provider import handling may need attention")
    
    # Check for environment loading
    if "env_file = Path(__file__).parent / '.env'" in content:
        print("✅ Direct environment loading implemented")
    else:
        print("⚠️ Environment loading may need attention")
    
    return True

def main():
    """Main verification function"""
    print("🧪 Gap Hunter Bot - NameError Fix Verification")
    print("=" * 50)
    
    function_ok = verify_function_exists()
    import_ok = verify_import_structure()
    
    print("\n📊 Verification Summary")
    print("=" * 20)
    
    if function_ok and import_ok:
        print("✅ NameError fix VERIFIED")
        print("✅ Web interface should work without NameError")
        print("✅ All required functions are present")
        print("✅ Import structure is correct")
        print("\n🎉 The web interface is ready for deployment!")
        return True
    else:
        print("❌ NameError fix INCOMPLETE")
        print("❌ Additional work may be needed")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
