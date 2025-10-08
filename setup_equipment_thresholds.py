#!/usr/bin/env python3
"""
Quick setup script to add equipment specifications and customer thresholds
"""

import os
import sys
from sqlalchemy.orm import sessionmaker

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.models.database import engine, EquipmentSpecification, Customer, CustomerBalance
from src.config import settings

def setup_equipment_and_thresholds():
    """Set up basic equipment specifications and customer thresholds"""
    try:
        # Create session
        Session = sessionmaker(bind=engine)
        session = Session()
        
        print("🔧 Setting up equipment specifications and thresholds...")
        
        # 1. Add basic equipment specifications
        equipment_specs = [
            {
                "equipment_type": "container",
                "name": "Blue Standard Container",
                "color": "Blue",
                "size": "Standard",
                "grade": "A",
                "description": "Standard blue container for general use",
                "default_threshold": 10
            },
            {
                "equipment_type": "pallet",
                "name": "Euro Pallet",
                "color": "Brown",
                "size": "Euro",
                "grade": "A",
                "description": "Standard Euro pallet",
                "default_threshold": 20
            },
            {
                "equipment_type": "cage",
                "name": "Large Silver Cage",
                "color": "Silver",
                "size": "Large",
                "grade": "A",
                "description": "Large silver cage for heavy items",
                "default_threshold": 5
            },
            {
                "equipment_type": "dolly",
                "name": "Standard Black Dolly",
                "color": "Black",
                "size": "Standard",
                "grade": "A",
                "description": "Standard black dolly",
                "default_threshold": 15
            },
            {
                "equipment_type": "stillage",
                "name": "Medium Green Stillage",
                "color": "Green",
                "size": "Medium",
                "grade": "A",
                "description": "Medium green stillage",
                "default_threshold": 8
            }
        ]
        
        print("Adding equipment specifications...")
        for spec in equipment_specs:
            existing = session.query(EquipmentSpecification).filter_by(
                equipment_type=spec["equipment_type"]
            ).first()
            
            if not existing:
                equipment = EquipmentSpecification(**spec)
                session.add(equipment)
                print(f"✓ Added {spec['equipment_type']} specification")
            else:
                print(f"⚠ {spec['equipment_type']} already exists")
        
        # 2. Add some sample customers
        customers = [
            {
                "customer_name": "Tesco Stores",
                "contact_person": "John Smith",
                "email": "john.smith@tesco.com",
                "phone": "+44 20 1234 5678",
                "address": "Tesco House, Shire Park, Welwyn Garden City",
                "city": "Welwyn Garden City",
                "postcode": "AL7 1GA",
                "country": "UK",
                "status": "active",
                "credit_limit": 50000,
                "payment_terms": "30 days"
            },
            {
                "customer_name": "Sainsbury's",
                "contact_person": "Sarah Johnson",
                "email": "sarah.johnson@sainsburys.co.uk",
                "phone": "+44 20 2345 6789",
                "address": "33 Holborn, London",
                "city": "London",
                "postcode": "EC1N 2HT",
                "country": "UK",
                "status": "active",
                "credit_limit": 75000,
                "payment_terms": "30 days"
            },
            {
                "customer_name": "ASDA Stores",
                "contact_person": "Mike Brown",
                "email": "mike.brown@asda.co.uk",
                "phone": "+44 113 243 5432",
                "address": "ASDA House, Great Wilson Street, Leeds",
                "city": "Leeds",
                "postcode": "LS11 5AD",
                "country": "UK",
                "status": "active",
                "credit_limit": 60000,
                "payment_terms": "30 days"
            }
        ]
        
        print("\nAdding sample customers...")
        for customer_data in customers:
            existing = session.query(Customer).filter_by(
                customer_name=customer_data["customer_name"]
            ).first()
            
            if not existing:
                customer = Customer(**customer_data)
                session.add(customer)
                print(f"✓ Added {customer_data['customer_name']}")
            else:
                print(f"⚠ {customer_data['customer_name']} already exists")
        
        # 3. Add customer balances with thresholds
        print("\nAdding customer balances with thresholds...")
        
        # Get the customers we just added
        tesco = session.query(Customer).filter_by(customer_name="Tesco Stores").first()
        sainsburys = session.query(Customer).filter_by(customer_name="Sainsbury's").first()
        asda = session.query(Customer).filter_by(customer_name="ASDA Stores").first()
        
        if tesco and sainsburys and asda:
            # Add balances for each customer and equipment type
            balance_data = [
                # Tesco
                {"customer_name": "Tesco Stores", "equipment_type": "container", "current_balance": 3, "threshold": 10},
                {"customer_name": "Tesco Stores", "equipment_type": "pallet", "current_balance": 8, "threshold": 20},
                {"customer_name": "Tesco Stores", "equipment_type": "cage", "current_balance": 2, "threshold": 5},
                
                # Sainsbury's
                {"customer_name": "Sainsbury's", "equipment_type": "container", "current_balance": 12, "threshold": 10},  # Over threshold
                {"customer_name": "Sainsbury's", "equipment_type": "pallet", "current_balance": 15, "threshold": 20},
                {"customer_name": "Sainsbury's", "equipment_type": "dolly", "current_balance": 6, "threshold": 15},
                
                # ASDA
                {"customer_name": "ASDA Stores", "equipment_type": "container", "current_balance": 7, "threshold": 10},
                {"customer_name": "ASDA Stores", "equipment_type": "stillage", "current_balance": 10, "threshold": 8},  # Over threshold
                {"customer_name": "ASDA Stores", "equipment_type": "cage", "current_balance": 1, "threshold": 5},
            ]
            
            for balance_info in balance_data:
                existing = session.query(CustomerBalance).filter_by(
                    customer_name=balance_info["customer_name"],
                    equipment_type=balance_info["equipment_type"]
                ).first()
                
                if not existing:
                    # Determine status
                    current = balance_info["current_balance"]
                    threshold = balance_info["threshold"]
                    
                    if current > threshold:
                        status = "over_threshold"
                    elif current < 0:
                        status = "negative"
                    else:
                        status = "normal"
                    
                    balance = CustomerBalance(
                        customer_name=balance_info["customer_name"],
                        equipment_type=balance_info["equipment_type"],
                        current_balance=current,
                        threshold=threshold,
                        status=status
                    )
                    session.add(balance)
                    print(f"✓ Added {balance_info['customer_name']} - {balance_info['equipment_type']} (Status: {status})")
                else:
                    print(f"⚠ {balance_info['customer_name']} - {balance_info['equipment_type']} already exists")
        
        # Commit all changes
        session.commit()
        print("\n✅ Setup completed successfully!")
        
        # Show summary
        print("\n📊 Summary:")
        print(f"Equipment specifications: {session.query(EquipmentSpecification).count()}")
        print(f"Customers: {session.query(Customer).count()}")
        print(f"Customer balances: {session.query(CustomerBalance).count()}")
        
        # Show over-threshold items
        over_threshold = session.query(CustomerBalance).filter_by(status="over_threshold").all()
        if over_threshold:
            print(f"\n⚠️  Over-threshold items that will generate alerts:")
            for item in over_threshold:
                excess = item.current_balance - item.threshold
                print(f"  - {item.customer_name}: {item.equipment_type} ({item.current_balance}/{item.threshold}, +{excess})")
        
        session.close()
        return True
        
    except Exception as e:
        print(f"❌ Error setting up equipment and thresholds: {e}")
        return False

if __name__ == "__main__":
    print("🔧 EQUIPMENT & THRESHOLD SETUP")
    print("=" * 50)
    
    success = setup_equipment_and_thresholds()
    
    if success:
        print("\n🎉 Setup complete! You can now:")
        print("1. View the dashboard to see the data")
        print("2. Check the Equipment Thresholds tab in Settings")
        print("3. See alerts for over-threshold items")
        print("4. Test the AI photo extraction")
    else:
        print("\n❌ Setup failed. Please check the error messages above.")
        sys.exit(1)
