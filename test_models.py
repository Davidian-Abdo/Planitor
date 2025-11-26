#!/usr/bin/env python3
"""
Test that all models can be imported without syntax errors
"""
import sys
import os

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_model_imports():
    """Test that all models can be imported"""
    try:
        print("🔍 TESTING MODEL IMPORTS")
        print("=" * 40)
        
        # Test database models
        from backend.models import db_models
        print("✅ Database models imported successfully")
        
        # Test domain models  
        from backend.models import domain_models
        print("✅ Domain models imported successfully")
        
        print("\n🎉 All models imported without syntax errors!")
        return True
        
    except SyntaxError as e:
        print(f"❌ Syntax error in models: {e}")
        return False
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

if __name__ == "__main__":
    if test_model_imports():
        print("\n🚀 Ready to initialize database!")
    else:
        print("\n💥 Fix model syntax errors first")