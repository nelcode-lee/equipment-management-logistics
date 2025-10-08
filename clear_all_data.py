#!/usr/bin/env python3
"""
Clear all seed data from the database for fresh testing
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.models.database import Base, engine
from src.config import settings

def clear_all_data():
    """Clear all data from the database"""
    try:
        # Get database URL
        database_url = settings.DATABASE_URL
        print(f"Connecting to database: {database_url}")
        
        # Create session
        Session = sessionmaker(bind=engine)
        session = Session()
        
        print("Clearing all data from database...")
        
        # List of all tables to clear (in dependency order)
        tables_to_clear = [
            'equipment_movements',
            'customer_balances', 
            'alerts',
            'driver_instructions',
            'customers',
            'equipment_specifications',
            'users'
        ]
        
        # Clear each table
        for table in tables_to_clear:
            try:
                result = session.execute(text(f"DELETE FROM {table}"))
                deleted_count = result.rowcount
                print(f"✓ Cleared {deleted_count} records from {table}")
            except Exception as e:
                print(f"⚠ Could not clear {table}: {e}")
        
        # Reset auto-increment sequences (for PostgreSQL)
        try:
            session.execute(text("ALTER SEQUENCE IF EXISTS users_id_seq RESTART WITH 1"))
            session.execute(text("ALTER SEQUENCE IF EXISTS customers_id_seq RESTART WITH 1"))
            session.execute(text("ALTER SEQUENCE IF EXISTS equipment_specifications_id_seq RESTART WITH 1"))
            session.execute(text("ALTER SEQUENCE IF EXISTS customer_balances_id_seq RESTART WITH 1"))
            session.execute(text("ALTER SEQUENCE IF EXISTS equipment_movements_id_seq RESTART WITH 1"))
            session.execute(text("ALTER SEQUENCE IF EXISTS alerts_id_seq RESTART WITH 1"))
            session.execute(text("ALTER SEQUENCE IF EXISTS driver_instructions_id_seq RESTART WITH 1"))
            print("✓ Reset auto-increment sequences")
        except Exception as e:
            print(f"⚠ Could not reset sequences: {e}")
        
        # Commit changes
        session.commit()
        print("\n✅ Database cleared successfully!")
        print("All seed data has been removed. Ready for fresh testing.")
        
        # Show current record counts
        print("\nCurrent record counts:")
        for table in tables_to_clear:
            try:
                result = session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                print(f"  {table}: {count} records")
            except Exception as e:
                print(f"  {table}: Error - {e}")
        
        session.close()
        
    except Exception as e:
        print(f"❌ Error clearing database: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🗑️  CLEARING ALL SEED DATA")
    print("=" * 50)
    
    success = clear_all_data()
    
    if success:
        print("\n🎉 Database is now clean and ready for testing!")
        print("\nNext steps:")
        print("1. Test the empty dashboard")
        print("2. Add some test data manually")
        print("3. Test the AI photo extraction")
        print("4. Test all dashboard features")
    else:
        print("\n❌ Failed to clear database. Please check the error messages above.")
        sys.exit(1)
