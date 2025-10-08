#!/usr/bin/env python3
"""
Check equipment types in database
"""
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.models.database import SessionLocal, CustomerBalance
from src.models.schemas import EquipmentType

def check_equipment_types():
    """Check equipment types in database"""
    print("🔍 Checking Equipment Types in Database")
    print("=" * 40)
    
    try:
        db = SessionLocal()
        
        # Get unique equipment types
        equipment_types = db.query(CustomerBalance.equipment_type).distinct().all()
        print(f"✅ Found {len(equipment_types)} unique equipment types:")
        
        for eq_type in equipment_types:
            print(f"   - '{eq_type[0]}'")
        
        # Check if they match the enum
        print(f"\n📋 EquipmentType enum values:")
        for eq_type in EquipmentType:
            print(f"   - {eq_type.value}")
        
        # Test conversion
        print(f"\n🔄 Testing conversion:")
        for eq_type in equipment_types:
            try:
                converted = EquipmentType(eq_type[0])
                print(f"   ✅ '{eq_type[0]}' -> {converted}")
            except ValueError as e:
                print(f"   ❌ '{eq_type[0]}' -> Error: {e}")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_equipment_types()
