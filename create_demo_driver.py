#!/usr/bin/env python3
"""
Create demo driver user for testing
"""
import sys
import os
sys.path.insert(0, 'src')

from src.models.database import create_tables, SessionLocal
from src.models.auth_models import User, UserRole
from src.services.auth_service import AuthService
from src.models.auth_schemas import UserCreate

def main():
    print("🚗 Creating Demo Driver User")
    print("=" * 50)
    
    # Create tables if they don't exist
    create_tables()
    
    # Create database session
    db = SessionLocal()
    auth_service = AuthService(db)
    
    try:
        # List existing users
        print("\n📋 Existing users:")
        users = db.query(User).all()
        for user in users:
            print(f"   - {user.username} ({user.role.value}) - {user.email}")
        
        print("\n👤 Creating demo users...")
        
        demo_users = [
            {
                "username": "driver",
                "email": "driver@demo.com",
                "password": "driver123",
                "full_name": "Demo Driver",
                "role": UserRole.DRIVER,
                "driver_license": "DL123456789",
                "phone_number": "+44 7700 900123",
                "company": "Demo Logistics Ltd"
            },
            {
                "username": "admin",
                "email": "admin@demo.com",
                "password": "admin123",
                "full_name": "Demo Admin",
                "role": UserRole.ADMIN
            },
            {
                "username": "manager",
                "email": "manager@demo.com",
                "password": "manager123",
                "full_name": "Demo Manager",
                "role": UserRole.MANAGER
            }
        ]
        
        created = 0
        for user_data in demo_users:
            try:
                existing = auth_service.get_user_by_username(user_data["username"])
                if existing:
                    print(f"   ℹ️  {user_data['username']} already exists")
                else:
                    user_create = UserCreate(**user_data)
                    new_user = auth_service.create_user(user_create)
                    print(f"   ✅ Created: {user_data['username']} ({user_data['role'].value})")
                    created += 1
            except Exception as e:
                print(f"   ⚠️  Error creating {user_data['username']}: {e}")
        
        print(f"\n✅ Created {created} new users")
        print("\n🔑 Demo Login Credentials:")
        print("=" * 50)
        print("\n🚗 DRIVER APP Login:")
        print("   URL: http://localhost:3001")
        print("   Username: driver")
        print("   Password: driver123")
        print("\n🏢 OFFICE DASHBOARD Login:")
        print("   URL: http://localhost:3000")
        print("   Username: admin")
        print("   Password: admin123")
        print("   OR")
        print("   Username: manager")
        print("   Password: manager123")
        print("\n" + "=" * 50)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()
