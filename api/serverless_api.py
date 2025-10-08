"""
Serverless-compatible API for Equipment Management
"""
import os
import sys
from pathlib import Path

# Add src directory to Python path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

# Set VERCEL env var to skip file operations
os.environ["VERCEL"] = "1"

from fastapi import FastAPI, Depends, Query, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
import base64
import uuid
import os
import asyncio

# Import database and models
from src.models.database import get_db, create_tables
from src.models.database import (
    EquipmentMovement as DBMovement,
    CustomerBalance as DBBalance,
    Alert as DBAlert,
    DriverInstruction as DBInstruction,
    Customer as DBCustomer,
    EquipmentSpecification as DBEquipmentSpec,
    Driver as DBDriver,
    Vehicle as DBVehicle
)
from src.models.auth_models import User
from src.services.auth_dependencies import get_current_active_user

# Create FastAPI app
app = FastAPI(title="Equipment Management API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH", "HEAD"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600
)

# Import and include auth router
from src.api.auth import router as auth_router
app.include_router(auth_router)

@app.get("/")
async def root():
    return {"message": "Equipment Management API", "status": "ok", "version": "1.0.0"}

@app.get("/health")
def health(db: Session = Depends(get_db)):
    """Health check with basic stats"""
    total_movements = db.query(DBMovement).count()
    total_customers = db.query(DBBalance).distinct(DBBalance.customer_name).count()
    
    return {
        "status": "healthy",
        "message": "API is working",
        "total_movements": total_movements,
        "total_customers": total_customers
    }

@app.get("/movements")
def get_movements(
    customer_name: Optional[str] = Query(None),
    equipment_type: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Get equipment movements with pagination"""
    query = db.query(DBMovement)
    
    if customer_name:
        query = query.filter(DBMovement.customer_name == customer_name)
    
    if equipment_type:
        query = query.filter(DBMovement.equipment_type == equipment_type)
    
    # Get total count for pagination
    total = query.count()
    
    # Apply pagination with optimized query (uses indexes)
    movements = query.order_by(DBMovement.timestamp.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "data": [
            {
                "movement_id": m.movement_id,
                "customer_name": m.customer_name,
                "equipment_type": m.equipment_type,
                "equipment_name": m.equipment_name,
                "equipment_color": m.equipment_color,
                "equipment_size": m.equipment_size,
                "equipment_grade": m.equipment_grade,
                "quantity": m.quantity,
                "direction": m.direction,
                "timestamp": m.timestamp.isoformat() if m.timestamp else None,
                "driver_name": m.driver_name,
                "confidence_score": m.confidence_score,
                "notes": m.notes,
                "verified": m.verified,
                "source_image_url": m.source_image_url
            }
            for m in movements
        ]
    }

@app.get("/balances")
def get_balances(
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Get customer balances with pagination"""
    query = db.query(DBBalance)
    
    if status == "over_threshold":
        query = query.filter(DBBalance.current_balance > DBBalance.threshold)
    elif status == "negative":
        query = query.filter(DBBalance.current_balance < 0)
    elif status == "normal":
        query = query.filter(
            DBBalance.current_balance >= 0,
            DBBalance.current_balance <= DBBalance.threshold
        )
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    balances = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "data": [
            {
                "customer_name": b.customer_name,
                "equipment_type": b.equipment_type,
                "current_balance": b.current_balance,
                "threshold": b.threshold,
                "last_movement": b.last_movement.isoformat() if b.last_movement else None,
                "status": "over_threshold" if b.current_balance > b.threshold else "negative" if b.current_balance < 0 else "normal"
            }
            for b in balances
        ]
    }

@app.get("/alerts")
def get_alerts(
    resolved: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    """Get alerts - only shows customers who exceed their thresholds"""
    query = db.query(DBAlert)
    
    if resolved is not None:
        query = query.filter(DBAlert.resolved == resolved)
    else:
        # Default to unresolved alerts
        query = query.filter(DBAlert.resolved == False)
    
    alerts = query.order_by(DBAlert.created_at.desc()).all()
    
    return [
        {
            "id": str(a.id),
            "customer_name": a.customer_name,
            "equipment_type": a.equipment_type,
            "current_balance": a.current_balance,
            "threshold": a.threshold,
            "excess": a.excess,  # This is now correctly calculated as current_balance - threshold
            "priority": a.priority,
            "created_at": a.created_at.isoformat() if a.created_at else None,
            "resolved": a.resolved
        }
        for a in alerts
    ]

@app.get("/driver-instructions")
def get_driver_instructions(
    is_active: Optional[bool] = Query(None),
    driver_name: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get driver instructions"""
    query = db.query(DBInstruction)
    
    if is_active is not None:
        query = query.filter(DBInstruction.is_active == is_active)
    
    if driver_name:
        query = query.filter(DBInstruction.assigned_driver == driver_name)
    
    if status:
        query = query.filter(DBInstruction.status == status)
    
    instructions = query.order_by(DBInstruction.created_at.desc()).all()
    
    return [
        {
            "id": str(i.id),
            "title": i.title,
            "content": i.content,
            "customer_name": i.customer_name,
            "equipment_type": i.equipment_type,
            "equipment_quantity": i.equipment_quantity,
            "assigned_driver": i.assigned_driver,
            "status": i.status,
            "priority": i.priority,
            "delivery_date": i.delivery_date.isoformat() if i.delivery_date else None,
            "special_instructions": i.special_instructions,
            "is_active": i.is_active,
            "created_at": i.created_at.isoformat() if i.created_at else None,
            "updated_at": i.updated_at.isoformat() if i.updated_at else None
        }
        for i in instructions
    ]

@app.post("/driver-instructions")
def create_driver_instruction(
    instruction_data: dict,
    db: Session = Depends(get_db)
):
    """Create a new driver instruction"""
    try:
        instruction = DBInstruction(
            title=instruction_data.get("title"),
            content=instruction_data.get("content"),
            customer_name=instruction_data.get("customer_name"),
            equipment_type=instruction_data.get("equipment_type"),
            equipment_quantity=instruction_data.get("equipment_quantity"),
            assigned_driver=instruction_data.get("assigned_driver"),
            status=instruction_data.get("status", "pending"),
            priority=instruction_data.get("priority", "MEDIUM"),
            delivery_date=instruction_data.get("delivery_date"),
            special_instructions=instruction_data.get("special_instructions"),
            is_active=instruction_data.get("is_active", True)
        )
        
        db.add(instruction)
        db.commit()
        db.refresh(instruction)
        
        return {
            "id": str(instruction.id),
            "title": instruction.title,
            "content": instruction.content,
            "customer_name": instruction.customer_name,
            "equipment_type": instruction.equipment_type,
            "equipment_quantity": instruction.equipment_quantity,
            "assigned_driver": instruction.assigned_driver,
            "status": instruction.status,
            "priority": instruction.priority,
            "delivery_date": instruction.delivery_date.isoformat() if instruction.delivery_date else None,
            "special_instructions": instruction.special_instructions,
            "is_active": instruction.is_active,
            "created_at": instruction.created_at.isoformat() if instruction.created_at else None,
            "updated_at": instruction.updated_at.isoformat() if instruction.updated_at else None
        }
    except Exception as e:
        db.rollback()
        return {"error": f"Failed to create driver instruction: {str(e)}"}

@app.put("/driver-instructions/{instruction_id}")
def update_driver_instruction(
    instruction_id: str,
    instruction_data: dict,
    db: Session = Depends(get_db)
):
    """Update an existing driver instruction"""
    try:
        instruction = db.query(DBInstruction).filter(DBInstruction.id == instruction_id).first()
        if not instruction:
            return {"error": "Driver instruction not found"}
        
        # Update fields
        for field, value in instruction_data.items():
            if hasattr(instruction, field) and value is not None:
                setattr(instruction, field, value)
        
        instruction.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(instruction)
        
        return {
            "id": str(instruction.id),
            "title": instruction.title,
            "content": instruction.content,
            "customer_name": instruction.customer_name,
            "equipment_type": instruction.equipment_type,
            "equipment_quantity": instruction.equipment_quantity,
            "assigned_driver": instruction.assigned_driver,
            "status": instruction.status,
            "priority": instruction.priority,
            "delivery_date": instruction.delivery_date.isoformat() if instruction.delivery_date else None,
            "special_instructions": instruction.special_instructions,
            "is_active": instruction.is_active,
            "created_at": instruction.created_at.isoformat() if instruction.created_at else None,
            "updated_at": instruction.updated_at.isoformat() if instruction.updated_at else None
        }
    except Exception as e:
        db.rollback()
        return {"error": f"Failed to update driver instruction: {str(e)}"}

@app.delete("/driver-instructions/{instruction_id}")
def delete_driver_instruction(
    instruction_id: str,
    db: Session = Depends(get_db)
):
    """Delete a driver instruction"""
    try:
        instruction = db.query(DBInstruction).filter(DBInstruction.id == instruction_id).first()
        if not instruction:
            return {"error": "Driver instruction not found"}
        
        db.delete(instruction)
        db.commit()
        
        return {"message": "Driver instruction deleted successfully"}
    except Exception as e:
        db.rollback()
        return {"error": f"Failed to delete driver instruction: {str(e)}"}


@app.get("/company/logo")
def get_company_logo():
    """Get company logo - returns null for now"""
    return {"logo": None}

# Customer Management Endpoints
@app.get("/customers")
def get_customers(
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all customers with optional filtering"""
    query = db.query(DBCustomer)
    
    if status:
        query = query.filter(DBCustomer.status == status)
    
    if search:
        query = query.filter(
            DBCustomer.customer_name.ilike(f"%{search}%") |
            DBCustomer.contact_person.ilike(f"%{search}%") |
            DBCustomer.email.ilike(f"%{search}%")
        )
    
    customers = query.order_by(DBCustomer.customer_name).all()
    
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
        customer = DBCustomer(
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
        customer = db.query(DBCustomer).filter(DBCustomer.id == customer_id).first()
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
        customer = db.query(DBCustomer).filter(DBCustomer.id == customer_id).first()
        if not customer:
            return {"error": "Customer not found"}
        
        # Check if customer has any balances or movements
        balances_count = db.query(DBBalance).filter(DBBalance.customer_name == customer.customer_name).count()
        movements_count = db.query(DBMovement).filter(DBMovement.customer_name == customer.customer_name).count()
        
        if balances_count > 0 or movements_count > 0:
            return {"error": f"Cannot delete customer. Has {balances_count} balances and {movements_count} movements. Consider setting status to 'inactive' instead."}
        
        db.delete(customer)
        db.commit()
        
        return {"message": "Customer deleted successfully"}
    except Exception as e:
        db.rollback()
        return {"error": f"Failed to delete customer: {str(e)}"}

# Equipment Specifications Endpoints
@app.get("/equipment-specifications")
def get_equipment_specifications(
    equipment_type: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all equipment specifications with optional filtering"""
    query = db.query(DBEquipmentSpec)
    
    if equipment_type:
        query = query.filter(DBEquipmentSpec.equipment_type == equipment_type)
    
    if is_active is not None:
        query = query.filter(DBEquipmentSpec.is_active == is_active)
    
    specs = query.order_by(DBEquipmentSpec.equipment_type, DBEquipmentSpec.name).all()
    
    return [
        {
            "id": str(s.id),
            "equipment_type": s.equipment_type,
            "name": s.name,
            "color": s.color,
            "size": s.size,
            "grade": s.grade,
            "description": s.description,
            "default_threshold": s.default_threshold,
            "is_active": s.is_active,
            "created_at": s.created_at.isoformat() if s.created_at else None,
            "updated_at": s.updated_at.isoformat() if s.updated_at else None
        }
        for s in specs
    ]

@app.post("/equipment-specifications")
def create_equipment_specification(
    spec_data: dict,
    db: Session = Depends(get_db)
):
    """Create a new equipment specification"""
    try:
        spec = DBEquipmentSpec(
            equipment_type=spec_data.get("equipment_type"),
            name=spec_data.get("name"),
            color=spec_data.get("color"),
            size=spec_data.get("size"),
            grade=spec_data.get("grade"),
            description=spec_data.get("description"),
            default_threshold=spec_data.get("default_threshold", 20),
            is_active=spec_data.get("is_active", True)
        )
        
        db.add(spec)
        db.commit()
        db.refresh(spec)
        
        return {
            "id": str(spec.id),
            "equipment_type": spec.equipment_type,
            "name": spec.name,
            "color": spec.color,
            "size": spec.size,
            "grade": spec.grade,
            "description": spec.description,
            "default_threshold": spec.default_threshold,
            "is_active": spec.is_active,
            "created_at": spec.created_at.isoformat() if spec.created_at else None,
            "updated_at": spec.updated_at.isoformat() if spec.updated_at else None
        }
    except Exception as e:
        db.rollback()
        return {"error": f"Failed to create equipment specification: {str(e)}"}

@app.put("/equipment-specifications/{spec_id}")
def update_equipment_specification(
    spec_id: str,
    spec_data: dict,
    db: Session = Depends(get_db)
):
    """Update an existing equipment specification"""
    try:
        spec = db.query(DBEquipmentSpec).filter(DBEquipmentSpec.id == spec_id).first()
        if not spec:
            return {"error": "Equipment specification not found"}
        
        # Update fields
        for field, value in spec_data.items():
            if hasattr(spec, field) and value is not None:
                setattr(spec, field, value)
        
        spec.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(spec)
        
        return {
            "id": str(spec.id),
            "equipment_type": spec.equipment_type,
            "name": spec.name,
            "color": spec.color,
            "size": spec.size,
            "grade": spec.grade,
            "description": spec.description,
            "default_threshold": spec.default_threshold,
            "is_active": spec.is_active,
            "created_at": spec.created_at.isoformat() if spec.created_at else None,
            "updated_at": spec.updated_at.isoformat() if spec.updated_at else None
        }
    except Exception as e:
        db.rollback()
        return {"error": f"Failed to update equipment specification: {str(e)}"}

@app.delete("/equipment-specifications/{spec_id}")
def delete_equipment_specification(
    spec_id: str,
    db: Session = Depends(get_db)
):
    """Delete an equipment specification"""
    try:
        spec = db.query(DBEquipmentSpec).filter(DBEquipmentSpec.id == spec_id).first()
        if not spec:
            return {"error": "Equipment specification not found"}
        
        # Check if spec is being used in customer balances
        balances_count = db.query(DBBalance).filter(DBBalance.equipment_type == spec.equipment_type).count()
        
        if balances_count > 0:
            return {"error": f"Cannot delete specification. Used in {balances_count} customer balances. Consider setting is_active to false instead."}
        
        db.delete(spec)
        db.commit()
        
        return {"message": "Equipment specification deleted successfully"}
    except Exception as e:
        db.rollback()
        return {"error": f"Failed to delete equipment specification: {str(e)}"}

# Photo Upload Endpoints
@app.post("/photos/upload")
async def upload_photo(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload a photo and use AI to extract equipment movement data"""
    try:
        # Generate unique filename
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
        filename = f"{uuid.uuid4()}.{file_extension}"
        
        # Read file content
        content = await file.read()
        
        # Convert to base64 for storage (in production, use cloud storage)
        base64_content = base64.b64encode(content).decode('utf-8')
        
        # Use AI to extract data from the photo
        extracted_data = await extract_equipment_data_from_photo(content)
        
        # Create movement record with AI-extracted data
        movement = DBMovement(
            customer_name=extracted_data.get('customer_name', 'Unknown Customer'),
            equipment_type=extracted_data.get('equipment_type', 'container'),
            quantity=extracted_data.get('quantity', 1),
            direction=extracted_data.get('direction', 'out'),
            notes=extracted_data.get('notes', 'AI-extracted from photo'),
            confidence_score=extracted_data.get('confidence', 0.85),
            verified=False,  # Mark as unverified since it's AI-extracted
            source_image_url=f"data:image/{file_extension};base64,{base64_content}"
        )
        
        db.add(movement)
        db.commit()
        db.refresh(movement)
        
        return {
            "success": True,
            "movement_id": str(movement.movement_id),
            "message": "Photo uploaded and equipment data extracted successfully!",
            "movement": {
                "customer_name": movement.customer_name,
                "equipment_type": movement.equipment_type,
                "quantity": movement.quantity,
                "direction": movement.direction,
                "confidence": movement.confidence_score,
                "timestamp": movement.timestamp.isoformat() if movement.timestamp else None,
                "verified": movement.verified
            },
            "ai_extraction": {
                "confidence": extracted_data.get('confidence', 0.85),
                "extracted_text": extracted_data.get('extracted_text', ''),
                "processing_notes": extracted_data.get('processing_notes', '')
            }
        }
    except Exception as e:
        return {"error": f"Failed to upload photo: {str(e)}"}

async def extract_equipment_data_from_photo(image_content: bytes) -> dict:
    """Use AI to extract equipment data from photo using Anthropic Claude Vision API"""
    try:
        # Import Anthropic client
        import anthropic
        import json
        import re
        
        # Get API key from environment
        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not configured. Please set it in your environment variables.")
        
        # Initialize Anthropic client
        client = anthropic.Anthropic(api_key=api_key)
        
        # Convert image to base64 for AI processing
        base64_image = base64.b64encode(image_content).decode('utf-8')
        
        # Detect media type (basic detection)
        media_type = "image/jpeg"  # Default to JPEG
        
        # Create prompt for Claude
        prompt = """Analyze this delivery note/paperwork image and extract equipment movement information.

Look for:
1. Customer name or delivery location
2. Equipment types (containers, pallets, cages, dollies, stillages)
3. Quantities of each equipment type
4. Whether equipment is being delivered TO customer (IN) or collected FROM customer (OUT)
5. Date/time if visible
6. Any other relevant notes

Return the information in this exact JSON format:
{
    "customer_name": "string",
    "equipment_type": "container|pallet|cage|dolly|stillage|other",
    "quantity": number,
    "direction": "in|out",
    "date": "YYYY-MM-DD or null",
    "notes": "any additional context",
    "confidence": 0.0-1.0
}

If you cannot extract information confidently, set confidence below 0.7 and explain why in notes."""

        # Call Claude Vision API
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": base64_image,
                            },
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ],
                }
            ],
        )
        
        # Parse Claude's response
        response_text = message.content[0].text
        
        # Extract JSON from response (Claude might wrap it in markdown)
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            extracted_data = json.loads(json_match.group())
        else:
            raise ValueError("Could not parse JSON from Claude's response")
        
        # Return extracted data with additional metadata
        return {
            "customer_name": extracted_data.get("customer_name", "Unknown Customer"),
            "equipment_type": extracted_data.get("equipment_type", "container"),
            "quantity": extracted_data.get("quantity", 1),
            "direction": extracted_data.get("direction", "out"),
            "confidence": extracted_data.get("confidence", 0.5),
            "extracted_text": response_text,
            "processing_notes": extracted_data.get("notes", "AI extracted data from delivery note")
        }
        
    except Exception as e:
        # Fallback data if AI extraction fails
        return {
            "customer_name": "Unknown Customer",
            "equipment_type": "container",
            "quantity": 1,
            "direction": "out",
            "confidence": 0.5,
            "extracted_text": "Could not extract data from image",
            "processing_notes": f"AI extraction failed: {str(e)}"
        }

@app.get("/photos")
def get_photos(
    limit: int = Query(20),
    db: Session = Depends(get_db)
):
    """Get recent photos with movements"""
    movements = db.query(DBMovement).filter(
        DBMovement.source_image_url.isnot(None)
    ).order_by(DBMovement.timestamp.desc()).limit(limit).all()
    
    return [
        {
            "movement_id": str(m.movement_id),
            "customer_name": m.customer_name,
            "equipment_type": m.equipment_type,
            "quantity": m.quantity,
            "direction": m.direction,
            "confidence_score": m.confidence_score,
            "verified": m.verified,
            "notes": m.notes,
            "timestamp": m.timestamp.isoformat() if m.timestamp else None,
            "image_url": m.source_image_url
        }
        for m in movements
    ]

@app.get("/company/logo")
def get_company_logo():
    """Get company logo"""
    return {
        "logo": "/static/logo.png",
        "company_name": "Equipment Management Logistics",
        "version": "1.0.0"
    }

# ==================== DRIVER MANAGEMENT ENDPOINTS ====================

@app.get("/drivers")
def get_drivers(
    is_active: Optional[bool] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all drivers with optional filtering"""
    query = db.query(DBDriver)
    
    if is_active is not None:
        query = query.filter(DBDriver.is_active == is_active)
    
    if status:
        query = query.filter(DBDriver.status == status)
    
    drivers = query.order_by(DBDriver.driver_name).all()
    
    return [
        {
            "id": str(d.id),
            "driver_name": d.driver_name,
            "employee_id": d.employee_id,
            "email": d.email,
            "phone": d.phone,
            "license_number": d.license_number,
            "license_expiry": d.license_expiry.isoformat() if d.license_expiry else None,
            "status": d.status,
            "assigned_vehicle_id": d.assigned_vehicle_id,
            "notes": d.notes,
            "is_active": d.is_active,
            "created_at": d.created_at.isoformat() if d.created_at else None,
            "updated_at": d.updated_at.isoformat() if d.updated_at else None
        }
        for d in drivers
    ]

@app.post("/drivers")
def create_driver(
    driver_data: dict,
    db: Session = Depends(get_db)
):
    """Create a new driver"""
    try:
        driver = DBDriver(
            driver_name=driver_data.get("driver_name"),
            employee_id=driver_data.get("employee_id"),
            email=driver_data.get("email"),
            phone=driver_data.get("phone"),
            license_number=driver_data.get("license_number"),
            license_expiry=driver_data.get("license_expiry"),
            status=driver_data.get("status", "active"),
            assigned_vehicle_id=driver_data.get("assigned_vehicle_id"),
            notes=driver_data.get("notes")
        )
        
        db.add(driver)
        db.commit()
        db.refresh(driver)
        
        return {
            "id": str(driver.id),
            "driver_name": driver.driver_name,
            "employee_id": driver.employee_id,
            "email": driver.email,
            "phone": driver.phone,
            "license_number": driver.license_number,
            "license_expiry": driver.license_expiry.isoformat() if driver.license_expiry else None,
            "status": driver.status,
            "assigned_vehicle_id": driver.assigned_vehicle_id,
            "notes": driver.notes,
            "is_active": driver.is_active,
            "created_at": driver.created_at.isoformat() if driver.created_at else None,
            "updated_at": driver.updated_at.isoformat() if driver.updated_at else None
        }
    except Exception as e:
        db.rollback()
        return {"error": f"Failed to create driver: {str(e)}"}

@app.put("/drivers/{driver_id}")
def update_driver(
    driver_id: str,
    driver_data: dict,
    db: Session = Depends(get_db)
):
    """Update an existing driver"""
    try:
        driver = db.query(DBDriver).filter(DBDriver.id == driver_id).first()
        if not driver:
            return {"error": "Driver not found"}
        
        # Update fields
        for field, value in driver_data.items():
            if hasattr(driver, field) and value is not None:
                setattr(driver, field, value)
        
        driver.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(driver)
        
        return {
            "id": str(driver.id),
            "driver_name": driver.driver_name,
            "employee_id": driver.employee_id,
            "email": driver.email,
            "phone": driver.phone,
            "license_number": driver.license_number,
            "license_expiry": driver.license_expiry.isoformat() if driver.license_expiry else None,
            "status": driver.status,
            "assigned_vehicle_id": driver.assigned_vehicle_id,
            "notes": driver.notes,
            "is_active": driver.is_active,
            "created_at": driver.created_at.isoformat() if driver.created_at else None,
            "updated_at": driver.updated_at.isoformat() if driver.updated_at else None
        }
    except Exception as e:
        db.rollback()
        return {"error": f"Failed to update driver: {str(e)}"}

@app.delete("/drivers/{driver_id}")
def delete_driver(
    driver_id: str,
    db: Session = Depends(get_db)
):
    """Delete a driver (soft delete)"""
    try:
        driver = db.query(DBDriver).filter(DBDriver.id == driver_id).first()
        if not driver:
            return {"error": "Driver not found"}
        
        driver.is_active = False
        driver.updated_at = datetime.utcnow()
        db.commit()
        
        return {"message": "Driver deleted successfully"}
    except Exception as e:
        db.rollback()
        return {"error": f"Failed to delete driver: {str(e)}"}

# ==================== VEHICLE MANAGEMENT ENDPOINTS ====================

@app.get("/vehicles")
def get_vehicles(
    is_active: Optional[bool] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all vehicles with optional filtering"""
    query = db.query(DBVehicle)
    
    if is_active is not None:
        query = query.filter(DBVehicle.is_active == is_active)
    
    if status:
        query = query.filter(DBVehicle.status == status)
    
    vehicles = query.order_by(DBVehicle.fleet_number).all()
    
    return [
        {
            "id": str(v.id),
            "fleet_number": v.fleet_number,
            "registration": v.registration,
            "make": v.make,
            "model": v.model,
            "year": v.year,
            "vehicle_type": v.vehicle_type,
            "capacity": v.capacity,
            "status": v.status,
            "mot_expiry": v.mot_expiry.isoformat() if v.mot_expiry else None,
            "insurance_expiry": v.insurance_expiry.isoformat() if v.insurance_expiry else None,
            "last_service_date": v.last_service_date.isoformat() if v.last_service_date else None,
            "next_service_due": v.next_service_due.isoformat() if v.next_service_due else None,
            "mileage": v.mileage,
            "notes": v.notes,
            "is_active": v.is_active,
            "created_at": v.created_at.isoformat() if v.created_at else None,
            "updated_at": v.updated_at.isoformat() if v.updated_at else None
        }
        for v in vehicles
    ]

@app.post("/vehicles")
def create_vehicle(
    vehicle_data: dict,
    db: Session = Depends(get_db)
):
    """Create a new vehicle"""
    try:
        vehicle = DBVehicle(
            fleet_number=vehicle_data.get("fleet_number"),
            registration=vehicle_data.get("registration"),
            make=vehicle_data.get("make"),
            model=vehicle_data.get("model"),
            year=vehicle_data.get("year"),
            vehicle_type=vehicle_data.get("vehicle_type"),
            capacity=vehicle_data.get("capacity"),
            status=vehicle_data.get("status", "available"),
            mot_expiry=vehicle_data.get("mot_expiry"),
            insurance_expiry=vehicle_data.get("insurance_expiry"),
            last_service_date=vehicle_data.get("last_service_date"),
            next_service_due=vehicle_data.get("next_service_due"),
            mileage=vehicle_data.get("mileage"),
            notes=vehicle_data.get("notes")
        )
        
        db.add(vehicle)
        db.commit()
        db.refresh(vehicle)
        
        return {
            "id": str(vehicle.id),
            "fleet_number": vehicle.fleet_number,
            "registration": vehicle.registration,
            "make": vehicle.make,
            "model": vehicle.model,
            "year": vehicle.year,
            "vehicle_type": vehicle.vehicle_type,
            "capacity": vehicle.capacity,
            "status": vehicle.status,
            "mot_expiry": vehicle.mot_expiry.isoformat() if vehicle.mot_expiry else None,
            "insurance_expiry": vehicle.insurance_expiry.isoformat() if vehicle.insurance_expiry else None,
            "last_service_date": vehicle.last_service_date.isoformat() if vehicle.last_service_date else None,
            "next_service_due": vehicle.next_service_due.isoformat() if vehicle.next_service_due else None,
            "mileage": vehicle.mileage,
            "notes": vehicle.notes,
            "is_active": vehicle.is_active,
            "created_at": vehicle.created_at.isoformat() if vehicle.created_at else None,
            "updated_at": vehicle.updated_at.isoformat() if vehicle.updated_at else None
        }
    except Exception as e:
        db.rollback()
        return {"error": f"Failed to create vehicle: {str(e)}"}

@app.put("/vehicles/{vehicle_id}")
def update_vehicle(
    vehicle_id: str,
    vehicle_data: dict,
    db: Session = Depends(get_db)
):
    """Update an existing vehicle"""
    try:
        vehicle = db.query(DBVehicle).filter(DBVehicle.id == vehicle_id).first()
        if not vehicle:
            return {"error": "Vehicle not found"}
        
        # Update fields
        for field, value in vehicle_data.items():
            if hasattr(vehicle, field) and value is not None:
                setattr(vehicle, field, value)
        
        vehicle.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(vehicle)
        
        return {
            "id": str(vehicle.id),
            "fleet_number": vehicle.fleet_number,
            "registration": vehicle.registration,
            "make": vehicle.make,
            "model": vehicle.model,
            "year": vehicle.year,
            "vehicle_type": vehicle.vehicle_type,
            "capacity": vehicle.capacity,
            "status": vehicle.status,
            "mot_expiry": vehicle.mot_expiry.isoformat() if vehicle.mot_expiry else None,
            "insurance_expiry": vehicle.insurance_expiry.isoformat() if vehicle.insurance_expiry else None,
            "last_service_date": vehicle.last_service_date.isoformat() if vehicle.last_service_date else None,
            "next_service_due": vehicle.next_service_due.isoformat() if vehicle.next_service_due else None,
            "mileage": vehicle.mileage,
            "notes": vehicle.notes,
            "is_active": vehicle.is_active,
            "created_at": vehicle.created_at.isoformat() if vehicle.created_at else None,
            "updated_at": vehicle.updated_at.isoformat() if vehicle.updated_at else None
        }
    except Exception as e:
        db.rollback()
        return {"error": f"Failed to update vehicle: {str(e)}"}

@app.delete("/vehicles/{vehicle_id}")
def delete_vehicle(
    vehicle_id: str,
    db: Session = Depends(get_db)
):
    """Delete a vehicle (soft delete)"""
    try:
        vehicle = db.query(DBVehicle).filter(DBVehicle.id == vehicle_id).first()
        if not vehicle:
            return {"error": "Vehicle not found"}
        
        vehicle.is_active = False
        vehicle.updated_at = datetime.utcnow()
        db.commit()
        
        return {"message": "Vehicle deleted successfully"}
    except Exception as e:
        db.rollback()
        return {"error": f"Failed to delete vehicle: {str(e)}"}

# Create tables on startup
@app.on_event("startup")
async def startup():
    create_tables()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

