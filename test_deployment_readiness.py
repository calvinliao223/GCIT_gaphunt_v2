#!/usr/bin/env python3
"""
Test deployment readiness for Gap Hunter Bot web interface
Validates that all critical issues have been resolved
"""

import sys
import os
from pathlib import Path

def test_environment_setup():
    """Test that environment variables are properly configured"""
    print("🔧 Testing Environment Setup")
    print("=" * 30)
    
    # Load environment variables
    env_file = Path('AI-gaphunt-v2/.env')
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    value = value.strip('"\'')
                    if key not in os.environ:
                        os.environ[key] = value
        print("✅ Environment variables loaded from .env file")
    else:
        print("⚠️ .env file not found - using system environment variables")
    
    # Check critical API keys
    required_keys = ['S2_API_KEY', 'CORE_API_KEY', 'GOOGLE_API_KEY', 'CONTACT_EMAIL']
    missing_keys = []
    
    for key in required_keys:
        if os.environ.get(key):
            print(f"✅ {key}: Available")
        else:
            print(f"❌ {key}: Missing")
            missing_keys.append(key)
    
    return len(missing_keys) == 0

def test_core_functionality():
    """Test that core Gap Hunter Bot functionality works"""
    print("\n🤖 Testing Core Functionality")
    print("=" * 30)
    
    try:
        # Add paths
        sys.path.insert(0, 'AI-gaphunt-v2')
        
        # Test Gap Hunter Bot import and initialization
        from clean_gap_hunter import GapHunterBot
        print("✅ GapHunterBot imported successfully")
        
        # Test bot initialization
        bot = GapHunterBot()
        print("✅ GapHunterBot initialized successfully")
        
        # Test a simple search (non-interactive)
        results = bot.hunt_gaps("test query")
        print(f"✅ Search functionality works (returned {len(results)} results)")
        
        return True
        
    except Exception as e:
        print(f"❌ Core functionality test failed: {e}")
        return False

def test_web_interface_structure():
    """Test that web interface has required components"""
    print("\n🌐 Testing Web Interface Structure")
    print("=" * 35)
    
    try:
        # Check if web interface file exists
        web_file = Path('web/streamlit_app.py')
        if not web_file.exists():
            print("❌ Web interface file not found")
            return False
        print("✅ Web interface file exists")
        
        # Check for critical functions by reading the file
        with open(web_file, 'r') as f:
            content = f.read()
        
        required_functions = [
            'display_simple_security_status',
            'search_research_gaps',
            'display_results',
            'main'
        ]
        
        missing_functions = []
        for func in required_functions:
            if f"def {func}" in content:
                print(f"✅ Function {func} found")
            else:
                print(f"❌ Function {func} missing")
                missing_functions.append(func)
        
        # Check for proper import handling
        if "LLM_PROVIDERS_AVAILABLE" in content:
            print("✅ Optional LLM provider handling implemented")
        else:
            print("⚠️ LLM provider handling may need attention")
        
        return len(missing_functions) == 0
        
    except Exception as e:
        print(f"❌ Web interface structure test failed: {e}")
        return False

def test_deployment_files():
    """Test that deployment files are properly configured"""
    print("\n📦 Testing Deployment Files")
    print("=" * 25)
    
    deployment_files = {
        'requirements.txt': 'Python dependencies',
        'AI-gaphunt-v2/.env': 'Environment variables',
        'web/.env': 'Web environment variables',
        'Procfile': 'Heroku deployment config',
        'runtime.txt': 'Python runtime version'
    }
    
    all_present = True
    for file_path, description in deployment_files.items():
        if Path(file_path).exists():
            print(f"✅ {description}: {file_path}")
        else:
            print(f"⚠️ {description}: {file_path} (optional)")
            if file_path in ['requirements.txt', 'AI-gaphunt-v2/.env']:
                all_present = False
    
    return all_present

def main():
    """Run all deployment readiness tests"""
    print("🚀 Gap Hunter Bot - Deployment Readiness Test")
    print("=" * 50)
    
    tests = [
        ("Environment Setup", test_environment_setup),
        ("Core Functionality", test_core_functionality),
        ("Web Interface Structure", test_web_interface_structure),
        ("Deployment Files", test_deployment_files)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 15)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 DEPLOYMENT READY!")
        print("✅ All critical issues resolved")
        print("✅ Web interface should deploy successfully")
        print("✅ Core functionality working")
        return True
    else:
        print("\n⚠️ DEPLOYMENT NEEDS ATTENTION")
        print("❌ Some issues need to be resolved")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
