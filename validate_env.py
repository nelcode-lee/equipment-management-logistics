#!/usr/bin/env python3
"""
Environment Validation Script for Equipment Management Logistics
Validates all environment variables and configuration settings
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import urlparse
import re

# Add src to path
sys.path.insert(0, 'src')

def load_environment():
    """Load environment variables from .env file"""
    env_file = Path('.env')
    if env_file.exists():
        load_dotenv()
        print("✅ .env file loaded successfully")
        return True
    else:
        print("❌ .env file not found")
        return False

def validate_required_vars():
    """Validate required environment variables"""
    print("\n🔍 Validating required environment variables...")
    
    required_vars = {
        'ANTHROPIC_API_KEY': 'Required for AI processing of delivery notes',
        'DATABASE_URL': 'Required for database connection',
        'DEBUG': 'Required for application mode',
        'HOST': 'Required for server configuration',
        'PORT': 'Required for server configuration'
    }
    
    missing_vars = []
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        if not value:
            print(f"❌ {var}: Missing - {description}")
            missing_vars.append(var)
        else:
            print(f"✅ {var}: Set")
    
    return len(missing_vars) == 0, missing_vars

def validate_database_url():
    """Validate database URL format"""
    print("\n🗄️  Validating database configuration...")
    
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("❌ DATABASE_URL not set")
        return False
    
    try:
        parsed = urlparse(db_url)
        
        if parsed.scheme == 'sqlite':
            print("✅ SQLite database configured")
            # Check if SQLite file path is valid
            db_path = parsed.path.lstrip('/')
            if db_path and not db_path.startswith(':'):
                print(f"   Database file: {db_path}")
            return True
            
        elif parsed.scheme == 'postgresql':
            print("✅ PostgreSQL database configured")
            print(f"   Host: {parsed.hostname}")
            print(f"   Port: {parsed.port or 5432}")
            print(f"   Database: {parsed.path.lstrip('/')}")
            print(f"   SSL Mode: {'require' if 'sslmode=require' in db_url else 'not specified'}")
            return True
            
        else:
            print(f"❌ Unsupported database type: {parsed.scheme}")
            return False
            
    except Exception as e:
        print(f"❌ Invalid DATABASE_URL format: {e}")
        return False

def validate_api_keys():
    """Validate API key formats"""
    print("\n🔑 Validating API keys...")
    
    # Anthropic API Key
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    if anthropic_key:
        if anthropic_key.startswith('sk-ant-') and len(anthropic_key) > 20:
            print("✅ ANTHROPIC_API_KEY: Valid format")
        else:
            print("⚠️  ANTHROPIC_API_KEY: Invalid format (should start with 'sk-ant-')")
    else:
        print("❌ ANTHROPIC_API_KEY: Not set")
    
    # Twilio credentials
    twilio_sid = os.getenv('TWILIO_ACCOUNT_SID')
    twilio_token = os.getenv('TWILIO_AUTH_TOKEN')
    
    if twilio_sid and twilio_token:
        if twilio_sid.startswith('AC') and len(twilio_sid) == 34:
            print("✅ TWILIO_ACCOUNT_SID: Valid format")
        else:
            print("⚠️  TWILIO_ACCOUNT_SID: Invalid format")
            
        if len(twilio_token) == 32:
            print("✅ TWILIO_AUTH_TOKEN: Valid format")
        else:
            print("⚠️  TWILIO_AUTH_TOKEN: Invalid format")
    else:
        print("ℹ️  Twilio credentials: Not set (optional)")

def validate_aws_config():
    """Validate AWS S3 configuration"""
    print("\n☁️  Validating AWS S3 configuration...")
    
    aws_key = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret = os.getenv('AWS_SECRET_ACCESS_KEY')
    s3_bucket = os.getenv('S3_BUCKET_NAME')
    
    if aws_key and aws_secret and s3_bucket:
        if len(aws_key) == 20 and aws_key.isalnum():
            print("✅ AWS_ACCESS_KEY_ID: Valid format")
        else:
            print("⚠️  AWS_ACCESS_KEY_ID: Invalid format")
            
        if len(aws_secret) == 40:
            print("✅ AWS_SECRET_ACCESS_KEY: Valid format")
        else:
            print("⚠️  AWS_SECRET_ACCESS_KEY: Invalid format")
            
        if re.match(r'^[a-z0-9.-]+$', s3_bucket):
            print("✅ S3_BUCKET_NAME: Valid format")
        else:
            print("⚠️  S3_BUCKET_NAME: Invalid format")
    else:
        print("ℹ️  AWS S3 configuration: Not set (optional)")

def validate_application_settings():
    """Validate application settings"""
    print("\n⚙️  Validating application settings...")
    
    # Debug mode
    debug = os.getenv('DEBUG', 'True').lower()
    if debug in ['true', 'false']:
        print(f"✅ DEBUG: {debug.title()}")
    else:
        print("⚠️  DEBUG: Invalid value (should be 'True' or 'False')")
    
    # Port number
    try:
        port = int(os.getenv('PORT', '8000'))
        if 1 <= port <= 65535:
            print(f"✅ PORT: {port}")
        else:
            print(f"⚠️  PORT: {port} (should be between 1-65535)")
    except ValueError:
        print("❌ PORT: Invalid number")
    
    # Host
    host = os.getenv('HOST', '0.0.0.0')
    if host in ['0.0.0.0', 'localhost', '127.0.0.1']:
        print(f"✅ HOST: {host}")
    else:
        print(f"⚠️  HOST: {host} (unusual value)")

def validate_file_settings():
    """Validate file upload settings"""
    print("\n📁 Validating file upload settings...")
    
    try:
        max_size = int(os.getenv('MAX_FILE_SIZE_MB', '10'))
        if max_size > 0:
            print(f"✅ MAX_FILE_SIZE_MB: {max_size}MB")
        else:
            print("⚠️  MAX_FILE_SIZE_MB: Should be positive")
    except ValueError:
        print("❌ MAX_FILE_SIZE_MB: Invalid number")
    
    extensions = os.getenv('ALLOWED_EXTENSIONS', 'jpg,jpeg,png,gif,webp')
    if extensions:
        print(f"✅ ALLOWED_EXTENSIONS: {extensions}")
    else:
        print("⚠️  ALLOWED_EXTENSIONS: Not set")

def test_database_connection():
    """Test database connection"""
    print("\n🔗 Testing database connection...")
    
    try:
        from src.models.database import engine
        with engine.connect() as conn:
            print("✅ Database connection successful")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def validate_security_settings():
    """Validate security settings"""
    print("\n🔒 Validating security settings...")
    
    secret_key = os.getenv('SECRET_KEY')
    if secret_key and secret_key != 'your_secret_key_here':
        if len(secret_key) >= 32:
            print("✅ SECRET_KEY: Set and secure")
        else:
            print("⚠️  SECRET_KEY: Too short (should be at least 32 characters)")
    else:
        print("⚠️  SECRET_KEY: Using default value (not secure for production)")
    
    cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://localhost:8000')
    if cors_origins:
        print(f"✅ CORS_ORIGINS: {cors_origins}")
    else:
        print("⚠️  CORS_ORIGINS: Not set")

def main():
    """Main validation function"""
    print("🔍 Equipment Management Logistics - Environment Validation")
    print("=" * 60)
    
    # Load environment
    if not load_environment():
        sys.exit(1)
    
    # Run all validations
    validations = [
        validate_required_vars,
        validate_database_url,
        validate_api_keys,
        validate_aws_config,
        validate_application_settings,
        validate_file_settings,
        validate_security_settings,
        test_database_connection
    ]
    
    all_passed = True
    
    for validation in validations:
        try:
            result = validation()
            if result is False:
                all_passed = False
        except Exception as e:
            print(f"❌ Validation error: {e}")
            all_passed = False
    
    # Summary
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All validations passed! Your environment is properly configured.")
    else:
        print("⚠️  Some validations failed. Please check the configuration above.")
        print("\n📝 Next steps:")
        print("   1. Update .env file with missing or incorrect values")
        print("   2. Run this script again to verify")
        print("   3. Check the .env.example file for reference")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
