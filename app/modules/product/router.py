from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.infra.database import get_session
from app.modules.product.schemas import ProductResponse
from app.modules.product.service import ProductService

router = APIRouter(prefix="/api/v1/products", tags=["product"])

@router.get('',response_model=list[ProductResponse])
async def list_products(category: str | None = None,session: AsyncSession = Depends(get_session),) -> list[ProductResponse]:
    # 1.获取Service
    service = ProductService(session)
    # 2.查询并返回产品列表
    return await service.list_products(category)
