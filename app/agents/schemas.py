from dataclasses import dataclass
from decimal import Decimal
from typing import Optional, List

from pydantic import BaseModel, Field


@dataclass(frozen=True)
class InsuranceAgentContext:
    """保险顾问Agent运行时上下文"""
    user_id: int

class ProductToolResult(BaseModel):
    """产品工具结果模型"""
    id:int = Field(...,description="产品唯一标识")
    name:str = Field(...,description="产品名称")
    clause_name: str = Field(..., description='保险条款名称')
    category: str = Field(..., description='保险分类')
    insurer: str = Field(..., description='承保保险公司')
    image_url: Optional[str] = Field(None, description='产品展示图片地址')
    description: Optional[str] = Field(None, description='保险产品简介')
    min_premium: Optional[Decimal] = Field(None, description='产品公开的最低年缴保费参考')
    max_premium: Optional[Decimal] = Field(None, description='产品公开的最高保费参考，可为空')
    target_group: Optional[str] = Field(None, description='适用人群说明')
    highlights: Optional[List[str]] = Field(None, description='保险产品亮点列表')

    model_config = {
        "from_attributes": True,
    }