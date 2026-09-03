from decimal import Decimal
from typing import Literal

from langchain.tools import tool
from langgraph.prebuilt import ToolRuntime

from app.infra.database import AsyncSessionFactory
from app.modules.insurance_plan.schemas import InsurancePlanCreate
from app.modules.insurance_plan.service import InsurancePlanService
from app.modules.product.service import ProductService
from .schemas import InsuranceAgentContext, ProductToolResult


@tool
async def query_candidate_products(
    categories : list[Literal['critical_illness', 'medical', 'accident', 'life']],
    premium_min : Decimal | None = None,
    limit_per_category : int = 5,
) -> list[ProductToolResult]:
    """
    查询候选推荐保险产品列表,在用户咨询保险产品或者要求推荐保险产品时调用
    :param categories: 需要推荐的保险分类列表(最少需要一个),保险分类标识(重疾险:critical_illness  百万医疗险:medical  意外险:accident 寿险:life)
    :param premium_min: 推荐保险的最低价格, 会返回保险最低价格低于这个值的保险产品
    :param limit_per_category: 每个分类下返回的推荐保险数量
    :return: 推荐保险的字典列表
    """
    # 1. 获取数据库会话对象
    async with AsyncSessionFactory() as session:
        # 2. 创建ProductService业务层对象
        product_service = ProductService(session)
        # 3. 调用业务层方法查询候选推荐产品
        products = await product_service.list_candidates(categories, premium_min, limit_per_category)
        # 4. 将数据库模型对象列表转化为Pydantic模型对象
        result_list = [ProductToolResult.model_validate(product) for product in products]
        # 5. 返回结果
        return result_list

@tool
async def save_insurance_plan(
        data:InsurancePlanCreate,
        runtime: ToolRuntime[InsuranceAgentContext]
) -> dict[str, str]:
    """
    保存当前用户的保险推荐方案
    当用户确认这个方案可以或者满意的情况下调用此工具完成保险方案保存
    :param data:保险方案数据
    :param runtime:
    :return:当用户保存方案时,一并给出保存方案和方案编号
    """
    async with AsyncSessionFactory() as session:
        # 创建业务层对象
        insurance_plan_service = InsurancePlanService(session=session)
        # 调用业务层完成保险方案保存
        plan_id = await insurance_plan_service.create_plan(
            user_id=runtime.context.user_id,
            data=data
        )

        return {'plan_id': str(plan_id), 'message': '保险方案保存成功'}
