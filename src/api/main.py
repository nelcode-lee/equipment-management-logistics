"""
Main FastAPI application for Equipment Tracking System
"""
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, List
import os
import shutil
import uuid

from ..config import settings
from ..models.database import get_db, create_tables, EquipmentMovement as DBMovement, CustomerBalance, EquipmentSpecification as DBEquipmentSpec, Customer, DriverInstruction as DBDriverInstruction, Driver as DBDriver, Vehicle as DBVehicle
from ..models.schemas import (
    EquipmentMovement, EquipmentMovementResponse, CustomerBalance, ExtractionResult, 
    AlertResponse, HealthResponse, EquipmentType, EquipmentSpecification,
    DriverInstruction, DriverInstructionCreate, DriverInstructionUpdate, DriverInstructionResponse,
    Priority, InstructionStatus,
    Driver, DriverCreate, DriverUpdate, DriverStatus,
    Vehicle, VehicleCreate, VehicleUpdate, VehicleStatus
)
from ..models.auth_models import User, UserRole
from ..services.ai_service import ai_service
from ..services.balance_service import BalanceService
from ..services.storage_service import storage_service
from ..services.auth_dependencies import get_current_active_user, require_driver, require_manager
from ..middleware.security import SecurityHeadersMiddleware, RateLimitMiddleware, RequestLoggingMiddleware
from .auth import router as auth_router

# Create FastAPI app
app = FastAPI(
    title="Equipment Tracker API",
    description="AI-powered equipment tracking system for logistics",
    version="1.0.0",
    docs_url="/docs" if settings.ENABLE_DOCS else None,
    redoc_url="/redoc" if settings.ENABLE_DOCS else None
)

# CORS middleware MUST be first (order matters!)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins_list(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH", "HEAD"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Security middleware (after CORS)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=60, burst_size=10)
app.add_middleware(SecurityHeadersMiddleware)

# Include authentication router
app.include_router(auth_router)

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    create_tables()

@app.get("/", response_model=dict)
def read_root():
    return {
        "service": "Equipment Tracker API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs"
    }

@app.post("/upload-photo", response_model=ExtractionResult)
async def upload_photo(
    file: UploadFile = File(...),
    driver_name: Optional[str] = None,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_driver)
):
    """
    Upload delivery note photo for AI processing
    """
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Read image bytes
    image_bytes = await file.read()
    
    # Upload to storage (optional)
    image_url = storage_service.upload_image(image_bytes, file.content_type)
    
    # Extract equipment data using AI
    result = ai_service.extract_equipment_from_image(image_bytes, driver_name)
    
    if result.success:
        balance_service = BalanceService(db)
        
        # Store movements and update balances
        for movement in result.movements:
            # Save to database
            db_movement = DBMovement(
                movement_id=movement.movement_id,
                customer_name=movement.customer_name,
                equipment_type=movement.equipment_type,
                quantity=movement.quantity,
                direction=movement.direction,
                timestamp=movement.timestamp,
                driver_name=movement.driver_name,
                confidence_score=movement.confidence_score,
                notes=movement.notes,
                verified=movement.verified,
                source_image_url=image_url
            )
            db.add(db_movement)
            
            # Update customer balance
            balance_service.update_customer_balance(movement)
        
        db.commit()
    
    return result

@app.get("/movements", response_model=List[EquipmentMovement])
def get_movements(
    customer_name: Optional[str] = Query(None, description="Filter by customer name"),
    equipment_type: Optional[EquipmentType] = Query(None, description="Filter by equipment type"),
    limit: int = Query(100, description="Maximum number of results"),
    db: Session = Depends(get_db)
):
    """
    Retrieve equipment movements with optional filtering
    """
    query = db.query(DBMovement)
    
    if customer_name:
        query = query.filter(DBMovement.customer_name.ilike(f"%{customer_name}%"))
    
    if equipment_type:
        query = query.filter(DBMovement.equipment_type == equipment_type)
    
    movements = query.order_by(DBMovement.timestamp.desc()).limit(limit).all()
    
    return [
        EquipmentMovement(
            movement_id=m.movement_id,
            customer_name=m.customer_name,
            equipment_type=EquipmentType(m.equipment_type.lower()),
            quantity=m.quantity,
            direction=m.direction,
            timestamp=m.timestamp,
            driver_name=m.driver_name,
            confidence_score=m.confidence_score,
            notes=m.notes,
            verified=m.verified,
            source_image_url=m.source_image_url
        )
        for m in movements
    ]

@app.get("/balances", response_model=List[CustomerBalance])
def get_balances(
    status: Optional[str] = Query(None, description="Filter by status (normal, over_threshold, negative)"),
    db: Session = Depends(get_db)
):
    """
    Get current equipment balances for all customers
    """
    balance_service = BalanceService(db)
    balances = balance_service.get_all_balances(status)
    
    return [
        CustomerBalance(
            id=b.id,
            customer_name=b.customer_name,
            equipment_type=EquipmentType(b.equipment_type.lower()),
            current_balance=b.current_balance,
            threshold=b.threshold,
            last_movement=b.last_movement,
            status=b.status
        )
        for b in balances
    ]

@app.get("/customers/{customer_name}/balance", response_model=List[CustomerBalance])
def get_customer_balance(
    customer_name: str,
    equipment_type: Optional[EquipmentType] = Query(None, description="Filter by equipment type"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get equipment balance for specific customer
    """
    balance_service = BalanceService(db)
    balances = balance_service.get_customer_balance(customer_name, equipment_type)
    
    if not balances:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    return [
        CustomerBalance(
            customer_name=b.customer_name,
            equipment_type=b.equipment_type,
            current_balance=b.current_balance,
            threshold=b.threshold,
            last_movement=b.last_movement,
            status=b.status
        )
        for b in balances
    ]

@app.post("/movements/{movement_id}/verify")
def verify_movement(
    movement_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager)
):
    """
    Mark a movement as verified by administrator
    """
    movement = db.query(DBMovement).filter(DBMovement.movement_id == movement_id).first()
    
    if not movement:
        raise HTTPException(status_code=404, detail="Movement not found")
    
    movement.verified = True
    db.commit()
    
    return {"status": "verified", "movement_id": movement_id}

@app.get("/alerts", response_model=List[AlertResponse])
def get_alerts(
    db: Session = Depends(get_db)
):
    """
    Get list of customers over threshold requiring action
    """
    balance_service = BalanceService(db)
    alerts = balance_service.get_alerts()
    
    return [
        AlertResponse(
            customer_name=a.customer_name,
            equipment_type=EquipmentType(a.equipment_type.lower()),
            current_balance=a.current_balance,
            threshold=a.threshold,
            excess=a.excess,
            last_movement=a.created_at,
            priority=a.priority
        )
        for a in alerts
    ]

@app.get("/driver-instructions/auto-generated")
def get_auto_generated_instructions(
    driver_name: Optional[str] = Query(None, description="Filter by driver name"),
    status: Optional[str] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db)
):
    """
    Get auto-generated collection instructions based on customer balances
    """
    balance_service = BalanceService(db)
    balances = balance_service.get_all_balances("over_threshold")
    
    # Convert balances to driver instructions
    instructions = []
    for balance in balances:
        instruction = {
            "id": f"auto_{balance.customer_name}_{balance.equipment_type}",
            "title": f"Collect Equipment - {balance.customer_name}",
            "content": f"Collect {balance.current_balance - balance.threshold} {balance.equipment_type}(s) from {balance.customer_name}",
            "customer_name": balance.customer_name,
            "equipment_type": balance.equipment_type,
            "equipment_quantity": balance.current_balance - balance.threshold,
            "current_balance": balance.current_balance,
            "threshold": balance.threshold,
            "excess": balance.current_balance - balance.threshold,
            "priority": "HIGH" if balance.current_balance > (balance.threshold * 1.5) else "MEDIUM",
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "assigned_driver": None,
            "delivery_date": None,
            "special_instructions": f"Customer has {balance.current_balance} but threshold is {balance.threshold}",
            "type": "auto_generated"
        }
        instructions.append(instruction)
    
    # Apply filters
    if driver_name:
        instructions = [i for i in instructions if i.get("assigned_driver") == driver_name]
    if status:
        instructions = [i for i in instructions if i.get("status") == status]
    
    return instructions

@app.put("/customers/{customer_name}/thresholds/{equipment_type}")
def update_threshold(
    customer_name: str,
    equipment_type: str,
    threshold: int = Query(..., description="New threshold value"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager)
):
    """
    Update equipment threshold for a specific customer
    """
    balance_service = BalanceService(db)
    
    # Find the balance record
    balance = db.query(CustomerBalance).filter(
        CustomerBalance.customer_name == customer_name,
        CustomerBalance.equipment_type == equipment_type
    ).first()
    
    if not balance:
        raise HTTPException(status_code=404, detail="Customer balance not found")
    
    # Update threshold
    balance.threshold = threshold
    
    # Update status based on new threshold
    if balance.current_balance > threshold:
        balance.status = "over_threshold"
    elif balance.current_balance < 0:
        balance.status = "negative"
    else:
        balance.status = "normal"
    
    db.commit()
    
    return {
        "customer_name": customer_name,
        "equipment_type": equipment_type,
        "new_threshold": threshold,
        "current_balance": balance.current_balance,
        "status": balance.status
    }

@app.get("/health", response_model=HealthResponse)
def health_check(
    db: Session = Depends(get_db)
):
    """
    Health check endpoint - No authentication required
    """
    total_movements = db.query(DBMovement).count()
    total_customers = len(set(m.customer_name for m in db.query(DBMovement).all()))
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        total_movements=total_movements,
        total_customers=total_customers
    )

# Equipment Specification management endpoints
@app.get("/equipment-specifications")
def get_equipment_specifications(
    equipment_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """
    Get all equipment specifications with optional filtering
    """
    query = db.query(DBEquipmentSpec)
    
    if equipment_type:
        query = query.filter(DBEquipmentSpec.equipment_type == equipment_type)
    
    if is_active is not None:
        query = query.filter(DBEquipmentSpec.is_active == is_active)
    
    specs = query.all()
    return [EquipmentSpecification.model_validate({
        'id': spec.id,
        'equipment_type': EquipmentType(spec.equipment_type.lower()),
        'name': spec.name,
        'color': spec.color,
        'size': spec.size,
        'grade': spec.grade,
        'description': spec.description,
        'default_threshold': spec.default_threshold,
        'is_active': spec.is_active,
        'created_at': spec.created_at,
        'updated_at': spec.updated_at
    }) for spec in specs]

@app.post("/equipment-specifications")
def create_equipment_specification(
    spec: EquipmentSpecification,
    db: Session = Depends(get_db)
):
    """
    Create a new equipment specification
    """
    db_spec = DBEquipmentSpec(**spec.model_dump())
    db.add(db_spec)
    db.commit()
    db.refresh(db_spec)
    return EquipmentSpecification.model_validate({
        'id': db_spec.id,
        'equipment_type': db_spec.equipment_type,
        'name': db_spec.name,
        'color': db_spec.color,
        'size': db_spec.size,
        'grade': db_spec.grade,
        'description': db_spec.description,
        'default_threshold': db_spec.default_threshold,
        'is_active': db_spec.is_active,
        'created_at': db_spec.created_at,
        'updated_at': db_spec.updated_at
    })

@app.put("/equipment-specifications/{spec_id}")
def update_equipment_specification(
    spec_id: str,
    spec: EquipmentSpecification,
    db: Session = Depends(get_db)
):
    """
    Update an existing equipment specification
    """
    db_spec = db.query(DBEquipmentSpec).filter(DBEquipmentSpec.id == spec_id).first()
    if not db_spec:
        raise HTTPException(status_code=404, detail="Equipment specification not found")
    
    for key, value in spec.model_dump().items():
        if value is not None:
            setattr(db_spec, key, value)
    
    db_spec.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_spec)
    return EquipmentSpecification.model_validate({
        'id': db_spec.id,
        'equipment_type': db_spec.equipment_type,
        'name': db_spec.name,
        'color': db_spec.color,
        'size': db_spec.size,
        'grade': db_spec.grade,
        'description': db_spec.description,
        'default_threshold': db_spec.default_threshold,
        'is_active': db_spec.is_active,
        'created_at': db_spec.created_at,
        'updated_at': db_spec.updated_at
    })

@app.delete("/equipment-specifications/{spec_id}")
def delete_equipment_specification(
    spec_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete an equipment specification (soft delete by setting is_active=False)
    """
    db_spec = db.query(DBEquipmentSpec).filter(DBEquipmentSpec.id == spec_id).first()
    if not db_spec:
        raise HTTPException(status_code=404, detail="Equipment specification not found")
    
    db_spec.is_active = False
    db_spec.updated_at = datetime.utcnow()
    db.commit()
    return {"message": "Equipment specification deactivated successfully"}

@app.get("/equipment-specifications/{spec_id}")
def get_equipment_specification(
    spec_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific equipment specification by ID
    """
    db_spec = db.query(DBEquipmentSpec).filter(DBEquipmentSpec.id == spec_id).first()
    if not db_spec:
        raise HTTPException(status_code=404, detail="Equipment specification not found")
    
    return EquipmentSpecification.model_validate({
        'id': db_spec.id,
        'equipment_type': db_spec.equipment_type,
        'name': db_spec.name,
        'color': db_spec.color,
        'size': db_spec.size,
        'grade': db_spec.grade,
        'description': db_spec.description,
        'default_threshold': db_spec.default_threshold,
        'is_active': db_spec.is_active,
        'created_at': db_spec.created_at,
        'updated_at': db_spec.updated_at
    })

# Logo management endpoints
LOGO_DIR = "uploads/logos"
# Skip directory creation in serverless/read-only environments
try:
    if not os.environ.get("VERCEL") and not os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
        os.makedirs(LOGO_DIR, exist_ok=True)
except (OSError, PermissionError):
    pass  # Ignore if can't create directory (serverless environment)

@app.post("/company/logo")
async def upload_company_logo(file: UploadFile = File(...)):
    """
    Upload company logo
    """
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Generate unique filename
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'png'
        filename = f"company_logo_{uuid.uuid4().hex}.{file_extension}"
        file_path = os.path.join(LOGO_DIR, filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Return logo URL
        logo_url = f"/static/logos/{filename}"
        return {"logo_url": logo_url, "message": "Logo uploaded successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload logo: {str(e)}")

@app.get("/company/logo")
async def get_company_logo():
    """
    Get current company logo
    """
    try:
        # Look for existing logo files
        logo_files = [f for f in os.listdir(LOGO_DIR) if f.startswith('company_logo_')]
        
        if logo_files:
            # Get the most recent logo
            latest_logo = max(logo_files, key=lambda x: os.path.getctime(os.path.join(LOGO_DIR, x)))
            logo_url = f"/static/logos/{latest_logo}"
            return {"logo": logo_url, "exists": True}
        else:
            return {"logo": None, "exists": False}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get logo: {str(e)}")

@app.delete("/company/logo")
async def delete_company_logo():
    """
    Delete company logo
    """
    try:
        # Find and delete all logo files
        logo_files = [f for f in os.listdir(LOGO_DIR) if f.startswith('company_logo_')]
        
        for logo_file in logo_files:
            file_path = os.path.join(LOGO_DIR, logo_file)
            if os.path.exists(file_path):
                os.remove(file_path)
        
        return {"message": "Logo deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete logo: {str(e)}")

# Customer Management Endpoints
@app.get("/customers")
def get_customers(
    status: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all customers with optional filtering"""
    query = db.query(Customer)
    
    if status:
        query = query.filter(Customer.status == status)
    
    if search:
        query = query.filter(
            Customer.customer_name.ilike(f"%{search}%") |
            Customer.contact_person.ilike(f"%{search}%") |
            Customer.email.ilike(f"%{search}%")
        )
    
    customers = query.order_by(Customer.customer_name).all()
    
    return [
        {
            "id": str(c.id),
            "customer_name": c.customer_name,
            "contact_person": c.contact_person,
            "email": c.email,
            "phone": c.phone,
            "address": c.address,
            "city": c.city,
            "postcode": c.postcode,
            "country": c.country,
            "status": c.status,
            "credit_limit": c.credit_limit,
            "payment_terms": c.payment_terms,
            "notes": c.notes,
            "created_at": c.created_at.isoformat() if c.created_at else None,
            "updated_at": c.updated_at.isoformat() if c.updated_at else None
        }
        for c in customers
    ]

@app.post("/customers")
def create_customer(
    customer_data: dict,
    db: Session = Depends(get_db)
):
    """Create a new customer"""
    try:
        customer = Customer(
            customer_name=customer_data.get("customer_name"),
            contact_person=customer_data.get("contact_person"),
            email=customer_data.get("email"),
            phone=customer_data.get("phone"),
            address=customer_data.get("address"),
            city=customer_data.get("city"),
            postcode=customer_data.get("postcode"),
            country=customer_data.get("country", "UK"),
            status=customer_data.get("status", "active"),
            credit_limit=customer_data.get("credit_limit"),
            payment_terms=customer_data.get("payment_terms", "30 days"),
            notes=customer_data.get("notes")
        )
        
        db.add(customer)
        db.commit()
        db.refresh(customer)
        
        return {
            "id": str(customer.id),
            "customer_name": customer.customer_name,
            "contact_person": customer.contact_person,
            "email": customer.email,
            "phone": customer.phone,
            "address": customer.address,
            "city": customer.city,
            "postcode": customer.postcode,
            "country": customer.country,
            "status": customer.status,
            "credit_limit": customer.credit_limit,
            "payment_terms": customer.payment_terms,
            "notes": customer.notes,
            "created_at": customer.created_at.isoformat() if customer.created_at else None,
            "updated_at": customer.updated_at.isoformat() if customer.updated_at else None
        }
    except Exception as e:
        db.rollback()
        return {"error": f"Failed to create customer: {str(e)}"}

@app.put("/customers/{customer_id}")
def update_customer(
    customer_id: str,
    customer_data: dict,
    db: Session = Depends(get_db)
):
    """Update an existing customer"""
    try:
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            return {"error": "Customer not found"}
        
        # Update fields
        for field, value in customer_data.items():
            if hasattr(customer, field) and value is not None:
                setattr(customer, field, value)
        
        customer.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(customer)
        
        return {
            "id": str(customer.id),
            "customer_name": customer.customer_name,
            "contact_person": customer.contact_person,
            "email": customer.email,
            "phone": customer.phone,
            "address": customer.address,
            "city": customer.city,
            "postcode": customer.postcode,
            "country": customer.country,
            "status": customer.status,
            "credit_limit": customer.credit_limit,
            "payment_terms": customer.payment_terms,
            "notes": customer.notes,
            "created_at": customer.created_at.isoformat() if customer.created_at else None,
            "updated_at": customer.updated_at.isoformat() if customer.updated_at else None
        }
    except Exception as e:
        db.rollback()
        return {"error": f"Failed to update customer: {str(e)}"}

@app.delete("/customers/{customer_id}")
def delete_customer(
    customer_id: str,
    db: Session = Depends(get_db)
):
    """Delete a customer"""
    try:
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            return {"error": "Customer not found"}
        
        # Check if customer has any balances or movements
        balances_count = db.query(CustomerBalance).filter(CustomerBalance.customer_name == customer.customer_name).count()
        movements_count = db.query(DBMovement).filter(DBMovement.customer_name == customer.customer_name).count()
        
        if balances_count > 0 or movements_count > 0:
            return {"error": f"Cannot delete customer. Has {balances_count} balances and {movements_count} movements. Consider setting status to 'inactive' instead."}
        
        db.delete(customer)
        db.commit()
        
        return {"message": "Customer deleted successfully"}
    except Exception as e:
        db.rollback()
        return {"error": f"Failed to delete customer: {str(e)}"}

# =============================================================================
# DRIVER INSTRUCTION ENDPOINTS
# =============================================================================

@app.post("/driver-instructions", response_model=DriverInstructionResponse)
def create_driver_instruction(
    instruction: DriverInstructionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager)
):
    """
    Create a new driver instruction (Manager only)
    """
    db_instruction = DBDriverInstruction(
        title=instruction.title,
        content=instruction.content,
        priority=instruction.priority.value,
        assigned_driver=instruction.assigned_driver,
        customer_name=instruction.customer_name,
        delivery_location=instruction.delivery_location,
        contact_phone=instruction.contact_phone,
        delivery_date=instruction.delivery_date,
        equipment_type=instruction.equipment_type.value if instruction.equipment_type else None,
        equipment_quantity=instruction.equipment_quantity,
        special_instructions=instruction.special_instructions,
        created_by=current_user.username,
        status="pending"
    )
    
    db.add(db_instruction)
    db.commit()
    db.refresh(db_instruction)
    
    return DriverInstructionResponse(
        id=db_instruction.id,
        title=db_instruction.title,
        content=db_instruction.content,
        priority=Priority(db_instruction.priority),
        status=InstructionStatus(db_instruction.status),
        assigned_driver=db_instruction.assigned_driver,
        customer_name=db_instruction.customer_name,
        delivery_location=db_instruction.delivery_location,
        contact_phone=db_instruction.contact_phone,
        delivery_date=db_instruction.delivery_date,
        equipment_type=EquipmentType(db_instruction.equipment_type) if db_instruction.equipment_type else None,
        equipment_quantity=db_instruction.equipment_quantity,
        special_instructions=db_instruction.special_instructions,
        created_by=db_instruction.created_by,
        is_active=db_instruction.is_active,
        created_at=db_instruction.created_at,
        updated_at=db_instruction.updated_at
    )

@app.get("/driver-instructions", response_model=List[DriverInstructionResponse])
def get_driver_instructions(
    driver_name: Optional[str] = Query(None, description="Filter by assigned driver"),
    status: Optional[InstructionStatus] = Query(None, description="Filter by status"),
    priority: Optional[Priority] = Query(None, description="Filter by priority"),
    is_active: Optional[bool] = Query(True, description="Filter by active status"),
    db: Session = Depends(get_db)
):
    """
    Get all driver instructions with optional filtering
    """
    query = db.query(DBDriverInstruction)
    
    if driver_name:
        query = query.filter(DBDriverInstruction.assigned_driver == driver_name)
    if status:
        query = query.filter(DBDriverInstruction.status == status.value)
    if priority:
        query = query.filter(DBDriverInstruction.priority == priority.value)
    if is_active is not None:
        query = query.filter(DBDriverInstruction.is_active == is_active)
    
    instructions = query.order_by(DBDriverInstruction.priority.desc(), DBDriverInstruction.created_at.desc()).all()
    
    return [
        DriverInstructionResponse(
            id=instruction.id,
            title=instruction.title,
            content=instruction.content,
            priority=Priority(instruction.priority),
            status=InstructionStatus(instruction.status),
            assigned_driver=instruction.assigned_driver,
            customer_name=instruction.customer_name,
            delivery_location=instruction.delivery_location,
            contact_phone=instruction.contact_phone,
            delivery_date=instruction.delivery_date,
            equipment_type=EquipmentType(instruction.equipment_type) if instruction.equipment_type else None,
            equipment_quantity=instruction.equipment_quantity,
            special_instructions=instruction.special_instructions,
            created_by=instruction.created_by,
            is_active=instruction.is_active,
            created_at=instruction.created_at,
            updated_at=instruction.updated_at
        )
        for instruction in instructions
    ]

@app.get("/driver-instructions/{instruction_id}", response_model=DriverInstructionResponse)
def get_driver_instruction(
    instruction_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific driver instruction by ID
    """
    instruction = db.query(DBDriverInstruction).filter(DBDriverInstruction.id == instruction_id).first()
    
    if not instruction:
        raise HTTPException(status_code=404, detail="Driver instruction not found")
    
    return DriverInstructionResponse(
        id=instruction.id,
        title=instruction.title,
        content=instruction.content,
        priority=Priority(instruction.priority),
        status=InstructionStatus(instruction.status),
        assigned_driver=instruction.assigned_driver,
        customer_name=instruction.customer_name,
        delivery_location=instruction.delivery_location,
        contact_phone=instruction.contact_phone,
        delivery_date=instruction.delivery_date,
        equipment_type=EquipmentType(instruction.equipment_type) if instruction.equipment_type else None,
        equipment_quantity=instruction.equipment_quantity,
        special_instructions=instruction.special_instructions,
        created_by=instruction.created_by,
        is_active=instruction.is_active,
        created_at=instruction.created_at,
        updated_at=instruction.updated_at
    )

@app.put("/driver-instructions/{instruction_id}", response_model=DriverInstructionResponse)
def update_driver_instruction(
    instruction_id: str,
    instruction_update: DriverInstructionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager)
):
    """
    Update a driver instruction (Manager only)
    """
    instruction = db.query(DBDriverInstruction).filter(DBDriverInstruction.id == instruction_id).first()
    
    if not instruction:
        raise HTTPException(status_code=404, detail="Driver instruction not found")
    
    # Update fields if provided
    if instruction_update.title is not None:
        instruction.title = instruction_update.title
    if instruction_update.content is not None:
        instruction.content = instruction_update.content
    if instruction_update.priority is not None:
        instruction.priority = instruction_update.priority.value
    if instruction_update.status is not None:
        instruction.status = instruction_update.status.value
    if instruction_update.assigned_driver is not None:
        instruction.assigned_driver = instruction_update.assigned_driver
    if instruction_update.customer_name is not None:
        instruction.customer_name = instruction_update.customer_name
    if instruction_update.delivery_location is not None:
        instruction.delivery_location = instruction_update.delivery_location
    if instruction_update.contact_phone is not None:
        instruction.contact_phone = instruction_update.contact_phone
    if instruction_update.delivery_date is not None:
        instruction.delivery_date = instruction_update.delivery_date
    if instruction_update.equipment_type is not None:
        instruction.equipment_type = instruction_update.equipment_type.value
    if instruction_update.equipment_quantity is not None:
        instruction.equipment_quantity = instruction_update.equipment_quantity
    if instruction_update.special_instructions is not None:
        instruction.special_instructions = instruction_update.special_instructions
    if instruction_update.is_active is not None:
        instruction.is_active = instruction_update.is_active
    
    db.commit()
    db.refresh(instruction)
    
    return DriverInstructionResponse(
        id=instruction.id,
        title=instruction.title,
        content=instruction.content,
        priority=Priority(instruction.priority),
        status=InstructionStatus(instruction.status),
        assigned_driver=instruction.assigned_driver,
        customer_name=instruction.customer_name,
        delivery_location=instruction.delivery_location,
        contact_phone=instruction.contact_phone,
        delivery_date=instruction.delivery_date,
        equipment_type=EquipmentType(instruction.equipment_type) if instruction.equipment_type else None,
        equipment_quantity=instruction.equipment_quantity,
        special_instructions=instruction.special_instructions,
        created_by=instruction.created_by,
        is_active=instruction.is_active,
        created_at=instruction.created_at,
        updated_at=instruction.updated_at
    )

@app.patch("/driver-instructions/{instruction_id}/status")
def update_instruction_status(
    instruction_id: str,
    status: InstructionStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update instruction status (Drivers can update their assigned instructions)
    """
    instruction = db.query(DBDriverInstruction).filter(DBDriverInstruction.id == instruction_id).first()
    
    if not instruction:
        raise HTTPException(status_code=404, detail="Driver instruction not found")
    
    # Check if driver can update this instruction
    if current_user.role == UserRole.DRIVER:
        if instruction.assigned_driver != current_user.username:
            raise HTTPException(status_code=403, detail="You can only update instructions assigned to you")
    
    instruction.status = status.value
    db.commit()
    
    return {"status": "updated", "instruction_id": instruction_id, "new_status": status.value}

@app.delete("/driver-instructions/{instruction_id}")
def delete_driver_instruction(
    instruction_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager)
):
    """
    Delete a driver instruction (Manager only)
    """
    instruction = db.query(DBDriverInstruction).filter(DBDriverInstruction.id == instruction_id).first()
    
    if not instruction:
        raise HTTPException(status_code=404, detail="Driver instruction not found")
    
    db.delete(instruction)
    db.commit()
    
    return {"status": "deleted", "instruction_id": instruction_id}

# ==================== DRIVER MANAGEMENT ENDPOINTS ====================

@app.get("/drivers", response_model=List[Driver])
def get_drivers(
    status: Optional[DriverStatus] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """
    Get all drivers with optional filtering
    """
    query = db.query(DBDriver)
    
    if status:
        query = query.filter(DBDriver.status == status.value)
    
    if is_active is not None:
        query = query.filter(DBDriver.is_active == is_active)
    
    drivers = query.order_by(DBDriver.driver_name).all()
    
    return [Driver(
        id=d.id,
        driver_name=d.driver_name,
        employee_id=d.employee_id,
        email=d.email,
        phone=d.phone,
        license_number=d.license_number,
        license_expiry=d.license_expiry,
        status=DriverStatus(d.status),
        assigned_vehicle_id=d.assigned_vehicle_id,
        notes=d.notes,
        is_active=d.is_active,
        created_at=d.created_at,
        updated_at=d.updated_at
    ) for d in drivers]

@app.post("/drivers", response_model=Driver)
def create_driver(
    driver_data: DriverCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new driver
    """
    # Check if employee_id already exists
    if driver_data.employee_id:
        existing = db.query(DBDriver).filter(DBDriver.employee_id == driver_data.employee_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Employee ID already exists")
    
    driver = DBDriver(
        driver_name=driver_data.driver_name,
        employee_id=driver_data.employee_id,
        email=driver_data.email,
        phone=driver_data.phone,
        license_number=driver_data.license_number,
        license_expiry=driver_data.license_expiry,
        status=driver_data.status.value,
        assigned_vehicle_id=driver_data.assigned_vehicle_id,
        notes=driver_data.notes
    )
    
    db.add(driver)
    db.commit()
    db.refresh(driver)
    
    return Driver(
        id=driver.id,
        driver_name=driver.driver_name,
        employee_id=driver.employee_id,
        email=driver.email,
        phone=driver.phone,
        license_number=driver.license_number,
        license_expiry=driver.license_expiry,
        status=DriverStatus(driver.status),
        assigned_vehicle_id=driver.assigned_vehicle_id,
        notes=driver.notes,
        is_active=driver.is_active,
        created_at=driver.created_at,
        updated_at=driver.updated_at
    )

@app.get("/drivers/{driver_id}", response_model=Driver)
def get_driver(
    driver_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific driver by ID
    """
    driver = db.query(DBDriver).filter(DBDriver.id == driver_id).first()
    
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    return Driver(
        id=driver.id,
        driver_name=driver.driver_name,
        employee_id=driver.employee_id,
        email=driver.email,
        phone=driver.phone,
        license_number=driver.license_number,
        license_expiry=driver.license_expiry,
        status=DriverStatus(driver.status),
        assigned_vehicle_id=driver.assigned_vehicle_id,
        notes=driver.notes,
        is_active=driver.is_active,
        created_at=driver.created_at,
        updated_at=driver.updated_at
    )

@app.put("/drivers/{driver_id}", response_model=Driver)
def update_driver(
    driver_id: str,
    driver_update: DriverUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a driver
    """
    driver = db.query(DBDriver).filter(DBDriver.id == driver_id).first()
    
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    # Update fields if provided
    if driver_update.driver_name is not None:
        driver.driver_name = driver_update.driver_name
    if driver_update.employee_id is not None:
        # Check if new employee_id already exists
        existing = db.query(DBDriver).filter(
            DBDriver.employee_id == driver_update.employee_id,
            DBDriver.id != driver_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Employee ID already exists")
        driver.employee_id = driver_update.employee_id
    if driver_update.email is not None:
        driver.email = driver_update.email
    if driver_update.phone is not None:
        driver.phone = driver_update.phone
    if driver_update.license_number is not None:
        driver.license_number = driver_update.license_number
    if driver_update.license_expiry is not None:
        driver.license_expiry = driver_update.license_expiry
    if driver_update.status is not None:
        driver.status = driver_update.status.value
    if driver_update.assigned_vehicle_id is not None:
        driver.assigned_vehicle_id = driver_update.assigned_vehicle_id
    if driver_update.notes is not None:
        driver.notes = driver_update.notes
    if driver_update.is_active is not None:
        driver.is_active = driver_update.is_active
    
    driver.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(driver)
    
    return Driver(
        id=driver.id,
        driver_name=driver.driver_name,
        employee_id=driver.employee_id,
        email=driver.email,
        phone=driver.phone,
        license_number=driver.license_number,
        license_expiry=driver.license_expiry,
        status=DriverStatus(driver.status),
        assigned_vehicle_id=driver.assigned_vehicle_id,
        notes=driver.notes,
        is_active=driver.is_active,
        created_at=driver.created_at,
        updated_at=driver.updated_at
    )

@app.delete("/drivers/{driver_id}")
def delete_driver(
    driver_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a driver (soft delete by setting is_active=False)
    """
    driver = db.query(DBDriver).filter(DBDriver.id == driver_id).first()
    
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    driver.is_active = False
    driver.updated_at = datetime.utcnow()
    db.commit()
    
    return {"status": "deleted", "driver_id": driver_id}

# ==================== VEHICLE MANAGEMENT ENDPOINTS ====================

@app.get("/vehicles", response_model=List[Vehicle])
def get_vehicles(
    status: Optional[VehicleStatus] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """
    Get all vehicles with optional filtering
    """
    query = db.query(DBVehicle)
    
    if status:
        query = query.filter(DBVehicle.status == status.value)
    
    if is_active is not None:
        query = query.filter(DBVehicle.is_active == is_active)
    
    vehicles = query.order_by(DBVehicle.fleet_number).all()
    
    return [Vehicle(
        id=v.id,
        fleet_number=v.fleet_number,
        registration=v.registration,
        make=v.make,
        model=v.model,
        year=v.year,
        vehicle_type=v.vehicle_type,
        capacity=v.capacity,
        status=VehicleStatus(v.status),
        mot_expiry=v.mot_expiry,
        insurance_expiry=v.insurance_expiry,
        last_service_date=v.last_service_date,
        next_service_due=v.next_service_due,
        mileage=v.mileage,
        notes=v.notes,
        is_active=v.is_active,
        created_at=v.created_at,
        updated_at=v.updated_at
    ) for v in vehicles]

@app.post("/vehicles", response_model=Vehicle)
def create_vehicle(
    vehicle_data: VehicleCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new vehicle
    """
    # Check if fleet_number or registration already exists
    existing_fleet = db.query(DBVehicle).filter(DBVehicle.fleet_number == vehicle_data.fleet_number).first()
    if existing_fleet:
        raise HTTPException(status_code=400, detail="Fleet number already exists")
    
    existing_reg = db.query(DBVehicle).filter(DBVehicle.registration == vehicle_data.registration).first()
    if existing_reg:
        raise HTTPException(status_code=400, detail="Registration already exists")
    
    vehicle = DBVehicle(
        fleet_number=vehicle_data.fleet_number,
        registration=vehicle_data.registration,
        make=vehicle_data.make,
        model=vehicle_data.model,
        year=vehicle_data.year,
        vehicle_type=vehicle_data.vehicle_type,
        capacity=vehicle_data.capacity,
        status=vehicle_data.status.value,
        mot_expiry=vehicle_data.mot_expiry,
        insurance_expiry=vehicle_data.insurance_expiry,
        last_service_date=vehicle_data.last_service_date,
        next_service_due=vehicle_data.next_service_due,
        mileage=vehicle_data.mileage,
        notes=vehicle_data.notes
    )
    
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    
    return Vehicle(
        id=vehicle.id,
        fleet_number=vehicle.fleet_number,
        registration=vehicle.registration,
        make=vehicle.make,
        model=vehicle.model,
        year=vehicle.year,
        vehicle_type=vehicle.vehicle_type,
        capacity=vehicle.capacity,
        status=VehicleStatus(vehicle.status),
        mot_expiry=vehicle.mot_expiry,
        insurance_expiry=vehicle.insurance_expiry,
        last_service_date=vehicle.last_service_date,
        next_service_due=vehicle.next_service_due,
        mileage=vehicle.mileage,
        notes=vehicle.notes,
        is_active=vehicle.is_active,
        created_at=vehicle.created_at,
        updated_at=vehicle.updated_at
    )

@app.get("/vehicles/{vehicle_id}", response_model=Vehicle)
def get_vehicle(
    vehicle_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific vehicle by ID
    """
    vehicle = db.query(DBVehicle).filter(DBVehicle.id == vehicle_id).first()
    
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    return Vehicle(
        id=vehicle.id,
        fleet_number=vehicle.fleet_number,
        registration=vehicle.registration,
        make=vehicle.make,
        model=vehicle.model,
        year=vehicle.year,
        vehicle_type=vehicle.vehicle_type,
        capacity=vehicle.capacity,
        status=VehicleStatus(vehicle.status),
        mot_expiry=vehicle.mot_expiry,
        insurance_expiry=vehicle.insurance_expiry,
        last_service_date=vehicle.last_service_date,
        next_service_due=vehicle.next_service_due,
        mileage=vehicle.mileage,
        notes=vehicle.notes,
        is_active=vehicle.is_active,
        created_at=vehicle.created_at,
        updated_at=vehicle.updated_at
    )

@app.put("/vehicles/{vehicle_id}", response_model=Vehicle)
def update_vehicle(
    vehicle_id: str,
    vehicle_update: VehicleUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a vehicle
    """
    vehicle = db.query(DBVehicle).filter(DBVehicle.id == vehicle_id).first()
    
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    # Update fields if provided
    if vehicle_update.fleet_number is not None:
        # Check if new fleet_number already exists
        existing = db.query(DBVehicle).filter(
            DBVehicle.fleet_number == vehicle_update.fleet_number,
            DBVehicle.id != vehicle_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Fleet number already exists")
        vehicle.fleet_number = vehicle_update.fleet_number
    if vehicle_update.registration is not None:
        # Check if new registration already exists
        existing = db.query(DBVehicle).filter(
            DBVehicle.registration == vehicle_update.registration,
            DBVehicle.id != vehicle_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Registration already exists")
        vehicle.registration = vehicle_update.registration
    if vehicle_update.make is not None:
        vehicle.make = vehicle_update.make
    if vehicle_update.model is not None:
        vehicle.model = vehicle_update.model
    if vehicle_update.year is not None:
        vehicle.year = vehicle_update.year
    if vehicle_update.vehicle_type is not None:
        vehicle.vehicle_type = vehicle_update.vehicle_type
    if vehicle_update.capacity is not None:
        vehicle.capacity = vehicle_update.capacity
    if vehicle_update.status is not None:
        vehicle.status = vehicle_update.status.value
    if vehicle_update.mot_expiry is not None:
        vehicle.mot_expiry = vehicle_update.mot_expiry
    if vehicle_update.insurance_expiry is not None:
        vehicle.insurance_expiry = vehicle_update.insurance_expiry
    if vehicle_update.last_service_date is not None:
        vehicle.last_service_date = vehicle_update.last_service_date
    if vehicle_update.next_service_due is not None:
        vehicle.next_service_due = vehicle_update.next_service_due
    if vehicle_update.mileage is not None:
        vehicle.mileage = vehicle_update.mileage
    if vehicle_update.notes is not None:
        vehicle.notes = vehicle_update.notes
    if vehicle_update.is_active is not None:
        vehicle.is_active = vehicle_update.is_active
    
    vehicle.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(vehicle)
    
    return Vehicle(
        id=vehicle.id,
        fleet_number=vehicle.fleet_number,
        registration=vehicle.registration,
        make=vehicle.make,
        model=vehicle.model,
        year=vehicle.year,
        vehicle_type=vehicle.vehicle_type,
        capacity=vehicle.capacity,
        status=VehicleStatus(vehicle.status),
        mot_expiry=vehicle.mot_expiry,
        insurance_expiry=vehicle.insurance_expiry,
        last_service_date=vehicle.last_service_date,
        next_service_due=vehicle.next_service_due,
        mileage=vehicle.mileage,
        notes=vehicle.notes,
        is_active=vehicle.is_active,
        created_at=vehicle.created_at,
        updated_at=vehicle.updated_at
    )

@app.delete("/vehicles/{vehicle_id}")
def delete_vehicle(
    vehicle_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a vehicle (soft delete by setting is_active=False)
    """
    vehicle = db.query(DBVehicle).filter(DBVehicle.id == vehicle_id).first()
    
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    vehicle.is_active = False
    vehicle.updated_at = datetime.utcnow()
    db.commit()
    
    return {"status": "deleted", "vehicle_id": vehicle_id}

# Mount static files for logo serving
app.mount("/static", StaticFiles(directory="uploads"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)

