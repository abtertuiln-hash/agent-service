from .models import *
from sqlalchemy.ext.asyncio import AsyncSession, result
from sqlalchemy import select

from .. import chat_thread

#仓储类，采用 Repository 模式
class ChatThreadRepository:

    def __init__(self,session: AsyncSession):
        self.session = session

    async def add(self,chat_thread: ChatThread):
        self.session.add(chat_thread)

    async def list_by_user(self,user_id: int) -> list[ChatThread]:
        result = await self.session.execute(
            select(ChatThread)
            .where(ChatThread.user_id == user_id)
            .order_by(
                ChatThread.updated_at.desc(),
                ChatThread.created_at.desc(),
            )
        )

        return result.scalars().all()

    async def find_owned(
            self,
            thread_id: UUID,
            user_id: int
    )-> ChatThread | None:
         return await self.session.scalar(
            select(ChatThread)
            .where(
                ChatThread.id == thread_id,
                ChatThread.user_id == user_id
            )
        )

    #删除方法
    async def delete(self,thread: ChatThread) -> None:
        await self.session.delete(thread)

