from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime
from enum import Enum

# --- Enums ---
class DiscountType(str, Enum):
    SLAB = "SLAB_BASED"
    FLAT = "FLAT"
    PERCENTAGE = "PERCENTAGE"
    CATEGORY = "CATEGORY" # Added
    BOGO = "BUY_X_GET_Y"  # Added

# --- Core Domain Models ---

class CartItem(BaseModel):
    sku: str
    name: str
    category: str
    quantity: int = Field(gt=0)
    unit_price: Decimal = Field(ge=0)
    
    @property
    def total_price(self):
        return self.unit_price * self.quantity

class CustomerInfo(BaseModel):
    id: str
    tier: str

class RequestContext(BaseModel):
    store_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = {}

class BillCalculationRequest(BaseModel):
    customer: CustomerInfo
    cart: Dict[str, List[CartItem]] 
    context: RequestContext

# --- Configuration / Rule Models ---

class PromotionRule(BaseModel):
    id: str
    name: str
    type: DiscountType
    active: bool = True
    priority: int = 10 
    version: int = 1
    
    # Conditions (Who gets this?)
    # Supported keys: tier, min_cart_value, category, valid_from, valid_to
    conditions: Dict[str, Any] = {} 

    # Action (What do they get?)
    action: Dict[str, Any]

    # Constraints
    max_discount_amount: Optional[Decimal] = None
    stackable: bool = True

class AppliedDiscount(BaseModel):
    promotion_id: str
    name: str
    amount: Decimal
    explanation: str

class SavingsSummary(BaseModel):
    you_saved: Decimal
    savings_percentage: float

class BillCalculationResponse(BaseModel):
    gross_amount: Decimal
    total_discount: Decimal
    net_amount: Decimal
    discounts: List[AppliedDiscount]
    savings_summary: Optional[SavingsSummary] = None