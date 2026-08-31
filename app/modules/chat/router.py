from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.sse import EventSourceResponse, ServerSentEvent

from fastapi import APIRouter, Depends, Request, Header
from app.infra.database import get_session
from .schemas import ChatRequest
from .service import ChatService

router = APIRouter(prefix="/api/v1/chat", tags=["与AI对话接口"])

def get_chat_service(
        request: Request,
        session:AsyncSession = Depends(get_session),
):
    # 1.创建ChatService
    agent = request.app.state.agent
    return ChatService(session, agent)

@router.post("",response_class=EventSourceResponse)
async def chat(
        request: ChatRequest,
        user_id: Annotated[int, Header(alias="x-user-id")],
        service: ChatService = Depends(get_chat_service)
):
    # Generator, 用yield不断生成内容，形成动态列表
    async for see in service.chat_stream(user_id,request):
        yield see
