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

