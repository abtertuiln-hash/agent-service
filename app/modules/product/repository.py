from unittest import result
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.product.models import Product


class ProductRepository:
    """保险产品仓库"""
    def __init__(self,session:AsyncSession):
        self.session = session

    async def find_by_category(self,category:str|None) -> list[Product]:
        """根据产品分类查询产品"""

        conditions = [Product.status == 'active']

        if category is not None:
            conditions.append(Product.category == category)

        products  = await self.session.scalars(
            select(Product)
            .where(*conditions)
            .order_by(Product.id)
        )
        return list(products .all())

    async def find_limited_by_category(
            self,
            category: str,
            premium_min: Decimal | None,
            limit: int,
    ) -> list[Product]:
        conditions = [
            Product.status == "active",
            Product.category == category,
        ]
        if premium_min is not None:
            conditions.append(Product.min_premium < premium_min)

        products = await self.session.scalars(
            select(Product)
            .where(*conditions)
            .order_by(
                Product.min_premium.asc().nullslast(),
                Product.id.asc(),
            )
            .limit(limit)
        )
        return products.all()


