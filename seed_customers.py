#!/usr/bin/env python3
"""
Seed sample customers for testing
"""
import os
import sys
from pathlib import Path
from datetime import datetime

# Add src to Python path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

# Use live Neon database
os.environ["DATABASE_URL"] = "postgresql://neondb_owner:npg_Asb4ahlrFHg5@ep-calm-union-ab7g1jas-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

from src.models.database import SessionLocal, create_tables
from src.models.database import Customer as DBCustomer

def seed_customers():
    """Create sample customers"""
    print("👥 Creating sample customers...")
    
    db = SessionLocal()
    
    # Clear existing customers
    db.query(DBCustomer).delete()
    
    customers = [
        {
            "customer_name": "Global Shipping Ltd",
            "contact_person": "Sarah Johnson",
            "email": "sarah.johnson@globalshipping.com",
            "phone": "+44 20 7123 4567",
            "address": "123 Commercial Street",
            "city": "London",
            "postcode": "E1 6LT",
            "country": "UK",
            "status": "active",
            "credit_limit": 50000,
            "payment_terms": "30 days",
            "notes": "Major logistics partner, high volume customer"
        },
        {
            "customer_name": "ABC Logistics Ltd",
            "contact_person": "Mike Wilson",
            "email": "mike.wilson@abclogistics.co.uk",
            "phone": "+44 161 123 4567",
            "address": "45 Industrial Estate",
            "city": "Manchester",
            "postcode": "M12 4AB",
            "country": "UK",
            "status": "active",
            "credit_limit": 25000,
            "payment_terms": "30 days",
            "notes": "Regular customer, good payment history"
        },
        {
            "customer_name": "Metro Freight Services",
            "contact_person": "Lisa Brown",
            "email": "lisa.brown@metrofreight.com",
            "phone": "+44 121 987 6543",
            "address": "78 Warehouse Road",
            "city": "Birmingham",
            "postcode": "B5 4RT",
            "country": "UK",
            "status": "active",
            "credit_limit": 15000,
            "payment_terms": "60 days",
            "notes": "Growing business, expanding operations"
        },
        {
            "customer_name": "Coastal Logistics",
            "contact_person": "David Smith",
            "email": "david.smith@coastallogistics.co.uk",
            "phone": "+44 117 456 7890",
            "address": "12 Harbour View",
            "city": "Bristol",
            "postcode": "BS1 5AD",
            "country": "UK",
            "status": "active",
            "credit_limit": 30000,
            "payment_terms": "30 days",
            "notes": "Port-based operations, seasonal variations"
        },
        {
            "customer_name": "XYZ Transport Co",
            "contact_person": "Emma Davis",
            "email": "emma.davis@xyztransport.com",
            "phone": "+44 113 234 5678",
            "address": "90 Transport Way",
            "city": "Leeds",
            "postcode": "LS9 8XY",
            "country": "UK",
            "status": "inactive",
            "credit_limit": 10000,
            "payment_terms": "Cash on delivery",
            "notes": "Temporarily suspended due to payment issues"
        },
        {
            "customer_name": "Northern Distribution",
            "contact_person": "James Taylor",
            "email": "james.taylor@northerndist.co.uk",
            "phone": "+44 191 345 6789",
            "address": "56 Distribution Park",
            "city": "Newcastle",
            "postcode": "NE12 8CD",
            "country": "UK",
            "status": "active",
            "credit_limit": 20000,
            "payment_terms": "30 days",
            "notes": "Reliable customer, consistent orders"
        },
        {
            "customer_name": "Express Logistics",
            "contact_person": "Rachel Green",
            "email": "rachel.green@expresslogistics.com",
            "phone": "+44 141 567 8901",
            "address": "34 Speed Street",
            "city": "Glasgow",
            "postcode": "G1 2EF",
            "country": "UK",
            "status": "suspended",
            "credit_limit": 5000,
            "payment_terms": "Prepaid",
            "notes": "Suspended due to repeated late payments"
        },
        {
            "customer_name": "Midlands Haulage",
            "contact_person": "Tom Anderson",
            "email": "tom.anderson@midlandshaulage.co.uk",
            "phone": "+44 115 678 9012",
            "address": "67 Truck Lane",
            "city": "Nottingham",
            "postcode": "NG7 3GH",
            "country": "UK",
            "status": "active",
            "credit_limit": 35000,
            "payment_terms": "30 days",
            "notes": "Long-standing customer, excellent relationship"
        }
    ]
    
    for customer_data in customers:
        try:
            customer = DBCustomer(**customer_data)
            db.add(customer)
        except Exception as e:
            print(f"❌ Error creating customer {customer_data['customer_name']}: {e}")
    
    db.commit()
    print(f"✅ Created {len(customers)} customers")
    db.close()

def main():
    """Main seeding function"""
    print("🌱 Seeding Sample Customers (Live Database)...")
    print("=" * 60)
    
    # Create tables first
    print("📊 Ensuring database tables exist...")
    create_tables()
    print("✅ Database tables ready")
    
    # Seed customers
    seed_customers()
    
    print("\n🎉 Customer seeding completed!")
    print("\n👥 Customer Management Features:")
    print("   ✅ Add new customers with full contact details")
    print("   ✅ Edit existing customer information")
    print("   ✅ Delete customers (with safety checks)")
    print("   ✅ Search and filter customers")
    print("   ✅ Status management (Active/Inactive/Suspended)")
    print("   ✅ Credit limit and payment terms tracking")
    print("\n🚀 Click 'Active Customers' metric to access customer management!")

if __name__ == "__main__":
    main()
