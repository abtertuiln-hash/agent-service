from decimal import Decimal
from typing import Optional, Literal
from uuid import UUID, uuid4

from sqlalchemy import BigInteger, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.common.models import Base, CreateAtMixin, UpdateAtMixin


class InsurancePlan(Base, CreateAtMixin, UpdateAtMixin):
    """用户保存的保险产品组合方案"""
    __tablename__ = "insurance_plans"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        comment='方案主键'
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        comment='方案所属用户'
    )
    plan_name: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
        comment='方案名称'
    )
    summary: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment='方案整体说明'
    )
    insured_profile: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        server_default="{}",
        comment='推荐时使用的被保险人画像'
    )
    annual_premium_budget: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(14, 2),
        nullable=True,
        comment='组合年缴预算参考'
    )
    status: Mapped[Literal['uninsured', 'applying', 'insured']] = mapped_column(
        String(30),
        nullable=False,
        server_default="uninsured",
        comment='方案投保状态: uninsured-未投保、applying-投保中、insured-已投保'
    )


class InsurancePlanItem(Base, CreateAtMixin, UpdateAtMixin):
    """保险组合方案中的产品项"""
    __tablename__ = "insurance_plan_items"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        comment='方案项主键'
    )
    plan_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=False,
        comment='所属保险方案'
    )
    product_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        comment='推荐产品'
    )
    priority: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="1",
        comment='方案内展示顺序'
    )
    recommendation_reason: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment='推荐该产品的理由'
    )
    annual_premium_budget: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(14, 2),
        nullable=True,
        comment='产品年缴预算参考'
    )
    status: Mapped[Literal['uninsured', 'insured']] = mapped_column(
        String(30), nullable=False,
        server_default="uninsured",
        comment='方案项投保状态: uninsured-未投保、insured-已投保'
    )