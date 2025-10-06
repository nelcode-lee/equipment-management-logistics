#!/usr/bin/env python3
"""
Seed script for Equipment Management Logistics with UK-style data
"""
import sys
import os
from datetime import datetime, timedelta
import random

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from sqlalchemy.orm import Session
from src.models.database import get_db, create_tables, EquipmentMovement, CustomerBalance
from src.models.schemas import EquipmentType, Direction

def seed_uk_data():
    """Seed the database with realistic UK logistics data"""
    
    # Create tables
    create_tables()
    
    # Get database session
    db = next(get_db())
    
    try:
        # UK Company names and locations
        uk_companies = [
            {"name": "Tesco Distribution Centre", "location": "Middlesex"},
            {"name": "Sainsbury's Logistics", "location": "Hertfordshire"},
            {"name": "ASDA Supercentres", "location": "Yorkshire"},
            {"name": "Morrisons Distribution", "location": "Bradford"},
            {"name": "Waitrose & Partners", "location": "Bracknell"},
            {"name": "Iceland Foods", "location": "Deeside"},
            {"name": "Co-op Food", "location": "Manchester"},
            {"name": "Aldi UK", "location": "Atherstone"},
            {"name": "Lidl GB", "location": "Perry Barr"},
            {"name": "Marks & Spencer", "location": "London"},
            {"name": "John Lewis Partnership", "location": "Milton Keynes"},
            {"name": "Argos Distribution", "location": "Staffordshire"},
            {"name": "Amazon Fulfilment", "location": "Dunstable"},
            {"name": "Next Retail", "location": "Leicestershire"},
            {"name": "Primark Stores", "location": "Birmingham"},
            {"name": "B&Q Warehouse", "location": "Southampton"},
            {"name": "Homebase Distribution", "location": "Essex"},
            {"name": "Wickes Building Supplies", "location": "Watford"},
            {"name": "Screwfix Direct", "location": "Yeovil"},
            {"name": "Toolstation", "location": "Bristol"}
        ]
        
        # UK Equipment types (common in UK logistics)
        equipment_types = [
            EquipmentType.PALLET,
            EquipmentType.CAGE,
            EquipmentType.DOLLY,
            EquipmentType.STILLAGE
        ]
        
        # UK Driver names
        uk_drivers = [
            "James Smith", "Michael Johnson", "Robert Williams", "David Brown",
            "Richard Jones", "Thomas Wilson", "Christopher Davies", "Daniel Taylor",
            "Matthew Evans", "Anthony Thomas", "Mark Roberts", "Donald Anderson",
            "Steven Jackson", "Paul White", "Andrew Harris", "Kenneth Martin",
            "Joshua Thompson", "Kevin Garcia", "Brian Martinez", "George Robinson",
            "Edward Clark", "Ronald Rodriguez", "Timothy Lewis", "Jason Lee",
            "Jeffrey Walker", "Ryan Hall", "Jacob Allen", "Gary Young",
            "Nicholas King", "Eric Wright", "Jonathan Lopez", "Stephen Hill",
            "Larry Scott", "Justin Green", "Brandon Adams", "Samuel Baker",
            "Gregory Nelson", "Alexander Carter", "Patrick Mitchell", "Jack Perez"
        ]
        
        # Generate movements over the last 30 days
        movements = []
        start_date = datetime.now() - timedelta(days=30)
        
        for i in range(200):  # Generate 200 movements
            company = random.choice(uk_companies)
            equipment = random.choice(equipment_types)
            direction = random.choice([Direction.IN, Direction.OUT])
            quantity = random.randint(1, 20)
            
            # Generate realistic timestamps
            random_days = random.randint(0, 30)
            random_hours = random.randint(6, 18)  # Business hours
            random_minutes = random.randint(0, 59)
            
            timestamp = start_date + timedelta(
                days=random_days,
                hours=random_hours,
                minutes=random_minutes
            )
            
            driver = random.choice(uk_drivers)
            
            # Generate realistic confidence scores
            confidence = round(random.uniform(0.75, 0.98), 2)
            
            # Generate movement ID
            movement_id = f"UK-{timestamp.strftime('%Y%m%d')}-{i+1:04d}"
            
            # Generate realistic notes
            notes_options = [
                f"Delivery to {company['location']} depot",
                f"Collection from {company['location']} site",
                "Standard delivery route",
                "Urgent collection requested",
                "Part of weekly delivery schedule",
                "Return journey from customer",
                "Equipment maintenance collection",
                "Customer requested early delivery",
                "Weather delay - rescheduled",
                "Driver: {driver} - Route completed successfully"
            ]
            
            notes = random.choice(notes_options)
            if "{driver}" in notes:
                notes = notes.format(driver=driver)
            
            movement = EquipmentMovement(
                movement_id=movement_id,
                customer_name=company["name"],
                equipment_type=equipment,
                quantity=quantity,
                direction=direction,
                timestamp=timestamp,
                driver_name=driver,
                confidence_score=confidence,
                notes=notes,
                verified=random.choice([True, False]),
                source_image_url=f"https://example.com/delivery-notes/{movement_id}.jpg"
            )
            
            movements.append(movement)
        
        # Add movements to database
        for movement in movements:
            db_movement = EquipmentMovement(
                movement_id=movement.movement_id,
                customer_name=movement.customer_name,
                equipment_type=movement.equipment_type,
                quantity=movement.quantity,
                direction=movement.direction,
                timestamp=movement.timestamp,
                driver_name=movement.driver_name,
                confidence_score=movement.confidence_score,
                notes=movement.notes,
                verified=movement.verified,
                source_image_url=movement.source_image_url
            )
            db.add(db_movement)
        
        # Commit movements
        db.commit()
        print(f"✅ Added {len(movements)} equipment movements")
        
        # Generate customer balances based on movements
        from src.services.balance_service import BalanceService
        balance_service = BalanceService(db)
        
        # Calculate balances for each customer/equipment combination
        customer_equipment_combinations = set()
        for movement in movements:
            customer_equipment_combinations.add((movement.customer_name, movement.equipment_type))
        
        print(f"📊 Calculating balances for {len(customer_equipment_combinations)} customer/equipment combinations...")
        
        # Set realistic thresholds for UK logistics
        thresholds = {
            EquipmentType.PALLET: 50,
            EquipmentType.CAGE: 30,
            EquipmentType.DOLLY: 25,
            EquipmentType.STILLAGE: 15
        }
        
        for customer_name, equipment_type in customer_equipment_combinations:
            # Get all movements for this customer/equipment combination
            customer_movements = [
                m for m in movements 
                if m.customer_name == customer_name and m.equipment_type == equipment_type
            ]
            
            # Calculate current balance
            current_balance = 0
            for movement in customer_movements:
                if movement.direction == Direction.IN:
                    current_balance += movement.quantity
                else:
                    current_balance -= movement.quantity
            
            # Set threshold
            threshold = thresholds.get(equipment_type, 20)
            
            # Determine status
            if current_balance < 0:
                status = "negative"
            elif current_balance > threshold:
                status = "over_threshold"
            else:
                status = "normal"
            
            # Get last movement
            last_movement = max(customer_movements, key=lambda x: x.timestamp) if customer_movements else None
            
            # Create balance record
            balance = CustomerBalance(
                customer_name=customer_name,
                equipment_type=equipment_type,
                current_balance=current_balance,
                threshold=threshold,
                last_movement=last_movement.timestamp if last_movement else None,
                status=status
            )
            
            # Update balance in database
            balance_service.update_customer_balance_from_balance(balance)
        
        db.commit()
        print("✅ Customer balances calculated and updated")
        
        # Print summary
        print("\n📈 UK Data Seeding Summary:")
        print(f"   • Companies: {len(uk_companies)}")
        print(f"   • Equipment Types: {len(equipment_types)}")
        print(f"   • Drivers: {len(uk_drivers)}")
        print(f"   • Movements: {len(movements)}")
        print(f"   • Customer/Equipment Combinations: {len(customer_equipment_combinations)}")
        
        # Show some examples of over-threshold customers
        over_threshold = db.query(CustomerBalance).filter(
            CustomerBalance.status == "over_threshold"
        ).all()
        
        if over_threshold:
            print(f"\n🚨 {len(over_threshold)} customers over threshold:")
            for balance in over_threshold[:5]:  # Show first 5
                excess = balance.current_balance - balance.threshold
                print(f"   • {balance.customer_name}: {balance.equipment_type} ({excess} over threshold)")
        
        print("\n🎉 UK data seeding completed successfully!")
        
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_uk_data()
