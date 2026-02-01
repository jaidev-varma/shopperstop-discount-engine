from fastapi import APIRouter, HTTPException
from app.models.schemas import BillCalculationRequest, BillCalculationResponse
from app.core.engine import DiscountEngine

router = APIRouter()
engine = DiscountEngine()

@router.post("/calculate", response_model=BillCalculationResponse)
async def calculate_bill(request: BillCalculationRequest):
    try:
        # --- FIX: Added 'await' here ---
        # The engine is now async (uses database lock), so we must await the result.
        return await engine.calculate_bill(request)
        # -------------------------------
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))