from decimal import Decimal

from pydantic import BaseModel, Field
from typing import Optional


class InsurancePlanItemCreate(BaseModel):
    """新增保险方案项的请求模型"""
    product_id: int = Field(..., description='推荐产品ID')
    product_name: str = Field(..., description='产品名称')  # 用于展示
    category: str = Field(..., description='产品险种类型')  # 用于展示
    priority: int = Field(default=1, ge=1, description='方案内展示顺序')
    recommendation_reason: Optional[str] = Field(default=None, description='推荐该产品的理由')
    annual_premium_budget: Optional[Decimal] = Field(default=None, ge=0, description='产品年缴预算参考')

class InsurancePlanCreate(BaseModel):
    """新增保险方案的请求模型"""
    plan_name: str = Field(..., min_length=1, max_length=120, description='方案名称')
    summary: Optional[str] = Field(default=None, description='方案整体说明')
    insured_profile: dict = Field(default_factory=dict, description='推荐时使用的被保险人画像')
    items: list[InsurancePlanItemCreate] = Field(default_factory=list, description='方案中的产品项列表')

