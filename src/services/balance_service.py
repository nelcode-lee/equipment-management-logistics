"""
Service for managing customer equipment balances
"""
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from ..models.database import CustomerBalance, EquipmentMovement, Alert
from ..models.schemas import Direction, EquipmentType
from ..config import settings

class BalanceService:
    def __init__(self, db: Session):
        self.db = db
    
    def update_customer_balance(self, movement: EquipmentMovement):
        """
        Updates customer equipment balance based on movement
        """
        # Find existing balance record
        balance = self.db.query(CustomerBalance).filter(
            CustomerBalance.customer_name == movement.customer_name,
            CustomerBalance.equipment_type == movement.equipment_type
        ).first()
        
        if not balance:
            # Create new balance record
            balance = CustomerBalance(
                customer_name=movement.customer_name,
                equipment_type=movement.equipment_type,
                current_balance=0,
                threshold=settings.DEFAULT_THRESHOLD,
                last_movement=movement.timestamp,
                status="normal"
            )
            self.db.add(balance)
        
        # Update balance (IN increases, OUT decreases)
        if movement.direction == Direction.IN:
            balance.current_balance += movement.quantity
        else:
            balance.current_balance -= movement.quantity
        
        balance.last_movement = movement.timestamp
        
        # Update status
        if balance.current_balance > balance.threshold:
            balance.status = "over_threshold"
            self._create_alert(balance)
        elif balance.current_balance < 0:
            balance.status = "negative"
            self._create_alert(balance)
        else:
            balance.status = "normal"
        
        self.db.commit()
        return balance
    
    def _create_alert(self, balance: CustomerBalance):
        """
        Create alert for threshold breach
        """
        # Check if alert already exists and is unresolved
        existing_alert = self.db.query(Alert).filter(
            Alert.customer_name == balance.customer_name,
            Alert.equipment_type == balance.equipment_type,
            Alert.resolved == False
        ).first()
        
        if existing_alert:
            # Update existing alert
            existing_alert.current_balance = balance.current_balance
            existing_alert.excess = max(0, balance.current_balance - balance.threshold)
            existing_alert.priority = self._calculate_priority(balance)
        else:
            # Create new alert
            excess = max(0, balance.current_balance - balance.threshold)
            alert = Alert(
                customer_name=balance.customer_name,
                equipment_type=balance.equipment_type,
                current_balance=balance.current_balance,
                threshold=balance.threshold,
                excess=excess,
                priority=self._calculate_priority(balance)
            )
            self.db.add(alert)
    
    def _calculate_priority(self, balance: CustomerBalance) -> str:
        """
        Calculate alert priority based on excess amount
        """
        if balance.current_balance > balance.threshold * settings.HIGH_PRIORITY_MULTIPLIER:
            return "high"
        else:
            return "medium"
    
    def get_customer_balance(self, customer_name: str, equipment_type: Optional[EquipmentType] = None) -> List[CustomerBalance]:
        """
        Get equipment balance for specific customer
        """
        query = self.db.query(CustomerBalance).filter(
            CustomerBalance.customer_name.ilike(f"%{customer_name}%")
        )
        
        if equipment_type:
            query = query.filter(CustomerBalance.equipment_type == equipment_type)
        
        return query.all()
    
    def get_all_balances(self, status: Optional[str] = None) -> List[CustomerBalance]:
        """
        Get all customer balances, optionally filtered by status
        """
        query = self.db.query(CustomerBalance)
        
        if status:
            query = query.filter(CustomerBalance.status == status)
        
        return query.all()
    
    def get_alerts(self) -> List[Alert]:
        """
        Get all unresolved alerts
        """
        return self.db.query(Alert).filter(Alert.resolved == False).all()
    
    def update_customer_balance_from_balance(self, balance: CustomerBalance):
        """
        Update customer balance from a balance object (for seeding)
        """
        # Check if balance already exists
        existing_balance = self.db.query(CustomerBalance).filter(
            CustomerBalance.customer_name == balance.customer_name,
            CustomerBalance.equipment_type == balance.equipment_type
        ).first()
        
        if existing_balance:
            # Update existing balance
            existing_balance.current_balance = balance.current_balance
            existing_balance.threshold = balance.threshold
            existing_balance.last_movement = balance.last_movement
            existing_balance.status = balance.status
        else:
            # Create new balance
            self.db.add(balance)
        
        self.db.commit()
        return balance
    
    def get_all_balances(self, status: Optional[str] = None) -> List[CustomerBalance]:
        """
        Get all customer balances, optionally filtered by status
        """
        query = self.db.query(CustomerBalance)
        if status:
            query = query.filter(CustomerBalance.status == status)
        return query.all()


# Global instance
balance_service = BalanceService(None)
