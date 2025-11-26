#!/usr/bin/env python3
"""
Check package versions for compatibility
"""
import pkg_resources

print("🔍 CHECKING PACKAGE VERSIONS")
print("=" * 50)

packages = ['sqlalchemy', 'psycopg2-binary', 'psycopg2']

for package in packages:
    try:
        version = pkg_resources.get_distribution(package).version
        print(f"✅ {package}: {version}")
    except pkg_resources.DistributionNotFound:
        print(f"❌ {package}: NOT INSTALLED")