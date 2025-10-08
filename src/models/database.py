"""
Database models and connection setup
"""
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Float, Boolean, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import uuid

from ..config import settings

# Database setup
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class EquipmentSpecification(Base):
    __tablename__ = "equipment_specifications"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    equipment_type = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)  # e.g., "Euro Pallet", "Half Pallet", "Blue Cage"
    color = Column(String, nullable=True)  # e.g., "Blue", "Red", "Green", "White"
    size = Column(String, nullable=True)  # e.g., "1200x800", "1000x600", "Standard"
    grade = Column(String, nullable=True)  # e.g., "A", "B", "C", "Food Grade", "Export Grade"
    description = Column(Text, nullable=True)
    default_threshold = Column(Integer, default=20)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class EquipmentMovement(Base):
    __tablename__ = "equipment_movements"
    
    movement_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_name = Column(String, nullable=False, index=True)
    equipment_type = Column(String, nullable=False)
    equipment_spec_id = Column(String, nullable=True)  # Reference to specific equipment specification
    equipment_name = Column(String, nullable=True)  # e.g., "Euro Pallet", "Blue Cage"
    equipment_color = Column(String, nullable=True)  # e.g., "Blue", "Red"
    equipment_size = Column(String, nullable=True)  # e.g., "1200x800", "Standard"
    equipment_grade = Column(String, nullable=True)  # e.g., "A", "Food Grade"
    quantity = Column(Integer, nullable=False)
    direction = Column(String, nullable=False)  # "in" or "out"
    timestamp = Column(DateTime, default=datetime.utcnow)
    driver_name = Column(String, nullable=True)
    confidence_score = Column(Float, nullable=False)
    notes = Column(Text, nullable=True)
    verified = Column(Boolean, default=False)
    source_image_url = Column(String, nullable=True)

class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_name = Column(String, nullable=False, unique=True, index=True)
    contact_person = Column(String, nullable=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    address = Column(String, nullable=True)
    city = Column(String, nullable=True)
    postcode = Column(String, nullable=True)
    country = Column(String, nullable=True, default="UK")
    status = Column(String, nullable=False, default="active")  # active, inactive, suspended
    credit_limit = Column(Integer, nullable=True)
    payment_terms = Column(String, nullable=True, default="30 days")
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CustomerBalance(Base):
    __tablename__ = "customer_balances"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_name = Column(String, nullable=False, index=True)
    equipment_type = Column(String, nullable=False)
    current_balance = Column(Integer, default=0)
    threshold = Column(Integer, default=20)
    last_movement = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="normal")  # "normal", "over_threshold", "negative"

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_name = Column(String, nullable=False)
    equipment_type = Column(String, nullable=False)
    current_balance = Column(Integer, nullable=False)
    threshold = Column(Integer, nullable=False)
    excess = Column(Integer, nullable=False)
    priority = Column(String, nullable=False)  # "high", "medium"
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved = Column(Boolean, default=False)

class Driver(Base):
    __tablename__ = "drivers"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    driver_name = Column(String, nullable=False, index=True)
    employee_id = Column(String, nullable=True, unique=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    license_number = Column(String, nullable=True)
    license_expiry = Column(DateTime, nullable=True)
    status = Column(String, nullable=False, default="active")  # "active", "inactive", "on_leave"
    assigned_vehicle_id = Column(String, nullable=True)  # Reference to Vehicle
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Vehicle(Base):
    __tablename__ = "vehicles"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    fleet_number = Column(String, nullable=False, unique=True, index=True)
    registration = Column(String, nullable=False, unique=True)
    make = Column(String, nullable=True)  # e.g., "Mercedes", "Ford"
    model = Column(String, nullable=True)  # e.g., "Sprinter", "Transit"
    year = Column(Integer, nullable=True)
    vehicle_type = Column(String, nullable=True)  # e.g., "Van", "Truck", "Lorry"
    capacity = Column(String, nullable=True)  # e.g., "3.5 tonne", "7.5 tonne"
    status = Column(String, nullable=False, default="available")  # "available", "in_use", "maintenance", "out_of_service"
    mot_expiry = Column(DateTime, nullable=True)
    insurance_expiry = Column(DateTime, nullable=True)
    last_service_date = Column(DateTime, nullable=True)
    next_service_due = Column(DateTime, nullable=True)
    mileage = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class DriverInstruction(Base):
    __tablename__ = "driver_instructions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    priority = Column(String, nullable=False)  # "HIGH", "MEDIUM", "LOW"
    status = Column(String, nullable=False, default="pending")  # "pending", "in_progress", "completed", "cancelled"
    assigned_driver = Column(String, nullable=True)  # Driver name
    customer_name = Column(String, nullable=True)  # Associated customer
    delivery_location = Column(String, nullable=True)  # Delivery address
    contact_phone = Column(String, nullable=True)  # Contact number
    delivery_date = Column(DateTime, nullable=True)  # When delivery should happen
    equipment_type = Column(String, nullable=True)  # Type of equipment
    equipment_quantity = Column(Integer, nullable=True)  # Quantity to deliver/collect
    special_instructions = Column(Text, nullable=True)  # Additional notes
    created_by = Column(String, nullable=True)  # Manager who created the instruction
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Create tables
def create_tables():
    Base.metadata.create_all(bind=engine)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

