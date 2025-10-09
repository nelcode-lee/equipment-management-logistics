#!/usr/bin/env python3
"""
Seed realistic demo data for Equipment Management System
- Fictional company names
- Mathematically correct equipment tallies
- Realistic movement patterns
"""
import os
import sys
from datetime import datetime, timedelta
import random
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sqlalchemy.orm import Session
from src.models.database import SessionLocal, create_tables
from src.models.database import (
    Customer as DBCustomer,
    EquipmentMovement as DBMovement,
    CustomerBalance as DBBalance,
    EquipmentSpecification as DBEquipmentSpec,
    Driver as DBDriver,
    Vehicle as DBVehicle,
    DriverInstruction as DBInstruction
)

load_dotenv()

# Fictional company data
COMPANIES = [
    {
        "name": "BuildRight Construction Ltd",
        "contact": "Sarah Mitchell",
        "email": "sarah.mitchell@buildright.example",
        "phone": "01234 567890",
        "address": "45 Industrial Estate",
        "city": "Manchester",
        "postcode": "M15 4FN",
        "credit_limit": 50000,
    },
    {
        "name": "FreshMart Supermarkets",
        "contact": "James Thompson",
        "email": "james.t@freshmart.example",
        "phone": "01234 567891",
        "address": "12 Retail Park",
        "city": "Birmingham",
        "postcode": "B5 7RG",
        "credit_limit": 75000,
    },
    {
        "name": "TechFlow Manufacturing",
        "contact": "Emily Chen",
        "email": "e.chen@techflow.example",
        "phone": "01234 567892",
        "address": "88 Technology Drive",
        "city": "Leeds",
        "postcode": "LS2 8JT",
        "credit_limit": 100000,
    },
    {
        "name": "GreenLeaf Wholesale",
        "contact": "Michael Brown",
        "email": "m.brown@greenleaf.example",
        "phone": "01234 567893",
        "address": "23 Distribution Centre",
        "city": "Bristol",
        "postcode": "BS1 6QA",
        "credit_limit": 60000,
    },
    {
        "name": "QuickServe Logistics",
        "contact": "Rachel Green",
        "email": "rachel@quickserve.example",
        "phone": "01234 567894",
        "address": "67 Warehouse Road",
        "city": "Liverpool",
        "postcode": "L3 9PP",
        "credit_limit": 80000,
    },
    {
        "name": "Premier Foods Distribution",
        "contact": "David Wilson",
        "email": "d.wilson@premierfoods.example",
        "phone": "01234 567895",
        "address": "34 Commerce Street",
        "city": "Sheffield",
        "postcode": "S1 2JE",
        "credit_limit": 90000,
    },
]

# Equipment types and their specifications
EQUIPMENT_SPECS = [
    {"type": "pallet", "name": "Euro Pallet", "color": "Brown", "size": "1200x800mm", "grade": "Grade A", "threshold": 50},
    {"type": "pallet", "name": "UK Pallet", "color": "Brown", "size": "1200x1000mm", "grade": "Grade A", "threshold": 40},
    {"type": "cage", "name": "Blue Cage", "color": "Blue", "size": "Standard", "grade": "Heavy Duty", "threshold": 30},
    {"type": "cage", "name": "Red Cage", "color": "Red", "size": "Standard", "grade": "Heavy Duty", "threshold": 25},
    {"type": "cage", "name": "Green Cage", "color": "Green", "size": "Large", "grade": "Standard", "threshold": 20},
    {"type": "stillage", "name": "Post Stillage", "color": "Silver", "size": "1200x1000mm", "grade": "Industrial", "threshold": 15},
    {"type": "dolly", "name": "Platform Dolly", "color": "Black", "size": "600x400mm", "grade": "Standard", "threshold": 35},
]

# Drivers
DRIVERS = [
    {
        "name": "Tom Harrison",
        "employee_id": "DRV-101",
        "email": "tom.h@company.example",
        "phone": "07700 900001",
        "license": "HARRI901234TH5AB",
        "license_expiry": datetime.now() + timedelta(days=730),
    },
    {
        "name": "Lisa Anderson",
        "employee_id": "DRV-102",
        "email": "lisa.a@company.example",
        "phone": "07700 900002",
        "license": "ANDER234567LA9CD",
        "license_expiry": datetime.now() + timedelta(days=550),
    },
    {
        "name": "Mark Roberts",
        "employee_id": "DRV-103",
        "email": "mark.r@company.example",
        "phone": "07700 900003",
        "license": "ROBER567890MR3EF",
        "license_expiry": datetime.now() + timedelta(days=820),
    },
    {
        "name": "Sophie Turner",
        "employee_id": "DRV-104",
        "email": "sophie.t@company.example",
        "phone": "07700 900004",
        "license": "TURNE123456ST7GH",
        "license_expiry": datetime.now() + timedelta(days=650),
    },
]

# Vehicles
VEHICLES = [
    {
        "fleet_number": "VAN-201",
        "registration": "BX21 ABC",
        "make": "Mercedes",
        "model": "Sprinter",
        "year": 2021,
        "type": "Van",
        "capacity": "3.5 tonne",
    },
    {
        "fleet_number": "VAN-202",
        "registration": "CY22 DEF",
        "make": "Ford",
        "model": "Transit",
        "year": 2022,
        "type": "Van",
        "capacity": "3.5 tonne",
    },
    {
        "fleet_number": "TRUCK-301",
        "registration": "DZ20 GHI",
        "make": "DAF",
        "model": "LF",
        "year": 2020,
        "type": "Truck",
        "capacity": "7.5 tonne",
    },
    {
        "fleet_number": "TRUCK-302",
        "registration": "EA23 JKL",
        "make": "Iveco",
        "model": "Eurocargo",
        "year": 2023,
        "type": "Truck",
        "capacity": "12 tonne",
    },
]

def clear_existing_data(db: Session):
    """Clear existing demo data"""
    print("Clearing existing data...")
    db.query(DBInstruction).delete()
    db.query(DBBalance).delete()
    db.query(DBMovement).delete()
    db.query(DBEquipmentSpec).delete()
    db.query(DBDriver).delete()
    db.query(DBVehicle).delete()
    db.query(DBCustomer).delete()
    db.commit()
    print("✓ Existing data cleared")

def seed_customers(db: Session):
    """Seed customer data"""
    print("\nSeeding customers...")
    customers = []
    for company in COMPANIES:
        customer = DBCustomer(
            customer_name=company["name"],
            contact_person=company["contact"],
            email=company["email"],
            phone=company["phone"],
            address=company["address"],
            city=company["city"],
            postcode=company["postcode"],
            country="UK",
            status="active",
            credit_limit=company["credit_limit"],
            payment_terms="30 days",
            notes=f"Demo customer - {company['city']} location"
        )
        db.add(customer)
        customers.append(customer)
    
    db.commit()
    print(f"✓ Created {len(customers)} customers")
    return customers

def seed_equipment_specs(db: Session):
    """Seed equipment specifications"""
    print("\nSeeding equipment specifications...")
    specs = []
    for spec_data in EQUIPMENT_SPECS:
        spec = DBEquipmentSpec(
            equipment_type=spec_data["type"],
            name=spec_data["name"],
            color=spec_data["color"],
            size=spec_data["size"],
            grade=spec_data["grade"],
            description=f"{spec_data['name']} - {spec_data['grade']}",
            default_threshold=spec_data["threshold"],
            is_active=True
        )
        db.add(spec)
        specs.append(spec)
    
    db.commit()
    print(f"✓ Created {len(specs)} equipment specifications")
    return specs

def seed_drivers(db: Session):
    """Seed driver data"""
    print("\nSeeding drivers...")
    drivers = []
    for driver_data in DRIVERS:
        driver = DBDriver(
            driver_name=driver_data["name"],
            employee_id=driver_data["employee_id"],
            email=driver_data["email"],
            phone=driver_data["phone"],
            license_number=driver_data["license"],
            license_expiry=driver_data["license_expiry"],
            status="active",
            notes="Demo driver"
        )
        db.add(driver)
        drivers.append(driver)
    
    db.commit()
    print(f"✓ Created {len(drivers)} drivers")
    return drivers

def seed_vehicles(db: Session, drivers):
    """Seed vehicle data"""
    print("\nSeeding vehicles...")
    vehicles = []
    for i, vehicle_data in enumerate(VEHICLES):
        vehicle = DBVehicle(
            fleet_number=vehicle_data["fleet_number"],
            registration=vehicle_data["registration"],
            make=vehicle_data["make"],
            model=vehicle_data["model"],
            year=vehicle_data["year"],
            vehicle_type=vehicle_data["type"],
            capacity=vehicle_data["capacity"],
            status="available",
            mot_expiry=datetime.now() + timedelta(days=300 + i*30),
            insurance_expiry=datetime.now() + timedelta(days=200 + i*20),
            mileage=50000 + i*10000,
            notes="Demo vehicle"
        )
        db.add(vehicle)
        vehicles.append(vehicle)
        
        # Assign first 2 vehicles to first 2 drivers
        if i < 2 and i < len(drivers):
            drivers[i].assigned_vehicle_id = vehicle.id
    
    db.commit()
    print(f"✓ Created {len(vehicles)} vehicles")
    return vehicles

def seed_movements_and_balances(db: Session, customers, drivers):
    """
    Seed equipment movements with mathematically correct balances
    
    Logic:
    - "in" direction = equipment delivered TO customer (increases their balance)
    - "out" direction = equipment collected FROM customer (decreases their balance)
    - Balance = Total IN - Total OUT
    """
    print("\nSeeding equipment movements (with correct math)...")
    
    # Track balances for each customer/equipment combination
    balances_tracker = {}
    movements = []
    
    # Define movement scenarios for each customer
    movement_scenarios = [
        # BuildRight Construction - Heavy pallet user
        {
            "customer": COMPANIES[0]["name"],
            "equipment": "pallet",
            "movements": [
                {"days_ago": 30, "direction": "in", "qty": 100, "note": "Initial delivery of Euro pallets"},
                {"days_ago": 25, "direction": "out", "qty": 40, "note": "Collection after project completion"},
                {"days_ago": 20, "direction": "in", "qty": 80, "note": "New project - large delivery"},
                {"days_ago": 15, "direction": "out", "qty": 30, "note": "Partial return"},
                {"days_ago": 10, "direction": "in", "qty": 60, "note": "Additional pallets for expansion"},
                {"days_ago": 5, "direction": "out", "qty": 25, "note": "Return of damaged pallets"},
            ]
        },
        # FreshMart - Cage heavy user
        {
            "customer": COMPANIES[1]["name"],
            "equipment": "cage",
            "movements": [
                {"days_ago": 28, "direction": "in", "qty": 50, "note": "Blue cages for produce delivery"},
                {"days_ago": 21, "direction": "in", "qty": 40, "note": "Additional cages for promotion"},
                {"days_ago": 14, "direction": "out", "qty": 35, "note": "Return after stock rotation"},
                {"days_ago": 7, "direction": "in", "qty": 45, "note": "Weekly delivery cages"},
                {"days_ago": 3, "direction": "out", "qty": 20, "note": "Partial collection"},
            ]
        },
        # TechFlow Manufacturing - Mixed equipment
        {
            "customer": COMPANIES[2]["name"],
            "equipment": "stillage",
            "movements": [
                {"days_ago": 35, "direction": "in", "qty": 30, "note": "Post stillages for parts storage"},
                {"days_ago": 28, "direction": "in", "qty": 25, "note": "Additional stillages"},
                {"days_ago": 20, "direction": "out", "qty": 15, "note": "Return of empty stillages"},
                {"days_ago": 12, "direction": "in", "qty": 20, "note": "Stillages for new production line"},
                {"days_ago": 6, "direction": "out", "qty": 10, "note": "Collection after line completion"},
            ]
        },
        # GreenLeaf Wholesale - Dolly user
        {
            "customer": COMPANIES[3]["name"],
            "equipment": "dolly",
            "movements": [
                {"days_ago": 25, "direction": "in", "qty": 60, "note": "Platform dollies for warehouse"},
                {"days_ago": 18, "direction": "out", "qty": 20, "note": "Return of surplus dollies"},
                {"days_ago": 10, "direction": "in", "qty": 40, "note": "Additional dollies for peak season"},
                {"days_ago": 4, "direction": "out", "qty": 15, "note": "Collection after season end"},
            ]
        },
        # QuickServe Logistics - Multiple equipment types
        {
            "customer": COMPANIES[4]["name"],
            "equipment": "pallet",
            "movements": [
                {"days_ago": 32, "direction": "in", "qty": 70, "note": "UK pallets for distribution"},
                {"days_ago": 24, "direction": "out", "qty": 30, "note": "Return to depot"},
                {"days_ago": 16, "direction": "in", "qty": 55, "note": "Pallets for cross-docking"},
                {"days_ago": 8, "direction": "out", "qty": 25, "note": "Collection after dispatch"},
            ]
        },
        {
            "customer": COMPANIES[4]["name"],
            "equipment": "cage",
            "movements": [
                {"days_ago": 30, "direction": "in", "qty": 35, "note": "Red cages for sorting"},
                {"days_ago": 22, "direction": "out", "qty": 15, "note": "Return of damaged cages"},
                {"days_ago": 14, "direction": "in", "qty": 30, "note": "Replacement cages"},
            ]
        },
        # Premier Foods - Heavy user, over threshold
        {
            "customer": COMPANIES[5]["name"],
            "equipment": "cage",
            "movements": [
                {"days_ago": 40, "direction": "in", "qty": 80, "note": "Large delivery of green cages"},
                {"days_ago": 35, "direction": "in", "qty": 60, "note": "Additional cages for new warehouse"},
                {"days_ago": 28, "direction": "out", "qty": 20, "note": "Small return"},
                {"days_ago": 21, "direction": "in", "qty": 50, "note": "More cages delivered"},
                {"days_ago": 14, "direction": "out", "qty": 15, "note": "Partial collection"},
                {"days_ago": 7, "direction": "in", "qty": 40, "note": "Latest delivery"},
                # This customer will be over threshold
            ]
        },
    ]
    
    # Create movements
    for scenario in movement_scenarios:
        customer_name = scenario["customer"]
        equipment_type = scenario["equipment"]
        key = f"{customer_name}_{equipment_type}"
        
        if key not in balances_tracker:
            balances_tracker[key] = {
                "customer_name": customer_name,
                "equipment_type": equipment_type,
                "total_in": 0,
                "total_out": 0,
                "last_movement": None
            }
        
        for mov in scenario["movements"]:
            timestamp = datetime.now() - timedelta(days=mov["days_ago"])
            driver = random.choice(drivers)
            
            movement = DBMovement(
                customer_name=customer_name,
                equipment_type=equipment_type,
                quantity=mov["qty"],
                direction=mov["direction"],
                timestamp=timestamp,
                driver_name=driver.driver_name,
                confidence_score=0.98,
                notes=mov["note"],
                verified=True
            )
            db.add(movement)
            movements.append(movement)
            
            # Update balance tracker
            if mov["direction"] == "in":
                balances_tracker[key]["total_in"] += mov["qty"]
            else:
                balances_tracker[key]["total_out"] += mov["qty"]
            
            balances_tracker[key]["last_movement"] = timestamp
    
    db.commit()
    print(f"✓ Created {len(movements)} equipment movements")
    
    # Create balances based on movements
    print("\nCalculating and creating balances...")
    balances = []
    for key, data in balances_tracker.items():
        current_balance = data["total_in"] - data["total_out"]
        
        # Get threshold for this equipment type
        threshold = next((s["threshold"] for s in EQUIPMENT_SPECS if s["type"] == data["equipment_type"]), 20)
        
        # Determine status
        if current_balance > threshold:
            status = "over_threshold"
        elif current_balance < 0:
            status = "negative"
        else:
            status = "normal"
        
        balance = DBBalance(
            customer_name=data["customer_name"],
            equipment_type=data["equipment_type"],
            current_balance=current_balance,
            threshold=threshold,
            last_movement=data["last_movement"],
            status=status
        )
        db.add(balance)
        balances.append(balance)
        
        print(f"  {data['customer_name']} - {data['equipment_type']}: "
              f"IN={data['total_in']}, OUT={data['total_out']}, "
              f"BALANCE={current_balance}, THRESHOLD={threshold}, STATUS={status}")
    
    db.commit()
    print(f"✓ Created {len(balances)} customer balances")
    
    return movements, balances

def seed_driver_instructions(db: Session, customers, drivers, balances):
    """Seed driver instructions for over-threshold customers"""
    print("\nSeeding driver instructions...")
    instructions = []
    
    # Create instructions for customers over threshold
    over_threshold = [b for b in balances if b.status == "over_threshold"]
    
    for balance in over_threshold:
        excess = balance.current_balance - balance.threshold
        driver = random.choice(drivers)
        
        instruction = DBInstruction(
            title=f"Collect Equipment - {balance.customer_name}",
            content=f"Collect {excess} {balance.equipment_type}(s) from {balance.customer_name}. "
                   f"Current balance: {balance.current_balance}, Threshold: {balance.threshold}",
            customer_name=balance.customer_name,
            equipment_type=balance.equipment_type,
            equipment_quantity=excess,
            assigned_driver=driver.driver_name,
            status="assigned",
            priority="HIGH" if excess > balance.threshold * 0.5 else "MEDIUM",
            delivery_date=datetime.now() + timedelta(days=random.randint(1, 5)),
            special_instructions=f"Customer has {balance.current_balance} units, needs to return {excess} units",
            is_active=True
        )
        db.add(instruction)
        instructions.append(instruction)
    
    db.commit()
    print(f"✓ Created {len(instructions)} driver instructions")
    return instructions

def print_summary(customers, movements, balances, drivers, vehicles, instructions):
    """Print summary of seeded data"""
    print("\n" + "="*60)
    print("DEMO DATA SEEDING COMPLETE")
    print("="*60)
    print(f"\n📊 Summary:")
    print(f"  • Customers: {len(customers)}")
    print(f"  • Equipment Specifications: {len(EQUIPMENT_SPECS)}")
    print(f"  • Drivers: {len(drivers)}")
    print(f"  • Vehicles: {len(vehicles)}")
    print(f"  • Equipment Movements: {len(movements)}")
    print(f"  • Customer Balances: {len(balances)}")
    print(f"  • Driver Instructions: {len(instructions)}")
    
    print(f"\n📈 Balance Status:")
    normal = len([b for b in balances if b.status == "normal"])
    over = len([b for b in balances if b.status == "over_threshold"])
    negative = len([b for b in balances if b.status == "negative"])
    print(f"  • Normal: {normal}")
    print(f"  • Over Threshold: {over}")
    print(f"  • Negative: {negative}")
    
    print(f"\n✅ All equipment movements are mathematically correct!")
    print(f"✅ Balances = Total IN - Total OUT")
    print(f"\n🚀 Demo data is ready for testing!")

def main():
    print("="*60)
    print("SEEDING REALISTIC DEMO DATA")
    print("="*60)
    
    # Create tables
    create_tables()
    
    # Get database session
    db = SessionLocal()
    
    try:
        # Clear existing data
        clear_existing_data(db)
        
        # Seed data in order
        customers = seed_customers(db)
        specs = seed_equipment_specs(db)
        drivers = seed_drivers(db)
        vehicles = seed_vehicles(db, drivers)
        movements, balances = seed_movements_and_balances(db, customers, drivers)
        instructions = seed_driver_instructions(db, customers, drivers, balances)
        
        # Print summary
        print_summary(customers, movements, balances, drivers, vehicles, instructions)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()

