#!/usr/bin/env python3
"""
Seed equipment specifications with UK-style data
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.models.database import get_db, create_tables, EquipmentSpecification as DBEquipmentSpec
from src.models.schemas import EquipmentSpecification, EquipmentType
from datetime import datetime

def seed_equipment_specifications():
    """Seed the database with sample equipment specifications"""
    
    # Create tables
    create_tables()
    
    # Get database session
    db = next(get_db())
    
    try:
        # Sample equipment specifications
        equipment_specs = [
            # Pallets
            EquipmentSpecification(
                equipment_type=EquipmentType.PALLET,
                name="Euro Pallet",
                color="Blue",
                size="1200x800",
                grade="A",
                description="Standard Euro pallet, blue color, grade A quality",
                default_threshold=50,
                is_active=True
            ),
            EquipmentSpecification(
                equipment_type=EquipmentType.PALLET,
                name="Half Pallet",
                color="Blue",
                size="600x800",
                grade="A",
                description="Half-size Euro pallet, blue color",
                default_threshold=30,
                is_active=True
            ),
            EquipmentSpecification(
                equipment_type=EquipmentType.PALLET,
                name="Export Pallet",
                color="Red",
                size="1200x800",
                grade="Export Grade",
                description="Export quality pallet, red color, ISPM 15 compliant",
                default_threshold=25,
                is_active=True
            ),
            EquipmentSpecification(
                equipment_type=EquipmentType.PALLET,
                name="Food Grade Pallet",
                color="White",
                size="1200x800",
                grade="Food Grade",
                description="Food-safe pallet, white color, HACCP compliant",
                default_threshold=40,
                is_active=True
            ),
            EquipmentSpecification(
                equipment_type=EquipmentType.PALLET,
                name="Economy Pallet",
                color="Brown",
                size="1200x800",
                grade="C",
                description="Economy pallet, brown color, basic quality",
                default_threshold=60,
                is_active=True
            ),
            
            # Cages
            EquipmentSpecification(
                equipment_type=EquipmentType.CAGE,
                name="Standard Cage",
                color="Blue",
                size="1200x800",
                grade="Standard",
                description="Standard transport cage, blue color",
                default_threshold=30,
                is_active=True
            ),
            EquipmentSpecification(
                equipment_type=EquipmentType.CAGE,
                name="Large Cage",
                color="Blue",
                size="1500x1000",
                grade="Standard",
                description="Large transport cage, blue color",
                default_threshold=20,
                is_active=True
            ),
            EquipmentSpecification(
                equipment_type=EquipmentType.CAGE,
                name="Small Cage",
                color="Green",
                size="800x600",
                grade="Standard",
                description="Small transport cage, green color",
                default_threshold=40,
                is_active=True
            ),
            EquipmentSpecification(
                equipment_type=EquipmentType.CAGE,
                name="Heavy Duty Cage",
                color="Red",
                size="1200x800",
                grade="Heavy Duty",
                description="Heavy duty transport cage, red color",
                default_threshold=15,
                is_active=True
            ),
            
            # Dollies
            EquipmentSpecification(
                equipment_type=EquipmentType.DOLLY,
                name="Standard Dolly",
                color="Blue",
                size="Standard",
                grade="Standard",
                description="Standard transport dolly, blue color",
                default_threshold=25,
                is_active=True
            ),
            EquipmentSpecification(
                equipment_type=EquipmentType.DOLLY,
                name="Heavy Duty Dolly",
                color="Red",
                size="Heavy Duty",
                grade="Heavy Duty",
                description="Heavy duty transport dolly, red color",
                default_threshold=15,
                is_active=True
            ),
            EquipmentSpecification(
                equipment_type=EquipmentType.DOLLY,
                name="Light Duty Dolly",
                color="Green",
                size="Light Duty",
                grade="Light Duty",
                description="Light duty transport dolly, green color",
                default_threshold=35,
                is_active=True
            ),
            EquipmentSpecification(
                equipment_type=EquipmentType.DOLLY,
                name="4-Wheel Dolly",
                color="Blue",
                size="4-Wheel",
                grade="Standard",
                description="4-wheel transport dolly, blue color",
                default_threshold=20,
                is_active=True
            ),
            
            # Stillages
            EquipmentSpecification(
                equipment_type=EquipmentType.STILLAGE,
                name="Standard Stillage",
                color="Blue",
                size="1200x800",
                grade="Standard",
                description="Standard transport stillage, blue color",
                default_threshold=15,
                is_active=True
            ),
            EquipmentSpecification(
                equipment_type=EquipmentType.STILLAGE,
                name="Large Stillage",
                color="Blue",
                size="1500x1000",
                grade="Standard",
                description="Large transport stillage, blue color",
                default_threshold=10,
                is_active=True
            ),
            EquipmentSpecification(
                equipment_type=EquipmentType.STILLAGE,
                name="Food Grade Stillage",
                color="White",
                size="1200x800",
                grade="Food Grade",
                description="Food-safe stillage, white color, HACCP compliant",
                default_threshold=12,
                is_active=True
            ),
            EquipmentSpecification(
                equipment_type=EquipmentType.STILLAGE,
                name="Export Stillage",
                color="Red",
                size="1200x800",
                grade="Export Grade",
                description="Export quality stillage, red color, ISPM 15 compliant",
                default_threshold=8,
                is_active=True
            ),
            
            # Other equipment
            EquipmentSpecification(
                equipment_type=EquipmentType.OTHER,
                name="Custom Container",
                color="Various",
                size="Custom",
                grade="Standard",
                description="Custom transport container, various colors",
                default_threshold=5,
                is_active=True
            ),
            EquipmentSpecification(
                equipment_type=EquipmentType.OTHER,
                name="Specialist Equipment",
                color="Yellow",
                size="Various",
                grade="Specialist",
                description="Specialist transport equipment, yellow color",
                default_threshold=3,
                is_active=True
            )
        ]
        
        # Add specifications to database
        for spec in equipment_specs:
            db_spec = DBEquipmentSpec(**spec.dict())
            db.add(db_spec)
        
        db.commit()
        print(f"✅ Successfully seeded {len(equipment_specs)} equipment specifications")
        
        # Print summary
        print("\n📊 Equipment Specifications Summary:")
        print("=" * 50)
        
        for equipment_type in EquipmentType:
            count = db.query(DBEquipmentSpec).filter(
                DBEquipmentSpec.equipment_type == equipment_type.value,
                DBEquipmentSpec.is_active == True
            ).count()
            print(f"{equipment_type.value.upper()}: {count} specifications")
        
        print("\n🎯 Sample Equipment Types:")
        print("- Euro Pallets (Blue, Red, White, Brown)")
        print("- Transport Cages (Blue, Green, Red)")
        print("- Transport Dollies (Blue, Red, Green)")
        print("- Transport Stillages (Blue, White, Red)")
        print("- Custom Equipment (Various)")
        
        print("\n📋 Equipment Attributes:")
        print("- Colors: Blue, Red, Green, White, Brown, Yellow")
        print("- Sizes: 1200x800, 600x800, 1500x1000, 800x600, Custom")
        print("- Grades: A, B, C, Food Grade, Export Grade, Heavy Duty")
        print("- Thresholds: 3-60 units (based on equipment type and grade)")
        
    except Exception as e:
        print(f"❌ Error seeding equipment specifications: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_equipment_specifications()
