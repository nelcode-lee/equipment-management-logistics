#!/usr/bin/env python3
"""
Apply database indexes for performance optimization
"""
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

indexes = [
    # Index for timestamp ordering (most common query pattern)
    """CREATE INDEX IF NOT EXISTS idx_movements_timestamp 
       ON equipment_movements(timestamp DESC);""",
    
    # Index for equipment_type filtering
    """CREATE INDEX IF NOT EXISTS idx_movements_equipment_type 
       ON equipment_movements(equipment_type);""",
    
    # Index for driver filtering
    """CREATE INDEX IF NOT EXISTS idx_movements_driver 
       ON equipment_movements(driver_name);""",
    
    # Composite index for common queries (customer + time)
    """CREATE INDEX IF NOT EXISTS idx_movements_customer_time 
       ON equipment_movements(customer_name, timestamp DESC);""",
    
    # Index for balance queries
    """CREATE INDEX IF NOT EXISTS idx_balances_customer_equipment 
       ON customer_balances(customer_name, equipment_type);""",
    
    # Index for instruction filtering
    """CREATE INDEX IF NOT EXISTS idx_instructions_driver 
       ON driver_instructions(assigned_driver);""",
    
    # Index for instruction status
    """CREATE INDEX IF NOT EXISTS idx_instructions_status 
       ON driver_instructions(status);""",
]

def apply_indexes():
    print("Connecting to database...")
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    print("Creating indexes for performance optimization...\n")
    
    for i, index_sql in enumerate(indexes, 1):
        try:
            print(f"[{i}/{len(indexes)}] Creating index...")
            cur.execute(index_sql)
            conn.commit()
            print(f"  ✓ Success: {index_sql.split('IF NOT EXISTS')[1].split('ON')[0].strip()}")
        except Exception as e:
            print(f"  ✗ Error: {e}")
            conn.rollback()
    
    print("\nAnalyzing tables for query planner...")
    tables = ['equipment_movements', 'customer_balances', 'driver_instructions', 'alerts', 'customers']
    for table in tables:
        try:
            cur.execute(f"ANALYZE {table};")
            conn.commit()
            print(f"  ✓ Analyzed {table}")
        except Exception as e:
            print(f"  ✗ Error analyzing {table}: {e}")
    
    print("\nVerifying indexes...")
    cur.execute("""
        SELECT 
            tablename,
            indexname
        FROM pg_indexes 
        WHERE schemaname = 'public' 
        AND indexname LIKE 'idx_%'
        ORDER BY tablename, indexname;
    """)
    
    results = cur.fetchall()
    print(f"\nTotal indexes created: {len(results)}")
    for table, index in results:
        print(f"  • {table}: {index}")
    
    cur.close()
    conn.close()
    print("\n✅ Database optimization complete!")

if __name__ == "__main__":
    apply_indexes()

