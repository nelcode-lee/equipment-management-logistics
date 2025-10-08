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
from ..models.database import get_db, create_tables, EquipmentMovement as DBMovement, CustomerBalance, EquipmentSpecification as DBEquipmentSpec
from ..models.schemas import (
    EquipmentMovement, EquipmentMovementResponse, CustomerBalance, ExtractionResult, 
    AlertResponse, HealthResponse, EquipmentType, EquipmentSpecification
)
from ..models.auth_models import User, UserRole
from ..services.ai_service import ai_service
from ..services.balance_service import BalanceService
from ..services.storage_service import storage_service
from ..services.auth_dependencies import get_current_active_user, require_driver, require_manager
from ..middleware.security import SecurityHeadersMiddleware, RateLimitMiddleware, RequestLoggingMiddleware

# Create FastAPI app
app = FastAPI(
    title="Equipment Tracker API",
    description="AI-powered equipment tracking system for logistics",
    version="1.0.0",
    docs_url="/docs" if settings.ENABLE_DOCS else None,
    redoc_url="/redoc" if settings.ENABLE_DOCS else None
)

# Security middleware (order matters!)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=60, burst_size=10)
app.add_middleware(SecurityHeadersMiddleware)

# CORS middleware (production-ready)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins_list(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-CSRF-Token"],
)

# Include authentication router
from .auth import router as auth_router
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
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

@app.get("/driver-instructions")
def get_driver_instructions(
    driver_name: Optional[str] = Query(None, description="Filter by driver name"),
    status: Optional[str] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_driver)
):
    """
    Get collection instructions for drivers
    """
    balance_service = BalanceService(db)
    balances = balance_service.get_all_balances("over_threshold")
    
    # Convert balances to driver instructions
    instructions = []
    for balance in balances:
        instruction = {
            "id": f"{balance.customer_name}_{balance.equipment_type}",
            "customer_name": balance.customer_name,
            "equipment_type": balance.equipment_type,
            "current_balance": balance.current_balance,
            "threshold": balance.threshold,
            "excess": balance.current_balance - balance.threshold,
            "priority": "high" if balance.current_balance > (balance.threshold * 1.5) else "medium",
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "driver_name": None,
            "delivery_date": None,
            "notes": f"Collect {balance.current_balance - balance.threshold} {balance.equipment_type}(s) - Customer has {balance.current_balance} but threshold is {balance.threshold}"
        }
        instructions.append(instruction)
    
    # Apply filters
    if driver_name:
        instructions = [i for i in instructions if i.get("driver_name") == driver_name]
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Health check endpoint
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
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
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager)
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
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager)
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
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager)
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

# Mount static files for logo serving
app.mount("/static", StaticFiles(directory="uploads"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)

