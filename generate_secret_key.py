#!/usr/bin/env python
"""
Generate a new Django SECRET_KEY for production use.
Run this script and copy the output to your .env file.
"""

from django.core.management.utils import get_random_secret_key

if __name__ == '__main__':
    secret_key = get_random_secret_key()
    print("\n" + "="*70)
    print("NEW SECRET KEY GENERATED")
    print("="*70)
    print("\nCopy this key to your .env file:\n")
    print(f"SECRET_KEY={secret_key}")
    print("\n" + "="*70)
    print("\n⚠️  IMPORTANT: Keep this key secret and secure!")
    print("⚠️  Never commit this key to version control!")
    print("⚠️  Use a different key for production than development!")
    print("\n" + "="*70 + "\n")
