#!/usr/bin/env python3
"""
Generate a secure secret key for the Equipment Management Logistics system
"""

import secrets
import string

def generate_secret_key(length=32):
    """Generate a secure secret key"""
    alphabet = string.ascii_letters + string.digits + '-_'
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_jwt_secret(length=64):
    """Generate a JWT secret key"""
    return secrets.token_urlsafe(length)

if __name__ == "__main__":
    print("🔐 Generating secure keys for Equipment Management Logistics")
    print("=" * 60)
    
    # Generate secret key
    secret_key = generate_secret_key(32)
    print(f"SECRET_KEY={secret_key}")
    
    # Generate JWT secret
    jwt_secret = generate_jwt_secret(64)
    print(f"JWT_SECRET={jwt_secret}")
    
    print("\n📝 Add these to your .env file:")
    print(f"SECRET_KEY={secret_key}")
    print(f"JWT_SECRET={jwt_secret}")
    
    print("\n✅ Keys generated successfully!")
    print("⚠️  Keep these keys secure and never commit them to version control")
