from typing import List
from decimal import Decimal
from app.models.db import db
from app.core.rules import (
    FlatDiscount, 
    PercentageDiscount, 
    SlabDiscount, 
    CategoryDiscount,
    BogoDiscount
)
from app.models.schemas import BillCalculationRequest, BillCalculationResponse, AppliedDiscount, DiscountType, SavingsSummary

class DiscountEngine:
    def __init__(self):
        self.strategies = {
            DiscountType.FLAT: FlatDiscount,
            DiscountType.PERCENTAGE: PercentageDiscount,
            DiscountType.SLAB: SlabDiscount,
            DiscountType.CATEGORY: CategoryDiscount,
            DiscountType.BOGO: BogoDiscount
        }

    async def calculate_bill(self, request: BillCalculationRequest) -> BillCalculationResponse:
        cart_items = request.cart.get('items', [])
        gross_amount = sum(item.total_price for item in cart_items)
        
        total_discount = Decimal('0.0')
        applied_discounts = []

        # FIX: Await the async DB call
        all_rules = await db.get_all_promotions()
        
        active_rules = sorted(
            [r for r in all_rules if r.active], 
            key=lambda x: x.priority
        )

        for rule_model in active_rules:
            strategy_class = self.strategies.get(rule_model.type)
            if not strategy_class:
                continue

            strategy = strategy_class(rule_model)
            
            if strategy.is_applicable(request, gross_amount):
                discount = strategy.calculate_discount(request, gross_amount)
                
                if discount > 0:
                    total_discount += discount
                    applied_discounts.append(AppliedDiscount(
                        promotion_id=rule_model.id,
                        name=rule_model.name,
                        amount=discount,
                        explanation=f"Applied {rule_model.type} logic"
                    ))
                    
                    if not rule_model.stackable:
                        break

        total_discount = min(total_discount, gross_amount)
        net_amount = gross_amount - total_discount
        
        savings_pct = 0.0
        if gross_amount > 0:
            savings_pct = float((total_discount / gross_amount) * 100)

        return BillCalculationResponse(
            gross_amount=gross_amount,
            total_discount=total_discount,
            net_amount=net_amount,
            discounts=applied_discounts,
            savings_summary=SavingsSummary(
                you_saved=total_discount,
                savings_percentage=round(savings_pct, 2)
            )
        )