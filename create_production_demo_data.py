"""
Create demo data for production demo environment
This script creates realistic, production-ready demo data for showcasing the system
"""
from src.models.database import SessionLocal, EquipmentMovement, Customer, CustomerBalance, Driver, Vehicle, DriverInstruction
from datetime import datetime, timedelta
import uuid
import random

def create_demo_data():
    """Create comprehensive demo data for production"""
    db = SessionLocal()
    
    try:
        # Clear existing demo data (optional - be careful in production!)
        # Uncomment only if you want to reset demo data
        # db.query(DriverInstruction).delete()
        # db.query(Driver).delete()
        # db.query(Vehicle).delete()
        # db.query(EquipmentMovement).delete()
        # db.query(CustomerBalance).delete()
        # db.query(Customer).delete()
        
        print("📦 Creating demo vehicles...")
        vehicles = [
            Vehicle(
                id=str(uuid.uuid4()),
                fleet_number="VAN-001",
                registration="AB12 CDE",
                make="Mercedes",
                model="Sprinter",
                year=2022,
                vehicle_type="Van",
                capacity="3.5 tonne",
                status="available",
                mot_expiry=datetime.now() + timedelta(days=180),
                insurance_expiry=datetime.now() + timedelta(days=90),
                mileage=45000,
                notes="Main delivery van - North London routes"
            ),
            Vehicle(
                id=str(uuid.uuid4()),
                fleet_number="VAN-002",
                registration="CD34 EFG",
                make="Ford",
                model="Transit",
                year=2021,
                vehicle_type="Van",
                capacity="3.0 tonne",
                status="available",
                mot_expiry=datetime.now() + timedelta(days=220),
                insurance_expiry=datetime.now() + timedelta(days=120),
                mileage=62000,
                notes="Secondary van - South London routes"
            ),
            Vehicle(
                id=str(uuid.uuid4()),
                fleet_number="TRUCK-001",
                registration="EF56 HIJ",
                make="DAF",
                model="LF",
                year=2023,
                vehicle_type="Truck",
                capacity="7.5 tonne",
                status="available",
                mot_expiry=datetime.now() + timedelta(days=350),
                insurance_expiry=datetime.now() + timedelta(days=180),
                mileage=28000,
                last_service_date=datetime.now() - timedelta(days=45),
                next_service_date=datetime.now() + timedelta(days=135),
                notes="Heavy loads and long distance deliveries"
            )
        ]
        
        for vehicle in vehicles:
            db.add(vehicle)
        
        print("👥 Creating demo drivers...")
        drivers = [
            Driver(
                id=str(uuid.uuid4()),
                driver_name="John Smith",
                employee_id="EMP001",
                email="john.smith@demo-equipment.co.uk",
                phone="+44 7700 900001",
                license_number="SMITH123456JD7EE",
                license_expiry=datetime.now() + timedelta(days=1200),
                status="active",
                assigned_vehicle_id=vehicles[0].id,
                notes="Senior driver - 15 years experience"
            ),
            Driver(
                id=str(uuid.uuid4()),
                driver_name="Sarah Johnson",
                employee_id="EMP002",
                email="sarah.johnson@demo-equipment.co.uk",
                phone="+44 7700 900002",
                license_number="JOHNS987654SJ8FF",
                license_expiry=datetime.now() + timedelta(days=900),
                status="active",
                assigned_vehicle_id=vehicles[1].id,
                notes="Excellent customer service - handles difficult sites"
            ),
            Driver(
                id=str(uuid.uuid4()),
                driver_name="Mike Wilson",
                employee_id="EMP003",
                email="mike.wilson@demo-equipment.co.uk",
                phone="+44 7700 900003",
                license_number="WILSO789012MW9GG",
                license_expiry=datetime.now() + timedelta(days=450),
                status="active",
                notes="HGV licensed - handles truck deliveries"
            ),
            Driver(
                id=str(uuid.uuid4()),
                driver_name="Lisa Brown",
                employee_id="EMP004",
                email="lisa.brown@demo-equipment.co.uk",
                phone="+44 7700 900004",
                license_number="BROWN456789LB0HH",
                license_expiry=datetime.now() + timedelta(days=730),
                status="active",
                notes="Part-time driver - weekends and cover"
            )
        ]
        
        for driver in drivers:
            db.add(driver)
        
        print("🏢 Creating demo customers...")
        customers_data = [
            {
                "name": "ABC Construction Ltd",
                "contact": "James Mitchell",
                "phone": "+44 20 7946 0001",
                "address": "145 High Street, London, E1 6AN",
                "movements": [
                    {"type": "cage", "direction": "in", "quantity": 30, "days_ago": 15},
                    {"type": "cage", "direction": "out", "quantity": 8, "days_ago": 7},
                    {"type": "barrier", "direction": "in", "quantity": 20, "days_ago": 12},
                    {"type": "barrier", "direction": "out", "quantity": 5, "days_ago": 3},
                ],
                "balance": {"cage": 22, "barrier": 15},
                "threshold": 20
            },
            {
                "name": "XYZ Builders Group",
                "contact": "Emma Thompson",
                "phone": "+44 20 7946 0002",
                "address": "78 Victoria Road, London, SW1A 1AA",
                "movements": [
                    {"type": "scaffolding", "direction": "in", "quantity": 45, "days_ago": 20},
                    {"type": "scaffolding", "direction": "out", "quantity": 12, "days_ago": 10},
                    {"type": "cage", "direction": "in", "quantity": 15, "days_ago": 8},
                ],
                "balance": {"scaffolding": 33, "cage": 15},
                "threshold": 25
            },
            {
                "name": "London Retail Co",
                "contact": "David Chen",
                "phone": "+44 20 7946 0003",
                "address": "92 Oxford Street, London, W1D 1BS",
                "movements": [
                    {"type": "barrier", "direction": "in", "quantity": 25, "days_ago": 30},
                    {"type": "barrier", "direction": "out", "quantity": 17, "days_ago": 5},
                ],
                "balance": {"barrier": 8},
                "threshold": 10
            },
            {
                "name": "Thames Projects Ltd",
                "contact": "Sophie Williams",
                "phone": "+44 20 7946 0004",
                "address": "234 River Street, London, SE1 9SG",
                "movements": [
                    {"type": "cage", "direction": "in", "quantity": 50, "days_ago": 25},
                    {"type": "cage", "direction": "out", "quantity": 19, "days_ago": 8},
                    {"type": "scaffolding", "direction": "in", "quantity": 30, "days_ago": 18},
                    {"type": "scaffolding", "direction": "out", "quantity": 10, "days_ago": 4},
                ],
                "balance": {"cage": 31, "scaffolding": 20},
                "threshold": 30
            },
            {
                "name": "Premier Developments",
                "contact": "Alex Kumar",
                "phone": "+44 20 7946 0005",
                "address": "56 Park Lane, London, W1K 1QE",
                "movements": [
                    {"type": "barrier", "direction": "in", "quantity": 35, "days_ago": 14},
                    {"type": "barrier", "direction": "out", "quantity": 8, "days_ago": 6},
                    {"type": "cage", "direction": "in", "quantity": 20, "days_ago": 10},
                    {"type": "cage", "direction": "out", "quantity": 3, "days_ago": 2},
                ],
                "balance": {"barrier": 27, "cage": 17},
                "threshold": 25
            }
        ]
        
        for customer_data in customers_data:
            # Create customer
            customer = Customer(
                id=str(uuid.uuid4()),
                customer_name=customer_data["name"],
                contact_person=customer_data["contact"],
                phone=customer_data["phone"],
                address=customer_data["address"],
                created_at=datetime.now() - timedelta(days=90)
            )
            db.add(customer)
            
            # Create movements
            for movement in customer_data["movements"]:
                movement_date = datetime.now() - timedelta(days=movement["days_ago"])
                eq_movement = EquipmentMovement(
                    id=str(uuid.uuid4()),
                    customer_name=customer_data["name"],
                    equipment_type=movement["type"],
                    quantity=movement["quantity"],
                    direction=movement["direction"],
                    movement_date=movement_date,
                    driver_name=random.choice(drivers).driver_name,
                    notes=f"Demo {movement['direction']} movement",
                    created_at=movement_date
                )
                db.add(eq_movement)
            
            # Create balances
            for eq_type, quantity in customer_data["balance"].items():
                balance = CustomerBalance(
                    id=str(uuid.uuid4()),
                    customer_name=customer_data["name"],
                    equipment_type=eq_type,
                    quantity=quantity,
                    threshold=customer_data["threshold"],
                    last_updated=datetime.now()
                )
                db.add(balance)
        
        print("📋 Creating demo driver instructions...")
        instructions = [
            DriverInstruction(
                id=str(uuid.uuid4()),
                title="Urgent Collection - ABC Construction",
                content="Customer has 22 cages on site, threshold is 20. Please collect excess equipment.",
                priority="HIGH",
                status="pending",
                assigned_driver=drivers[0].driver_name,
                customer_name="ABC Construction Ltd",
                delivery_location="145 High Street, London, E1 6AN",
                contact_phone="+44 20 7946 0001",
                delivery_date=datetime.now() + timedelta(days=1),
                equipment_type="cage",
                equipment_quantity=2,
                special_instructions="Contact James Mitchell before arrival. Use rear entrance.",
                created_by="System Auto-Generated",
                created_at=datetime.now() - timedelta(hours=2)
            ),
            DriverInstruction(
                id=str(uuid.uuid4()),
                title="Scaffolding Delivery - XYZ Builders",
                content="Deliver 15 scaffolding units to XYZ Builders construction site.",
                priority="MEDIUM",
                status="in_progress",
                assigned_driver=drivers[1].driver_name,
                customer_name="XYZ Builders Group",
                delivery_location="78 Victoria Road, London, SW1A 1AA",
                contact_phone="+44 20 7946 0002",
                delivery_date=datetime.now(),
                equipment_type="scaffolding",
                equipment_quantity=15,
                special_instructions="Site access from 7am-5pm only. Foreman: Emma Thompson",
                created_by="Office Manager",
                created_at=datetime.now() - timedelta(days=1)
            ),
            DriverInstruction(
                id=str(uuid.uuid4()),
                title="Collection Alert - Thames Projects",
                content="Customer has 31 cages, threshold 30. Schedule collection.",
                priority="HIGH",
                status="pending",
                assigned_driver=drivers[2].driver_name,
                customer_name="Thames Projects Ltd",
                delivery_location="234 River Street, London, SE1 9SG",
                contact_phone="+44 20 7946 0004",
                delivery_date=datetime.now() + timedelta(days=2),
                equipment_type="cage",
                equipment_quantity=5,
                special_instructions="Loading bay access code: 1234. Contact Sophie Williams",
                created_by="System Auto-Generated",
                created_at=datetime.now() - timedelta(hours=5)
            ),
            DriverInstruction(
                id=str(uuid.uuid4()),
                title="Barrier Collection - Premier Developments",
                content="Collect excess barriers from Premier Developments site.",
                priority="MEDIUM",
                status="pending",
                assigned_driver=drivers[0].driver_name,
                customer_name="Premier Developments",
                delivery_location="56 Park Lane, London, W1K 1QE",
                contact_phone="+44 20 7946 0005",
                delivery_date=datetime.now() + timedelta(days=3),
                equipment_type="barrier",
                equipment_quantity=10,
                special_instructions="Premium client - priority service. Contact Alex Kumar",
                created_by="Office Manager",
                created_at=datetime.now() - timedelta(hours=8)
            )
        ]
        
        for instruction in instructions:
            db.add(instruction)
        
        # Commit all changes
        db.commit()
        
        print("\n✅ Demo data created successfully!")
        print("\n📊 Summary:")
        print(f"  - Vehicles: {len(vehicles)}")
        print(f"  - Drivers: {len(drivers)}")
        print(f"  - Customers: {len(customers_data)}")
        print(f"  - Movements: {sum(len(c['movements']) for c in customers_data)}")
        print(f"  - Instructions: {len(instructions)}")
        print("\n🎯 Demo System Ready!")
        print("\nDemo Users:")
        print("  Manager: manager@demo.com / demo123")
        print("  Driver: driver@demo.com / demo123")
        
    except Exception as e:
        print(f"❌ Error creating demo data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_demo_data()

