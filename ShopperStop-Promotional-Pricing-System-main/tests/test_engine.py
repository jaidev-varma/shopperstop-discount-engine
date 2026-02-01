import pytest
from decimal import Decimal
from app.core.engine import DiscountEngine
from app.models.schemas import (
    BillCalculationRequest, CustomerInfo, RequestContext, 
    CartItem, PromotionRule, DiscountType
)
from app.models.db import db

# Helper
def create_request(tier="REGULAR", cart_items=None):
    if cart_items is None:
        cart_items = [CartItem(sku="1", name="TV", category="ELEC", quantity=1, unit_price=Decimal("5000"))]
    return BillCalculationRequest(
        customer=CustomerInfo(id="123", tier=tier),
        cart={"items": cart_items},
        context=RequestContext(store_id="1")
    )

@pytest.mark.asyncio
async def test_slab_discount_regular():
    # Setup
    db.promotions.clear()
    rule = PromotionRule(
        id="SLAB_REGULAR", name="Reg Tier", type=DiscountType.SLAB,
        conditions={"tier": "REGULAR"},
        action={"slabs": [
            {"min": 0, "max": 5000, "rate": 0.0},
            {"min": 5001, "max": 10000, "rate": 0.10},
            {"min": 10001, "max": float('inf'), "rate": 0.20}
        ]}
    )
    await db.add_promotion(rule)

    # Execute
    items = [CartItem(sku="1", name="TV", category="ELEC", quantity=1, unit_price=Decimal("15000"))]
    req = create_request("REGULAR", items)
    engine = DiscountEngine()
    res = await engine.calculate_bill(req)

    # Assert: 0 + 500 + 1000 = 1500
    assert res.total_discount == Decimal("1500.00")

@pytest.mark.asyncio
async def test_bogo_discount():
    # Buy 2 Get 1 Free
    db.promotions.clear()
    rule = PromotionRule(
        id="BOGO_SHIRT", name="Shirt BOGO", type=DiscountType.BOGO,
        conditions={"sku": "SHIRT"},
        action={"buy_x": 2, "get_y": 1}
    )
    await db.add_promotion(rule)

    # Buy 3 shirts (1000 each). Should pay for 2. Discount = 1000.
    items = [CartItem(sku="SHIRT", name="Shirt", category="CLOTH", quantity=3, unit_price=Decimal("1000"))]
    req = create_request("REGULAR", items)
    engine = DiscountEngine()
    res = await engine.calculate_bill(req)

    assert res.total_discount == Decimal("1000.00")