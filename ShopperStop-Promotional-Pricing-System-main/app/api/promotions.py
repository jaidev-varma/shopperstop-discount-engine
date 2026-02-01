from fastapi import APIRouter, HTTPException, status
from typing import List
from app.models.schemas import PromotionRule, BillCalculationRequest, BillCalculationResponse
from app.models.db import db
from app.core.engine import DiscountEngine

router = APIRouter()

@router.post("/", response_model=PromotionRule, status_code=status.HTTP_201_CREATED)
async def create_promotion(rule: PromotionRule):
    existing = await db.get_promotion(rule.id)
    if existing:
        raise HTTPException(status_code=400, detail="Promotion ID already exists")
    
    return await db.add_promotion(rule)

@router.get("/", response_model=List[PromotionRule])
async def list_promotions():
    return await db.get_all_promotions()

@router.get("/{rule_id}", response_model=PromotionRule)
async def get_promotion(rule_id: str):
    rule = await db.get_promotion(rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Promotion not found")
    return rule

# --- THIS WAS MISSING ---
@router.put("/{rule_id}", response_model=PromotionRule)
async def update_promotion(rule_id: str, rule: PromotionRule):
    """Update an existing promotion."""
    existing = await db.get_promotion(rule_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Promotion not found")
    
    if rule.id != rule_id:
        raise HTTPException(status_code=400, detail="Path ID does not match Body ID")

    return await db.add_promotion(rule)
# ------------------------

@router.post("/{rule_id}/activate")
async def activate_promotion(rule_id: str):
    rule = await db.get_promotion(rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Promotion not found")
    
    rule.active = True
    await db.add_promotion(rule)
    return {"status": "activated", "id": rule_id, "new_version": rule.version}

@router.post("/{rule_id}/deactivate")
async def deactivate_promotion(rule_id: str):
    rule = await db.get_promotion(rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Promotion not found")
    
    rule.active = False
    await db.add_promotion(rule)
    return {"status": "deactivated", "id": rule_id, "new_version": rule.version}

@router.delete("/{rule_id}")
async def delete_promotion(rule_id: str):
    success = await db.delete_promotion(rule_id)
    if not success:
        raise HTTPException(status_code=404, detail="Promotion not found")
    return {"message": "Promotion deleted successfully"}

@router.post("/simulate", response_model=BillCalculationResponse)
async def simulate_promotion(request: BillCalculationRequest):
    engine = DiscountEngine()
    return await engine.calculate_bill(request)