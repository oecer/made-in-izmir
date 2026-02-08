#!/usr/bin/env python
"""
Diagnostic script to check database configuration.
Run this on your cPanel server to see what credentials Django is using.
"""

import os
import sys
from pathlib import Path

# Add the project directory to the path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Load environment variables
from dotenv import load_dotenv
load_dotenv(os.path.join(BASE_DIR, '.env'), override=False)

print("=" * 60)
print("DATABASE CONFIGURATION CHECK")
print("=" * 60)
print()

# Check environment variables
print("Environment Variables:")
print("-" * 60)
print(f"DB_ENGINE: {os.getenv('DB_ENGINE', 'NOT SET')}")
print(f"DB_NAME: {os.getenv('DB_NAME', 'NOT SET')}")
print(f"DB_USER: {os.getenv('DB_USER', 'NOT SET')}")
print(f"DB_PASSWORD: {'*' * len(os.getenv('DB_PASSWORD', '')) if os.getenv('DB_PASSWORD') else 'NOT SET'} ({len(os.getenv('DB_PASSWORD', ''))} chars)")
print(f"DB_HOST: {os.getenv('DB_HOST', 'NOT SET')}")
print(f"DB_PORT: {os.getenv('DB_PORT', 'NOT SET')}")
print()

# Check Django settings
print("Django Settings:")
print("-" * 60)
try:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    import django
    django.setup()
    from django.conf import settings
    
    db_config = settings.DATABASES['default']
    print(f"ENGINE: {db_config.get('ENGINE', 'NOT SET')}")
    print(f"NAME: {db_config.get('NAME', 'NOT SET')}")
    print(f"USER: {db_config.get('USER', 'NOT SET')}")
    print(f"PASSWORD: {'*' * len(db_config.get('PASSWORD', '')) if db_config.get('PASSWORD') else 'NOT SET'} ({len(db_config.get('PASSWORD', ''))} chars)")
    print(f"HOST: {db_config.get('HOST', 'NOT SET')}")
    print(f"PORT: {db_config.get('PORT', 'NOT SET')}")
except Exception as e:
    print(f"Error loading Django settings: {e}")

print()
print("=" * 60)
print("INSTRUCTIONS:")
print("=" * 60)
print("1. Compare the DB_USER above with your MySQL user in cPanel")
print("2. Verify the DB_NAME matches your database name in cPanel")
print("3. Check that the password length matches what you expect")
print("4. Make sure the user has ALL PRIVILEGES on the database")
print()
print("To check in cPanel:")
print("  - Go to: MySQL Databases")
print("  - Look under 'Current Databases' for your database")
print("  - Look under 'Current Users' for your user")
print("  - Check 'Privileged Users' to ensure user has access")
print("=" * 60)
