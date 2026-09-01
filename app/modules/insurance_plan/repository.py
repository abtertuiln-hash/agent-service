from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from .models import InsurancePlan, InsurancePlanItem
from .schemas import InsurancePlanCreate

class InsurancePlanRepository:
    def __init__(self,session:AsyncSession):
        self.session = session

    async def create(self, user_id: int, data: InsurancePlanCreate) -> InsurancePlan:
        # 1. 计算方案组合年缴预算参考
        # 1.1 将每一个产品的产品年缴预算参考提取出来
        items_budget = [item.annual_premium_budget for item in data.items if item.annual_premium_budget is not None]

        # 2.2 累加求和就是组合年缴预算参考
        annual_premium_budget = sum(items_budget, Decimal('0') )if items_budget else None

        # 2. 保存保险方案
        insurance_plan = InsurancePlan(
            user_id=user_id,
            plan_name=data.plan_name,
            summary=data.summary,
            insured_profile=data.insured_profile,
            annual_premium_budget=annual_premium_budget,
        )
        self.session.add(insurance_plan)
        await self.session.flush()

        # 3. 保存保险方案项
        insurance_plan_items = [
            InsurancePlanItem(
                plan_id = insurance_plan.id,
                product_id=item.product_id,
                priority=item.priority,
                recommendation_reason=item.recommendation_reason,
                annual_premium_budget=item.annual_premium_budget
            )
            for item in data.items
        ]
        self.session.add_all(insurance_plan_items)

        return insurance_plan



