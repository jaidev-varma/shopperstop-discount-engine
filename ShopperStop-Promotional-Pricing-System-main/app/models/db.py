import asyncio
from typing import List, Optional
from app.models.schemas import PromotionRule, DiscountType

class InMemoryDB:
    def __init__(self):
        self.promotions = {}
        self.lock = asyncio.Lock()  # Concurrency handling
        self._seed_data()

    def _seed_data(self):
        # We seed data synchronously on startup
        seed_slab = PromotionRule(
            id="SLAB_REGULAR",
            name="Regular Customer Tier",
            type=DiscountType.SLAB,
            priority=1,
            conditions={"tier": "REGULAR"},
            action={
                "slabs": [
                    {"min": 0, "max": 5000, "rate": 0.0},
                    {"min": 5001, "max": 10000, "rate": 0.10},
                    {"min": 10001, "max": float('inf'), "rate": 0.20},
                ]
            }
        )
        self.promotions[seed_slab.id] = seed_slab

    async def get_all_promotions(self) -> List[PromotionRule]:
        async with self.lock:
            return list(self.promotions.values())

    async def get_promotion(self, rule_id: str) -> Optional[PromotionRule]:
        async with self.lock:
            return self.promotions.get(rule_id)

    async def add_promotion(self, rule: PromotionRule):
        async with self.lock:
            # Versioning Strategy
            if rule.id in self.promotions:
                existing = self.promotions[rule.id]
                rule.version = existing.version + 1
            else:
                rule.version = 1
                
            self.promotions[rule.id] = rule
            return rule

    async def delete_promotion(self, rule_id: str):
        async with self.lock:
            if rule_id in self.promotions:
                del self.promotions[rule_id]
                return True
            return False

db = InMemoryDB()