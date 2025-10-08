"""
Pydantic schemas for API request/response models
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum

class EquipmentType(str, Enum):
    PALLET = "pallet"
    CAGE = "cage"
    DOLLY = "dolly"
    STILLAGE = "stillage"
    CONTAINER = "container"
    OTHER = "other"

class EquipmentSpecification(BaseModel):
    id: Optional[str] = None
    equipment_type: EquipmentType
    name: str  # e.g., "Euro Pallet", "Half Pallet", "Blue Cage"
    color: Optional[str] = None  # e.g., "Blue", "Red", "Green", "White"
    size: Optional[str] = None  # e.g., "1200x800", "1000x600", "Standard"
    grade: Optional[str] = None  # e.g., "A", "B", "C", "Food Grade", "Export Grade"
    description: Optional[str] = None
    default_threshold: int = 20
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class Direction(str, Enum):
    IN = "in"  # Equipment going TO customer
    OUT = "out"  # Equipment coming FROM customer

class EquipmentMovement(BaseModel):
    movement_id: str
    customer_name: str
    equipment_type: EquipmentType
    equipment_spec_id: Optional[str] = None  # Reference to specific equipment specification
    equipment_name: Optional[str] = None  # e.g., "Euro Pallet", "Blue Cage"
    equipment_color: Optional[str] = None  # e.g., "Blue", "Red"
    equipment_size: Optional[str] = None  # e.g., "1200x800", "Standard"
    equipment_grade: Optional[str] = None  # e.g., "A", "Food Grade"
    quantity: int
    direction: Direction
    timestamp: datetime
    driver_name: Optional[str] = None
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    notes: Optional[str] = None
    verified: bool = False
    source_image_url: Optional[str] = None

class CustomerBalance(BaseModel):
    customer_name: str
    equipment_type: EquipmentType
    current_balance: int
    threshold: int = 20
    last_movement: datetime
    status: str

class ExtractionResult(BaseModel):
    success: bool
    movements: List[EquipmentMovement]
    raw_text: Optional[str] = None
    error: Optional[str] = None

class AlertResponse(BaseModel):
    customer_name: str
    equipment_type: EquipmentType
    current_balance: int
    threshold: int
    excess: int
    last_movement: datetime
    priority: str

class EquipmentMovementResponse(BaseModel):
    movement_id: str
    customer_name: str
    equipment_type: EquipmentType
    equipment_spec_id: Optional[str] = None
    equipment_name: Optional[str] = None
    equipment_color: Optional[str] = None
    equipment_size: Optional[str] = None
    equipment_grade: Optional[str] = None
    quantity: int
    direction: Direction
    timestamp: datetime
    driver_name: Optional[str] = None
    confidence_score: float
    notes: Optional[str] = None
    verified: bool = False
    source_image_url: Optional[str] = None

class CustomerBalance(BaseModel):
    id: Optional[str] = None
    customer_name: str
    equipment_type: EquipmentType
    current_balance: int = 0
    threshold: int = 20
    last_movement: Optional[datetime] = None
    status: str = "normal"  # "normal", "over_threshold", "negative"

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    total_movements: int
    total_customers: int

class Priority(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class InstructionStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class DriverInstructionCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    priority: Priority
    assigned_driver: Optional[str] = None
    customer_name: Optional[str] = None
    delivery_location: Optional[str] = None
    contact_phone: Optional[str] = None
    delivery_date: Optional[datetime] = None
    equipment_type: Optional[EquipmentType] = None
    equipment_quantity: Optional[int] = Field(None, ge=1)
    special_instructions: Optional[str] = None

class DriverInstructionUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    priority: Optional[Priority] = None
    status: Optional[InstructionStatus] = None
    assigned_driver: Optional[str] = None
    customer_name: Optional[str] = None
    delivery_location: Optional[str] = None
    contact_phone: Optional[str] = None
    delivery_date: Optional[datetime] = None
    equipment_type: Optional[EquipmentType] = None
    equipment_quantity: Optional[int] = Field(None, ge=1)
    special_instructions: Optional[str] = None
    is_active: Optional[bool] = None

class DriverInstruction(BaseModel):
    id: str
    title: str
    content: str
    priority: Priority
    status: InstructionStatus
    assigned_driver: Optional[str] = None
    customer_name: Optional[str] = None
    delivery_location: Optional[str] = None
    contact_phone: Optional[str] = None
    delivery_date: Optional[datetime] = None
    equipment_type: Optional[EquipmentType] = None
    equipment_quantity: Optional[int] = None
    special_instructions: Optional[str] = None
    created_by: Optional[str] = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

class DriverInstructionResponse(BaseModel):
    id: str
    title: str
    content: str
    priority: Priority
    status: InstructionStatus
    assigned_driver: Optional[str] = None
    customer_name: Optional[str] = None
    delivery_location: Optional[str] = None
    contact_phone: Optional[str] = None
    delivery_date: Optional[datetime] = None
    equipment_type: Optional[EquipmentType] = None
    equipment_quantity: Optional[int] = None
    special_instructions: Optional[str] = None
    created_by: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

# Driver Management Schemas
class DriverStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ON_LEAVE = "on_leave"

class DriverCreate(BaseModel):
    driver_name: str
    employee_id: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    license_number: Optional[str] = None
    license_expiry: Optional[datetime] = None
    status: DriverStatus = DriverStatus.ACTIVE
    assigned_vehicle_id: Optional[str] = None
    notes: Optional[str] = None

class DriverUpdate(BaseModel):
    driver_name: Optional[str] = None
    employee_id: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    license_number: Optional[str] = None
    license_expiry: Optional[datetime] = None
    status: Optional[DriverStatus] = None
    assigned_vehicle_id: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None

class Driver(BaseModel):
    id: str
    driver_name: str
    employee_id: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    license_number: Optional[str] = None
    license_expiry: Optional[datetime] = None
    status: DriverStatus
    assigned_vehicle_id: Optional[str] = None
    notes: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

# Vehicle Management Schemas
class VehicleStatus(str, Enum):
    AVAILABLE = "available"
    IN_USE = "in_use"
    MAINTENANCE = "maintenance"
    OUT_OF_SERVICE = "out_of_service"

class VehicleCreate(BaseModel):
    fleet_number: str
    registration: str
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    vehicle_type: Optional[str] = None
    capacity: Optional[str] = None
    status: VehicleStatus = VehicleStatus.AVAILABLE
    mot_expiry: Optional[datetime] = None
    insurance_expiry: Optional[datetime] = None
    last_service_date: Optional[datetime] = None
    next_service_due: Optional[datetime] = None
    mileage: Optional[int] = None
    notes: Optional[str] = None

class VehicleUpdate(BaseModel):
    fleet_number: Optional[str] = None
    registration: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    vehicle_type: Optional[str] = None
    capacity: Optional[str] = None
    status: Optional[VehicleStatus] = None
    mot_expiry: Optional[datetime] = None
    insurance_expiry: Optional[datetime] = None
    last_service_date: Optional[datetime] = None
    next_service_due: Optional[datetime] = None
    mileage: Optional[int] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None

class Vehicle(BaseModel):
    id: str
    fleet_number: str
    registration: str
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    vehicle_type: Optional[str] = None
    capacity: Optional[str] = None
    status: VehicleStatus
    mot_expiry: Optional[datetime] = None
    insurance_expiry: Optional[datetime] = None
    last_service_date: Optional[datetime] = None
    next_service_due: Optional[datetime] = None
    mileage: Optional[int] = None
    notes: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

