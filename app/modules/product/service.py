from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.product.repository import ProductRepository
from app.modules.product.schemas import ProductResponse


class ProductService:
    """保险产品服务"""
    def __init__(self,session: AsyncSession):
        self.session = session
        self.repository = ProductRepository(session)

    async def list_products(self,category: str | None,) -> list[ProductResponse]:
        return await self.repository.find_by_category(category)