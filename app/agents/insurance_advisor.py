from typing import Callable

from langchain.agents import create_agent
from langchain.agents.middleware import wrap_tool_call
from langchain.chat_models import init_chat_model
from langchain_core.messages import ToolMessage
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.prebuilt.tool_node import ToolCallRequest
from langgraph.types import Command

from app.core.config import settings
from app.core.logging import get_logger
from .tools import query_candidate_products,save_insurance_plan
from .schemas import InsuranceAgentContext

logger = get_logger(__name__)

SYSTEM_PROMPT = """
你是“安心保”的智能保险顾问。
你需要使用专业、准确、容易理解的语言回答用户的保险问题。
当信息不足时，应先向用户追问，不要编造保险产品或保障内容。
"""

@wrap_tool_call
async def handle_tool_errors(
        request: ToolCallRequest,
        handler: Callable
)-> ToolMessage | Command:
    """处理工具执行错误，返回自定义错误消息给模型"""
    try:
        return await handler(request)
    except Exception as e:
        logger.error(f"工具执行失败:{str(e)}")
        return ToolMessage(
            content=f'工具执行失败:{str(e)}',
            tool_call_id=request.tool_call['id']
        )


def init_insurance_agent(checkpointer:AsyncPostgresSaver):
    """初始化保险顾问Agent"""

    # 1.初始化模型
    model = init_chat_model(
        model=settings.llm.chat_model,
        model_provider = "deepseek",
        api_key = settings.llm.api_key,
        extra_body = {"thinking": {"type": "disabled"}},
    )

    # 2.创建Agent
    agent = create_agent(
        model = model,
        tools = [query_candidate_products,save_insurance_plan],
        system_prompt = SYSTEM_PROMPT,
        checkpointer = checkpointer,
        context_schema=InsuranceAgentContext,
        middleware=[handle_tool_errors]
    )
    logger.info("保险顾问Agent初始化成功~✅️")
    return agent





