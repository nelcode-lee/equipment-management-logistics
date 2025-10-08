-- Database Indexes for Performance Optimization
-- Run these on your Neon PostgreSQL database to improve query performance with 100s of movements

-- Index for timestamp ordering (most common query pattern)
CREATE INDEX IF NOT EXISTS idx_movements_timestamp 
ON equipment_movements(timestamp DESC);

-- Index for equipment_type filtering
CREATE INDEX IF NOT EXISTS idx_movements_equipment_type 
ON equipment_movements(equipment_type);

-- Index for driver filtering
CREATE INDEX IF NOT EXISTS idx_movements_driver 
ON equipment_movements(driver_name);

-- Composite index for common queries (customer + time)
CREATE INDEX IF NOT EXISTS idx_movements_customer_time 
ON equipment_movements(customer_name, timestamp DESC);

-- Index for balance queries
CREATE INDEX IF NOT EXISTS idx_balances_customer_equipment 
ON customer_balances(customer_name, equipment_type);

-- Index for active status filtering
CREATE INDEX IF NOT EXISTS idx_balances_status 
ON customer_balances(status);

-- Index for driver instructions filtering
CREATE INDEX IF NOT EXISTS idx_instructions_driver 
ON driver_instructions(assigned_driver) 
WHERE is_active = true;

-- Index for instruction status
CREATE INDEX IF NOT EXISTS idx_instructions_status 
ON driver_instructions(status) 
WHERE is_active = true;

-- Index for alert queries
CREATE INDEX IF NOT EXISTS idx_alerts_resolved 
ON alerts(resolved, created_at DESC);

-- Index for customer status
CREATE INDEX IF NOT EXISTS idx_customers_status 
ON customers(status);

-- Analyze tables after index creation for query planner
ANALYZE equipment_movements;
ANALYZE customer_balances;
ANALYZE driver_instructions;
ANALYZE alerts;
ANALYZE customers;

-- Verify indexes were created
SELECT 
    tablename,
    indexname,
    indexdef
FROM pg_indexes 
WHERE schemaname = 'public' 
AND tablename IN ('equipment_movements', 'customer_balances', 'driver_instructions', 'alerts', 'customers')
ORDER BY tablename, indexname;
