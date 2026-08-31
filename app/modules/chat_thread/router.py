from ..product.schemas import ProductResponse

from typing import Annotated

from fastapi import APIRouter, Depends, Header,status,Response,Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.infra.database import get_session
from .schemas import *
from .service import ChatThreadService


router = APIRouter(prefix = "/api/v1/chat-threads", tags=["会话管理的接口"])

def get_service(
        request: Request,
        session: AsyncSession = Depends(get_session)
    ):
    return ChatThreadService(
        session = session,
        agent=request.app.state.agent
    )

@router.post("", response_model=ChatThreadResponse)
async def create_chat_thread(
        request: ChatThreadCreate,
        user_id: Annotated[int, Header(alias="x-user-id")],
        service: ChatThreadService = Depends(get_service),
):
    """创建会话"""

    return await service.add(user_id, request.title)

@router.get("", response_model=list[ChatThreadResponse])
async def list_chat_threads(
    user_id: Annotated[int, Header(alias="x-user-id")],
    service: ChatThreadService = Depends(get_service),
):
    """查询当前用户的会话列表"""

    return await service.list_by_user(user_id)

@router.patch("/{thread_id}",  response_model=ChatThreadResponse)
async def rename(
    thread_id: str,
    request: ChatThreadCreate,
    user_id: Annotated[int, Header(alias="x-user-id")],
    service: ChatThreadService = Depends(get_service),
):
    """重命名会话"""

    return await service.rename(thread_id, user_id, request.title)

@router.delete("/{thread_id}", status_code=status.HTTP_204_NO_CONTENT,)
async def delete_chat_thread(
        thread_id: UUID,
        user_id: Annotated[int, Header(alias="x-user-id")],
        service: ChatThreadService = Depends(get_service),
) -> Response:
    """删除会话"""

    await service.delete(thread_id, user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.get("/{thread_id}/messages",response_model=ChatHistoryResponse)
async def get_chat_history(
    thread_id: UUID,
    user_id: Annotated[int, Header(alias="x-user-id")],
    service: ChatThreadService = Depends(get_service),
):
    """查询指定会话的历史消息"""

    return await service.get_history(thread_id, user_id)
