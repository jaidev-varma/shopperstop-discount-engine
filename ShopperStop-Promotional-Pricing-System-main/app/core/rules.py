from abc import ABC, abstractmethod
from decimal import Decimal
from datetime import datetime
from app.models.schemas import PromotionRule, BillCalculationRequest

class BaseDiscountStrategy(ABC):
    def __init__(self, rule: PromotionRule):
        self.rule = rule

    def is_applicable(self, request: BillCalculationRequest, current_total: Decimal) -> bool:
        # 1. Active Check
        if not self.rule.active:
            return False
            
        # 2. Tier Check
        req_tier = self.rule.conditions.get('tier')
        if req_tier and req_tier != request.customer.tier:
            return False

        # 3. Min Cart Value Check
        min_val = self.rule.conditions.get('min_cart_value')
        if min_val and current_total < Decimal(str(min_val)):
            return False

        # 4. Time/Date Check (Happy Hour logic)
        now = request.context.timestamp
        valid_from = self.rule.conditions.get('valid_from')
        valid_to = self.rule.conditions.get('valid_to')

        if valid_from:
            start_dt = datetime.fromisoformat(valid_from) if isinstance(valid_from, str) else valid_from
            if now < start_dt:
                return False
        
        if valid_to:
            end_dt = datetime.fromisoformat(valid_to) if isinstance(valid_to, str) else valid_to
            if now > end_dt:
                return False
            
        return True

    @abstractmethod
    def calculate_discount(self, request: BillCalculationRequest, current_total: Decimal) -> Decimal:
        pass

    def apply_cap(self, discount_amount: Decimal) -> Decimal:
        if self.rule.max_discount_amount:
            return min(discount_amount, self.rule.max_discount_amount)
        return discount_amount

# --- Strategy Implementations ---

class FlatDiscount(BaseDiscountStrategy):
    def calculate_discount(self, request: BillCalculationRequest, current_total: Decimal) -> Decimal:
        amount = Decimal(str(self.rule.action.get('flat_amount', 0)))
        return self.apply_cap(amount)

class PercentageDiscount(BaseDiscountStrategy):
    def calculate_discount(self, request: BillCalculationRequest, current_total: Decimal) -> Decimal:
        rate = Decimal(str(self.rule.action.get('rate', 0)))
        discount = current_total * rate
        return self.apply_cap(discount)

class CategoryDiscount(BaseDiscountStrategy):
    def calculate_discount(self, request: BillCalculationRequest, current_total: Decimal) -> Decimal:
        target_category = self.rule.conditions.get("category")
        discount_rate = Decimal(str(self.rule.action.get("rate", 0)))
        
        if not target_category:
            return Decimal(0)

        category_total = Decimal(0)
        cart_items = request.cart.get("items", [])
        
        for item in cart_items:
            if item.category.upper() == target_category.upper():
                category_total += item.total_price

        discount_amount = category_total * discount_rate
        return self.apply_cap(discount_amount)

class SlabDiscount(BaseDiscountStrategy):
    def calculate_discount(self, request: BillCalculationRequest, current_total: Decimal) -> Decimal:
        slabs = self.rule.action.get('slabs', [])
        sorted_slabs = sorted(slabs, key=lambda x: x['min'])
        
        calculated_discount = Decimal('0.0')
        previous_limit = Decimal('0')

        for slab in sorted_slabs:
            if current_total <= previous_limit:
                break

            slab_min = Decimal(str(slab['min']))
            slab_max = Decimal(str(slab['max']))
            rate = Decimal(str(slab['rate']))

            current_slab_ceiling = slab_max if slab_max != float('inf') else current_total
            effective_upper = min(current_total, current_slab_ceiling)
            amount_in_slab = max(Decimal('0'), effective_upper - previous_limit)

            if amount_in_slab > 0:
                discount_for_slab = amount_in_slab * rate
                calculated_discount += discount_for_slab
            
            previous_limit = effective_upper

        return self.apply_cap(calculated_discount)

class BogoDiscount(BaseDiscountStrategy):
    def calculate_discount(self, request: BillCalculationRequest, current_total: Decimal) -> Decimal:
        target_sku = self.rule.conditions.get("sku")
        buy_x = int(self.rule.action.get("buy_x", 2))
        get_y = int(self.rule.action.get("get_y", 1))
        
        if not target_sku:
            return Decimal(0)

        cart_items = request.cart.get("items", [])
        discount_amount = Decimal(0)

        for item in cart_items:
            if item.sku == target_sku:
                free_count = (item.quantity // (buy_x + get_y)) * get_y
                discount_amount += Decimal(free_count) * item.unit_price

        return self.apply_cap(discount_amount)