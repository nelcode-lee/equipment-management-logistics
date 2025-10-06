#!/usr/bin/env python3
"""
Create initial admin user for Equipment Management Logistics
"""
import sys
import os
sys.path.insert(0, 'src')

from src.models.database import create_tables, SessionLocal
from src.models.auth_models import User, UserRole
from src.services.auth_service import AuthService
from src.models.auth_schemas import UserCreate

def create_admin_user():
    """Create initial admin user"""
    print("🔐 Creating initial admin user...")
    
    # Create tables if they don't exist
    create_tables()
    
    # Create database session
    db = SessionLocal()
    auth_service = AuthService(db)
    
    try:
        # Check if admin user already exists
        existing_admin = auth_service.get_user_by_username("admin")
        if existing_admin:
            print("✅ Admin user already exists")
            return
        
        # Create admin user
        admin_data = UserCreate(
            username="admin",
            email="admin@equipment-logistics.com",
            password="Admin123",
            full_name="System Administrator",
            role=UserRole.ADMIN
        )
        
        admin_user = auth_service.create_user(admin_data)
        print(f"✅ Admin user created successfully!")
        print(f"   Username: {admin_user.username}")
        print(f"   Email: {admin_user.email}")
        print(f"   Role: {admin_user.role.value}")
        print(f"   ID: {admin_user.id}")
        print()
        print("🔑 Default credentials:")
        print("   Username: admin")
        print("   Password: Admin123")
        print()
        print("⚠️  IMPORTANT: Change the default password after first login!")
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        return False
    finally:
        db.close()
    
    return True

def create_demo_users():
    """Create demo users for testing"""
    print("\n👥 Creating demo users...")
    
    db = SessionLocal()
    auth_service = AuthService(db)
    
    demo_users = [
        {
            "username": "manager1",
            "email": "manager1@equipment-logistics.com",
            "password": "Manager123",
            "full_name": "John Manager",
            "role": UserRole.MANAGER
        },
        {
            "username": "driver1",
            "email": "driver1@equipment-logistics.com",
            "password": "Driver123",
            "full_name": "Mike Driver",
            "role": UserRole.DRIVER,
            "driver_license": "DL123456789",
            "phone_number": "+44 7700 900123",
            "company": "Logistics Co Ltd"
        },
        {
            "username": "viewer1",
            "email": "viewer1@equipment-logistics.com",
            "password": "Viewer123",
            "full_name": "Sarah Viewer",
            "role": UserRole.VIEWER
        }
    ]
    
    created_count = 0
    for user_data in demo_users:
        try:
            if not auth_service.get_user_by_username(user_data["username"]):
                user_create = UserCreate(**user_data)
                auth_service.create_user(user_create)
                print(f"✅ Created {user_data['role'].value}: {user_data['username']}")
                created_count += 1
            else:
                print(f"ℹ️  User already exists: {user_data['username']}")
        except Exception as e:
            print(f"❌ Error creating {user_data['username']}: {e}")
    
    print(f"\n🎉 Created {created_count} demo users")
    print("\n🔑 Demo credentials:")
    for user_data in demo_users:
        print(f"   {user_data['role'].value}: {user_data['username']} / {user_data['password']}")
    
    db.close()

if __name__ == "__main__":
    print("🚀 Equipment Management Logistics - User Setup")
    print("=" * 50)
    
    # Create admin user
    if create_admin_user():
        # Create demo users
        create_demo_users()
        
        print("\n🎉 User setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Start the application: ./quick_start.bash")
        print("2. Login with admin credentials")
        print("3. Change default passwords")
        print("4. Create additional users as needed")
    else:
        print("\n❌ User setup failed!")
        sys.exit(1)
