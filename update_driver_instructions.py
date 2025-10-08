#!/usr/bin/env python3
"""
Update driver instructions to focus on equipment collection and delivery
"""
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add src to Python path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

# Use live Neon database
os.environ["DATABASE_URL"] = "postgresql://neondb_owner:npg_Asb4ahlrFHg5@ep-calm-union-ab7g1jas-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

from src.models.database import SessionLocal
from src.models.database import DriverInstruction as DBInstruction

def update_driver_instructions():
    """Update driver instructions to focus on equipment collection and delivery"""
    print("📋 Updating driver instructions for equipment collection and delivery...")
    
    db = SessionLocal()
    
    # Clear existing instructions
    db.query(DBInstruction).delete()
    
    instructions = [
        {
            "title": "Equipment Collection Protocol",
            "content": "When collecting equipment from customers: 1) Verify customer identity and collection authorization, 2) Inspect equipment for damage before loading, 3) Complete collection paperwork with customer signature, 4) Take photos of equipment condition, 5) Load equipment securely on vehicle, 6) Update collection status in driver app immediately.",
            "priority": "HIGH",
            "is_active": True,
            "created_at": datetime.now() - timedelta(days=1)
        },
        {
            "title": "Equipment Delivery Procedures",
            "content": "For equipment deliveries: 1) Confirm delivery address and contact details, 2) Call customer 30 minutes before arrival, 3) Inspect equipment before unloading, 4) Obtain customer signature on delivery note, 5) Take photos of delivered equipment, 6) Update delivery status in driver app, 7) Ensure customer has proper equipment handling instructions.",
            "priority": "HIGH",
            "is_active": True,
            "created_at": datetime.now() - timedelta(days=2)
        },
        {
            "title": "Equipment Condition Assessment",
            "content": "Before collecting or delivering equipment: 1) Check for visible damage, dents, or wear, 2) Test moving parts (wheels, handles, locks), 3) Verify equipment identification numbers match paperwork, 4) Note any damage in collection/delivery forms, 5) Take clear photos of any issues, 6) Report significant damage to dispatch immediately.",
            "priority": "HIGH",
            "is_active": True,
            "created_at": datetime.now() - timedelta(days=3)
        },
        {
            "title": "Customer Equipment Handover",
            "content": "When delivering equipment to customers: 1) Explain equipment operation and safety features, 2) Provide equipment care instructions, 3) Confirm customer understands return procedures, 4) Leave contact information for support, 5) Ensure customer signs delivery confirmation, 6) Take photo of customer with delivered equipment.",
            "priority": "MEDIUM",
            "is_active": True,
            "created_at": datetime.now() - timedelta(days=4)
        },
        {
            "title": "Equipment Loading and Securing",
            "content": "Loading equipment safely: 1) Use appropriate lifting equipment for heavy items, 2) Distribute weight evenly across vehicle, 3) Secure all equipment with proper restraints, 4) Check load security before departure, 5) Re-check restraints after first 10 miles, 6) Never exceed vehicle weight limits, 7) Protect equipment from weather damage.",
            "priority": "HIGH",
            "is_active": True,
            "created_at": datetime.now() - timedelta(days=5)
        },
        {
            "title": "Collection Route Optimization",
            "content": "Planning efficient collection routes: 1) Check daily collection list in driver app, 2) Group collections by geographic area, 3) Consider customer availability windows, 4) Plan for equipment capacity constraints, 5) Allow time for equipment inspection, 6) Update ETA with customers, 7) Notify dispatch of any delays immediately.",
            "priority": "MEDIUM",
            "is_active": True,
            "created_at": datetime.now() - timedelta(days=6)
        },
        {
            "title": "Equipment Return Processing",
            "content": "When equipment is returned: 1) Verify equipment matches return authorization, 2) Inspect for damage or missing parts, 3) Grade equipment condition (A, B, C, or Damaged), 4) Complete return paperwork with customer, 5) Take photos of returned equipment, 6) Update return status in driver app, 7) Direct equipment to appropriate storage bay based on condition.",
            "priority": "HIGH",
            "is_active": True,
            "created_at": datetime.now() - timedelta(days=7)
        },
        {
            "title": "Customer Communication Standards",
            "content": "Maintaining professional communication: 1) Always wear company uniform and ID badge, 2) Greet customers politely and introduce yourself, 3) Explain collection/delivery process clearly, 4) Answer customer questions about equipment, 5) Provide accurate time estimates, 6) Follow up on any issues promptly, 7) Maintain positive company image at all times.",
            "priority": "MEDIUM",
            "is_active": True,
            "created_at": datetime.now() - timedelta(days=8)
        }
    ]
    
    for instruction_data in instructions:
        try:
            instruction = DBInstruction(**instruction_data)
            db.add(instruction)
        except Exception as e:
            print(f"❌ Error creating instruction: {e}")
    
    db.commit()
    print(f"✅ Updated {len(instructions)} driver instructions focused on equipment collection and delivery")
    db.close()

def main():
    """Main function"""
    print("🔄 Updating Driver Instructions for Equipment Operations...")
    print("=" * 60)
    
    update_driver_instructions()
    
    print("\n🎉 Driver instructions updated successfully!")
    print("\n📋 New Instructions Focus On:")
    print("   ✅ Equipment Collection Protocol")
    print("   ✅ Equipment Delivery Procedures") 
    print("   ✅ Equipment Condition Assessment")
    print("   ✅ Customer Equipment Handover")
    print("   ✅ Equipment Loading and Securing")
    print("   ✅ Collection Route Optimization")
    print("   ✅ Equipment Return Processing")
    print("   ✅ Customer Communication Standards")
    print("\n🚀 Refresh your dashboard to see the updated instructions!")

if __name__ == "__main__":
    main()
