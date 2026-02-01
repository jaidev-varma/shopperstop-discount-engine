from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict
from fastapi import HTTPException

router = APIRouter()

class CustomerTierConfig(BaseModel):
    tier_name: str
    min_spend_threshold: int
    benefits: Dict[str, str] = {}

# Simple in-memory storage for tiers
tier_db = {
    "REGULAR": CustomerTierConfig(tier_name="REGULAR", min_spend_threshold=0),
    "PREMIUM": CustomerTierConfig(tier_name="PREMIUM", min_spend_threshold=10000)
}

@router.get("/", response_model=List[CustomerTierConfig])
async def get_customer_tiers():
    return list(tier_db.values())

@router.post("/")
async def create_customer_tier(tier: CustomerTierConfig):
    tier_db[tier.tier_name] = tier
    return tier

@router.put("/{tier_name}", response_model=CustomerTierConfig)
async def update_customer_tier(tier_name: str, tier: CustomerTierConfig):
    """
    Update configuration for a specific tier (e.g. change min_spend).
    """
    if tier_name not in tier_db:
        raise HTTPException(status_code=404, detail=f"Tier '{tier_name}' not found")
    
    # Update the In-Memory DB
    tier_db[tier_name] = tier
    return tier