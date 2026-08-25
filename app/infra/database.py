from collections.abc import AsyncGenerator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings
from app.core.logging import get_logger
logger = get_logger(__name__)

# 1. 数据库连接地址
if not settings.db or not settings.db.url:
    raise RuntimeError("db.url未配置，初始化数据库失败！")
DATABASE_URL = settings.db.url

# 2. 创建异步数据库引擎
engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo=settings.db.echo,                  # 是否打印SQL语句
    pool_size=settings.db.pool_size,        # 连接池中长期保留的连接数
    max_overflow=settings.db.max_overflow,  # 连接池满后，允许临时创建的额外连接数
    pool_timeout=settings.db.pool_timeout,  # 获取连接的最长等待时间，单位：秒
    pool_recycle=settings.db.pool_recycle,  # 连接存活超过该时间后，在下次取出时重新创建
    pool_pre_ping=True,                     # 从连接池取出连接时，先检查连接是否有效
)

# 3. 创建异步 Session 工厂
AsyncSessionFactory = async_sessionmaker(
    bind=engine,
    autoflush=False,        # 执行查询前不自动 flush
    expire_on_commit=False, # commit 后保留 ORM 对象中的属性值
)

# 4. 获取session的工具
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """ 为每个 FastAPI 请求创建独立的 AsyncSession，适用于依赖注入。"""
    async with AsyncSessionFactory() as session:
        yield session

# 5. 释放数据库连接池
async def close_database() -> None:
    """ 关闭数据库引擎并释放连接池中的连接。应在应用关闭时调用。"""
    await engine.dispose()
    logger.info("数据库连接池已关闭~")

# 6. 数据库健康检查
async def check_database() -> None:
    async with engine.connect() as connection:
        await connection.execute(text("SELECT 1"))
    logger.info("数据库连接池初始化成功~✅️")