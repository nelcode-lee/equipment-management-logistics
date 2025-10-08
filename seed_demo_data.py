#!/usr/bin/env python3
"""
Demo data seeding script for Equipment Management Logistics
"""
import sys
import os
from datetime import datetime, timedelta
import random

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.models.database import SessionLocal, create_tables
from src.models.schemas import EquipmentMovement, CustomerBalance, EquipmentSpecification
from src.models.auth_models import User, UserRole
from src.services.auth_service import AuthService
from src.models.auth_schemas import UserCreate

def create_demo_users():
    """Create demo users for testing"""
    print("👥 Creating demo users...")
    
    db = SessionLocal()
    auth_service = AuthService(db)
    
    demo_users = [
        {
            "username": "admin",
            "email": "admin@equipment-logistics.com",
            "password": "Admin123",
            "full_name": "System Administrator",
            "role": UserRole.ADMIN
        },
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
                user = auth_service.create_user(UserCreate(**user_data))
                print(f"✅ Created {user.role.value}: {user.username}")
                created_count += 1
            else:
                print(f"ℹ️  {user_data['role'].value} {user_data['username']} already exists")
        except Exception as e:
            print(f"❌ Error creating {user_data['username']}: {e}")
    
    print(f"🎉 Created {created_count} demo users")
    db.close()

def create_demo_equipment_specs():
    """Create demo equipment specifications"""
    print("🔧 Creating equipment specifications...")
    
    db = SessionLocal()
    
    equipment_specs = [
        {
            "equipment_type": "Container",
            "name": "20ft Standard Container",
            "color": "Blue",
            "size": "20ft",
            "grade": "A",
            "description": "Standard 20ft shipping container",
            "default_threshold": 10,
            "is_active": True
        },
        {
            "equipment_type": "Container",
            "name": "40ft High Cube Container",
            "color": "White",
            "size": "40ft",
            "grade": "A",
            "description": "High cube 40ft container with extra height",
            "default_threshold": 8,
            "is_active": True
        },
        {
            "equipment_type": "Pallet",
            "name": "Euro Pallet",
            "color": "Brown",
            "size": "1200x800",
            "grade": "A",
            "description": "Standard Euro pallet",
            "default_threshold": 50,
            "is_active": True
        },
        {
            "equipment_type": "Pallet",
            "name": "Half Pallet",
            "color": "Blue",
            "size": "600x800",
            "grade": "B",
            "description": "Half-size Euro pallet",
            "default_threshold": 30,
            "is_active": True
        },
        {
            "equipment_type": "Cage",
            "name": "Blue Cage",
            "color": "Blue",
            "size": "Standard",
            "grade": "A",
            "description": "Standard blue transport cage",
            "default_threshold": 25,
            "is_active": True
        }
    ]
    
    from src.models.database import EquipmentSpecification as DBEquipmentSpec
    
    created_count = 0
    for spec_data in equipment_specs:
        try:
            existing = db.query(DBEquipmentSpec).filter(
                DBEquipmentSpec.equipment_type == spec_data["equipment_type"],
                DBEquipmentSpec.name == spec_data["name"]
            ).first()
            
            if not existing:
                spec = DBEquipmentSpec(**spec_data)
                db.add(spec)
                created_count += 1
                print(f"✅ Created {spec_data['equipment_type']}: {spec_data['name']}")
            else:
                print(f"ℹ️  {spec_data['equipment_type']}: {spec_data['name']} already exists")
        except Exception as e:
            print(f"❌ Error creating {spec_data['name']}: {e}")
    
    db.commit()
    print(f"🎉 Created {created_count} equipment specifications")
    db.close()

def create_demo_customers():
    """Create demo customer balances"""
    print("🏢 Creating customer balances...")
    
    db = SessionLocal()
    from src.models.database import CustomerBalance as DBCustomerBalance
    
    customers = [
        {"customer_name": "ABC Logistics Ltd", "equipment_type": "Container", "current_balance": 15, "threshold": 5},
        {"customer_name": "ABC Logistics Ltd", "equipment_type": "Pallet", "current_balance": 8, "threshold": 3},
        {"customer_name": "XYZ Transport Co", "equipment_type": "Container", "current_balance": 22, "threshold": 8},
        {"customer_name": "XYZ Transport Co", "equipment_type": "Cage", "current_balance": 12, "threshold": 4},
        {"customer_name": "Global Shipping", "equipment_type": "Container", "current_balance": 3, "threshold": 5},
        {"customer_name": "Global Shipping", "equipment_type": "Pallet", "current_balance": 1, "threshold": 2},
        {"customer_name": "Metro Freight", "equipment_type": "Container", "current_balance": 18, "threshold": 6},
        {"customer_name": "Metro Freight", "equipment_type": "Cage", "current_balance": 9, "threshold": 3},
        {"customer_name": "Coastal Logistics", "equipment_type": "Container", "current_balance": 7, "threshold": 4},
        {"customer_name": "Coastal Logistics", "equipment_type": "Pallet", "current_balance": 4, "threshold": 2}
    ]
    
    created_count = 0
    for customer_data in customers:
        try:
            existing = db.query(DBCustomerBalance).filter(
                DBCustomerBalance.customer_name == customer_data["customer_name"],
                DBCustomerBalance.equipment_type == customer_data["equipment_type"]
            ).first()
            
            if not existing:
                customer = DBCustomerBalance(**customer_data)
                db.add(customer)
                created_count += 1
                print(f"✅ Created {customer_data['customer_name']} - {customer_data['equipment_type']}: {customer_data['current_balance']}")
            else:
                print(f"ℹ️  {customer_data['customer_name']} - {customer_data['equipment_type']} already exists")
        except Exception as e:
            print(f"❌ Error creating {customer_data['customer_name']}: {e}")
    
    db.commit()
    print(f"🎉 Created {created_count} customer balances")
    db.close()

def create_demo_movements():
    """Create demo equipment movements"""
    print("🚛 Creating equipment movements...")
    
    db = SessionLocal()
    from src.models.database import EquipmentMovement as DBMovement
    
    # Sample data for movements
    equipment_types = ["Container", "Pallet", "Cage"]
    customers = ["ABC Logistics Ltd", "XYZ Transport Co", "Global Shipping", "Metro Freight", "Coastal Logistics"]
    equipment_names = ["20ft Standard Container", "Euro Pallet", "Blue Cage", "Half Pallet", "40ft High Cube Container"]
    equipment_colors = ["Blue", "Brown", "White", "Red"]
    equipment_sizes = ["20ft", "40ft", "1200x800", "600x800", "Standard"]
    equipment_grades = ["A", "B", "Food Grade"]
    
    movements = []
    base_date = datetime.now() - timedelta(days=30)
    
    for i in range(50):  # Create 50 movements
        movement_date = base_date + timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))
        
        movement = {
            "customer_name": random.choice(customers),
            "equipment_type": random.choice(equipment_types),
            "equipment_name": random.choice(equipment_names),
            "equipment_color": random.choice(equipment_colors),
            "equipment_size": random.choice(equipment_sizes),
            "equipment_grade": random.choice(equipment_grades),
            "quantity": random.randint(1, 10),
            "direction": random.choice(["in", "out"]),
            "timestamp": movement_date,
            "driver_name": f"Driver {random.randint(1, 10)}",
            "confidence_score": round(random.uniform(0.7, 0.99), 2),
            "notes": f"Movement {i+1} - {random.choice(['Routine delivery', 'Emergency pickup', 'Scheduled transfer', 'Maintenance return'])}",
            "verified": random.choice([True, False]),
            "source_image_url": f"/uploads/movement_{i+1}.jpg" if random.random() > 0.5 else None
        }
        movements.append(movement)
    
    created_count = 0
    for movement_data in movements:
        try:
            movement = DBMovement(**movement_data)
            db.add(movement)
            created_count += 1
        except Exception as e:
            print(f"❌ Error creating movement: {e}")
    
    db.commit()
    print(f"🎉 Created {created_count} equipment movements")
    db.close()

def create_demo_alerts():
    """Create demo alerts"""
    print("🚨 Creating alerts...")
    
    db = SessionLocal()
    from src.models.database import Alert as DBAlert
    
    # Create alerts for customers below threshold
    from src.models.database import CustomerBalance as DBCustomerBalance
    
    low_balance_customers = db.query(DBCustomerBalance).filter(
        DBCustomerBalance.current_balance < DBCustomerBalance.threshold
    ).all()
    
    alerts = []
    for customer in low_balance_customers:
        excess = customer.threshold - customer.current_balance
        alert = {
            "customer_name": customer.customer_name,
            "equipment_type": customer.equipment_type,
            "current_balance": customer.current_balance,
            "threshold": customer.threshold,
            "excess": excess,
            "priority": "high" if customer.current_balance == 0 else "medium",
            "created_at": datetime.now() - timedelta(hours=random.randint(1, 72)),
            "resolved": False
        }
        alerts.append(alert)
    
    # Add some general alerts
    general_alerts = [
        {
            "customer_name": "ABC Logistics Ltd",
            "equipment_type": "Container",
            "current_balance": 2,
            "threshold": 5,
            "excess": 3,
            "priority": "high",
            "created_at": datetime.now() - timedelta(hours=2),
            "resolved": False
        },
        {
            "customer_name": "Global Shipping",
            "equipment_type": "Pallet",
            "current_balance": 0,
            "threshold": 2,
            "excess": 2,
            "priority": "high",
            "created_at": datetime.now() - timedelta(hours=1),
            "resolved": False
        },
        {
            "customer_name": "Coastal Logistics",
            "equipment_type": "Pallet",
            "current_balance": 1,
            "threshold": 2,
            "excess": 1,
            "priority": "medium",
            "created_at": datetime.now() - timedelta(hours=4),
            "resolved": True
        }
    ]
    
    alerts.extend(general_alerts)
    
    created_count = 0
    for alert_data in alerts:
        try:
            alert = DBAlert(**alert_data)
            db.add(alert)
            created_count += 1
        except Exception as e:
            print(f"❌ Error creating alert: {e}")
    
    db.commit()
    print(f"🎉 Created {created_count} alerts")
    db.close()

def create_demo_driver_instructions():
    """Create demo driver instructions"""
    print("📋 Creating driver instructions...")
    
    db = SessionLocal()
    from src.models.database import DriverInstruction as DBDriverInstruction
    
    instructions = [
        {
            "title": "Daily Safety Check",
            "content": "Perform daily safety inspection of all equipment before departure. Check brakes, lights, and load security.",
            "priority": "HIGH",
            "is_active": True,
            "created_at": datetime.now() - timedelta(days=1)
        },
        {
            "title": "Container Loading Protocol",
            "content": "Ensure containers are properly secured and weight is evenly distributed. Use appropriate lifting equipment.",
            "priority": "HIGH",
            "is_active": True,
            "created_at": datetime.now() - timedelta(days=2)
        },
        {
            "title": "Fuel Efficiency Tips",
            "content": "Maintain steady speed, avoid rapid acceleration, and use cruise control when appropriate to improve fuel efficiency.",
            "priority": "MEDIUM",
            "is_active": True,
            "created_at": datetime.now() - timedelta(days=3)
        },
        {
            "title": "Customer Service Guidelines",
            "content": "Always be courteous and professional when interacting with customers. Report any issues immediately.",
            "priority": "MEDIUM",
            "is_active": True,
            "created_at": datetime.now() - timedelta(days=4)
        },
        {
            "title": "Emergency Procedures",
            "content": "In case of emergency, contact dispatch immediately. Follow safety protocols and ensure personal safety first.",
            "priority": "HIGH",
            "is_active": True,
            "created_at": datetime.now() - timedelta(days=5)
        }
    ]
    
    created_count = 0
    for instruction_data in instructions:
        try:
            instruction = DBDriverInstruction(**instruction_data)
            db.add(instruction)
            created_count += 1
        except Exception as e:
            print(f"❌ Error creating instruction: {e}")
    
    db.commit()
    print(f"🎉 Created {created_count} driver instructions")
    db.close()

def main():
    """Main seeding function"""
    print("🌱 Equipment Management Logistics - Demo Data Seeding")
    print("=" * 60)
    
    # Create tables first
    print("📊 Creating database tables...")
    create_tables()
    print("✅ Database tables created")
    
    # Seed all demo data
    create_demo_users()
    create_demo_equipment_specs()
    create_demo_customers()
    create_demo_movements()
    create_demo_alerts()
    create_demo_driver_instructions()
    
    print("\n🎉 Demo data seeding completed successfully!")
    print("\n📋 Demo Access Credentials:")
    print("   Admin: admin / Admin123")
    print("   Manager: manager1 / Manager123")
    print("   Driver: driver1 / Driver123")
    print("   Viewer: viewer1 / Viewer123")
    print("\n🚀 You can now test the dashboard with real data!")

if __name__ == "__main__":
    main()
