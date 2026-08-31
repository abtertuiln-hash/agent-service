from fastapi import FastAPI,Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn


from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.core.exceptions import ApplicationError
from app.modules.chat_thread.exceptions import ChatThreadNotFoundError
from app.agents.insurance_advisor import init_insurance_agent
from app.modules.chat.router import router as chat_router
from app.modules.chat_thread.router import router as chat_thread_router
from app.modules.product.router import router as product_router



import sys
from app.infra.checkpointer import (
    close_checkpointer,
    init_checkpointer,
)



# 初始化日志系统
configure_logging(settings.logging.level)
logger = get_logger(__name__)

# 生命周期管理（预留）
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"【{settings.app.name}】应用启动中...")
    from app.infra.checkpointer import init_checkpointer,close_checkpointer
    from app.infra.database import check_database, close_database
    try:
        # 1.检查SQLAlchemy的数据库连接状态
        await check_database()
        # 2.初始化checkpointer
        checkpointer = await init_checkpointer()
        # 3.初始化保险顾问Agent
        app.state.agent = init_insurance_agent(checkpointer)

        yield
    finally:
        logger.info("应用关闭中... ")
        # 关闭SQLAlchemy的数据库连接池
        await close_database()
        # 关闭checkpointer的数据库连接池
        await close_checkpointer()

app = FastAPI(
    title=settings.app.name,
    debug=settings.app.debug,
    lifespan=lifespan,
)

# 注册产品路由
from app.modules.product.router import router as product_router
app.include_router(product_router)

#注册会话路由
from app.modules.chat_thread.router import router as chat_thread_router
app.include_router(chat_thread_router)

#注册对话路由
app.include_router(chat_router)
app.include_router(chat_thread_router)
app.include_router(product_router)


# CORS配置，解决跨域问题
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", summary="健康检测接口")
async def health_check() -> dict[str, str]:
    logger.info("执行健康检查")
    return {"status": "ok"}

#注册全局异常处理器
@app.exception_handler(ApplicationError)
async def handle_application_error(
    request: Request,
    exc: ApplicationError, # 捕获到的异常（这里用自定义异常基类捕获，所有业务异常都会匹配到）
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code, # 异常中自带status
        content={
            "code": exc.code,        # 异常中自带code
            "message": exc.message,  # 异常中自带message
        },
    )


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.app.host,
        port=settings.app.port,
        reload=False,
        loop= "asyncio:SelectorEventLoop" if sys.platform == "win32" else "auto",
    )