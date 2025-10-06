#!/usr/bin/env python3
"""
Migration script to help transition from SQLite to Neon PostgreSQL
"""
import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """Check if required packages are installed"""
    print("🔍 Checking requirements...")
    
    try:
        import psycopg2
        print("✅ psycopg2 is installed")
    except ImportError:
        print("❌ psycopg2 not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "psycopg2-binary==2.9.9"])
        print("✅ psycopg2 installed successfully")
    
    try:
        import sqlalchemy
        print("✅ SQLAlchemy is available")
    except ImportError:
        print("❌ SQLAlchemy not found")
        return False
    
    return True

def check_env_file():
    """Check if .env file exists and has DATABASE_URL"""
    print("\n🔍 Checking environment configuration...")
    
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found")
        print("📝 Creating .env file template...")
        
        env_content = """# Neon Database (Recommended)
DATABASE_URL=postgresql://username:password@ep-xxx-xxx.us-east-1.aws.neon.tech/neondb?sslmode=require

# Alternative: SQLite (Development only)
# DATABASE_URL=sqlite:///./equipment_tracker.db

# API Keys
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Application Settings
DEBUG=True
HOST=0.0.0.0
PORT=8000
"""
        
        with open(".env", "w") as f:
            f.write(env_content)
        
        print("✅ .env file created. Please update with your Neon connection string.")
        return False
    
    with open(".env", "r") as f:
        content = f.read()
    
    if "neon.tech" in content:
        print("✅ Neon connection string found in .env")
        return True
    elif "sqlite" in content:
        print("⚠️  SQLite connection found. Please update to Neon connection string.")
        return False
    else:
        print("⚠️  No database connection found in .env")
        return False

def test_database_connection():
    """Test database connection"""
    print("\n🔍 Testing database connection...")
    
    try:
        from src.models.database import get_db
        from src.config import settings
        
        print(f"🔗 Connecting to: {settings.DATABASE_URL[:50]}...")
        db = next(get_db())
        print("✅ Database connection successful!")
        db.close()
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def create_tables():
    """Create database tables"""
    print("\n🔍 Creating database tables...")
    
    try:
        from src.models.database import create_tables
        create_tables()
        print("✅ Database tables created successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to create tables: {e}")
        return False

def seed_data():
    """Seed initial data"""
    print("\n🔍 Seeding initial data...")
    
    try:
        # Seed equipment specifications
        print("📦 Seeding equipment specifications...")
        subprocess.run([sys.executable, "seed_equipment_specs.py"], check=True)
        
        # Seed sample data
        print("📦 Seeding sample data...")
        subprocess.run([sys.executable, "seed_data.py"], check=True)
        
        print("✅ Data seeded successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to seed data: {e}")
        return False

def test_api():
    """Test API endpoints"""
    print("\n🔍 Testing API endpoints...")
    
    try:
        import requests
        import time
        
        # Wait a moment for server to start
        time.sleep(2)
        
        # Test health endpoint
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
        
        # Test equipment specifications endpoint
        response = requests.get("http://localhost:8000/equipment-specifications", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Equipment specifications endpoint working ({len(data)} specs)")
        else:
            print(f"❌ Equipment specifications endpoint failed: {response.status_code}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def main():
    """Main migration process"""
    print("🚀 Equipment Management Logistics - Neon Migration Helper")
    print("=" * 60)
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Requirements check failed. Please install missing packages.")
        return False
    
    # Check environment file
    if not check_env_file():
        print("\n❌ Environment configuration incomplete.")
        print("📝 Please update .env file with your Neon connection string.")
        print("📖 See NEON_SETUP.md for detailed instructions.")
        return False
    
    # Test database connection
    if not test_database_connection():
        print("\n❌ Database connection failed.")
        print("📝 Please check your Neon connection string in .env file.")
        return False
    
    # Create tables
    if not create_tables():
        print("\n❌ Failed to create database tables.")
        return False
    
    # Seed data
    if not seed_data():
        print("\n❌ Failed to seed initial data.")
        return False
    
    print("\n🎉 Migration completed successfully!")
    print("\n📋 Next steps:")
    print("1. Start the backend: uvicorn src.api.main:app --host localhost --port 8000 --reload")
    print("2. Start the frontend: cd frontend && npm start")
    print("3. Test the application at http://localhost:3000")
    print("4. Check the Equipment Management tab in Settings")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
