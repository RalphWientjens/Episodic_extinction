#!/usr/bin/env python3
"""
Test script to verify the experiment structure without running the full experiment.
This checks that all classes can be imported and instantiated.
"""

import sys
import os

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        from trial import ExtinctionTrial
        print("✓ trial.py imports successfully")
    except ImportError as e:
        print(f"✗ Failed to import trial.py: {e}")
        return False
    
    try:
        from session import ExtinctionSession
        print("✓ session.py imports successfully")
    except ImportError as e:
        print(f"✗ Failed to import session.py: {e}")
        return False
    
    try:
        import main
        print("✓ main.py imports successfully")
    except ImportError as e:
        print(f"✗ Failed to import main.py: {e}")
        return False
    
    return True

def test_structure():
    """Test that the basic experiment structure is valid."""
    print("\nTesting experiment structure...")
    
    # Check required files exist
    required_files = [
        'trial.py',
        'session.py', 
        'main.py',
        'requirements.txt',
        'settings.json',
        'README.md'
    ]
    
    all_exist = True
    for filename in required_files:
        if os.path.exists(filename):
            print(f"✓ {filename} exists")
        else:
            print(f"✗ {filename} missing")
            all_exist = False
    
    return all_exist

def test_settings():
    """Test that settings.json is valid JSON."""
    print("\nTesting settings file...")
    
    try:
        import json
        with open('settings.json', 'r') as f:
            settings = json.load(f)
        print(f"✓ settings.json is valid JSON with {len(settings)} sections")
        return True
    except Exception as e:
        print(f"✗ settings.json error: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Episodic Extinction Experiment - Structure Test")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("File structure", test_structure()))
    results.append(("Settings file", test_settings()))
    results.append(("Python imports", test_imports()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary:")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results:
        status = "PASS" if passed else "FAIL"
        symbol = "✓" if passed else "✗"
        print(f"{symbol} {test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n✓ All tests passed! Experiment structure is ready.")
        print("\nNote: exptools2 must be installed to run the actual experiment:")
        print("  pip install -r requirements.txt")
        return 0
    else:
        print("\n✗ Some tests failed. Please check the errors above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
