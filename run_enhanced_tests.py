#!/usr/bin/env python3
"""
Test runner for enhanced Gap Hunter Bot tests
"""

import sys
import os
import unittest
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'AI-gaphunt-v2'))
sys.path.insert(0, str(project_root / 'tests'))

def run_enhanced_tests():
    """Run the enhanced test suite"""
    print("🧪 Running Enhanced Gap Hunter Bot Tests")
    print("=" * 50)
    
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = str(project_root / 'tests')
    suite = loader.discover(start_dir, pattern='test_gap_hunter_enhanced.py')
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print("🧪 Test Summary")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\n💥 Errors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n✅ All tests passed!")
        return True
    else:
        print("\n❌ Some tests failed!")
        return False

if __name__ == '__main__':
    success = run_enhanced_tests()
    sys.exit(0 if success else 1)
