from uuid import UUID

from langgraph.graph.state import CompiledStateGraph
from sqlalchemy.ext.asyncio import AsyncSession
from langchain_core.messages import AIMessage, HumanMessage

from .repository import ChatThreadRepository
from .models import ChatThread

from .exceptions import ChatThreadNotFoundError
from app.modules.chat_thread.schemas import (
    ChatHistoryResponse,
    ChatMessageResponse,
)



class ChatThreadService:
    def __init__(self,session: AsyncSession,agent: CompiledStateGraph,):
        self.session = session
        self.repository = ChatThreadRepository(session)
        self.agent = agent

    async def  add(self, user_id: int , title: str):
        # 用上下文管理，开启事务，运行完成，自动commit，出现异常，自动rollback
        async with self.session.begin():
            # 创建对象，对象 映射 到数据库 一条数据
            chat_thread = ChatThread(user_id=user_id, title=title)
            # 新增对象，就是插入一条数据
            await self.repository.add(chat_thread)

            return chat_thread

    async def list_by_user(self, user_id: int)->list[ChatThread]:
        return await self.repository.list_by_user(user_id)

    async def rename(
            self,
            thread_id:UUID,
            user_id:int,
            title:str
    ) -> ChatThread:
        async with self.session.begin():
            # 1.根据thread_id和user_id查询，判断是否匹配
            thread = await self.repository.find_owned(thread_id, user_id)
            if thread is None:
                # 为None，说明不存在，或者不属于当前用户，抛出异常
                # raise: 就是指扔出去一个异常，代码会立刻终止，结束运行，把异常扔给调用者
                raise ChatThreadNotFoundError

            # 2.查询后直接修改字段，触发数据库更新
            thread.title = title

            # 3.刷新数据，重新从数据库中查出最新值
            await self.session.flush()
            await self.session.refresh(thread)

        return thread

    #删除方法
    async def delete(
            self,
            thread_id:UUID,
            user_id:int,
    ) -> None:
        async with self.session.begin():
            thread = await self.repository.find_owned(thread_id, user_id)
            if thread is None:
                raise ChatThreadNotFoundError

            await self.repository.delete(thread)

    #查询历史
    async def get_history(
            self,
            thread_id: UUID,
            user_id: int,
    )-> ChatHistoryResponse:
        # 1.校验会话归属
        thread = await self.repository.find_owned(thread_id, user_id)
        if thread is None:
            raise ChatThreadNotFoundError

        # 2.读取Agent最新状态
        config = {"configurable": {"thread_id": str(thread_id)}}
        snapshot = await self.agent.aget_state(config)

        # 3.只保留用户消息和AI消息
        messages = []
        for message in snapshot.values.get("messages", []):
            if isinstance(message, HumanMessage):
                role = "user"
            elif isinstance(message, AIMessage):
                role = "assistant"
            else:
                continue

            if message.text:
                messages.append(
                    ChatMessageResponse(
                        role=role,
                        content=message.text,
                    )
                )

        return ChatHistoryResponse(
            thread_id=thread_id,
            messages=messages,
        )

# 删除会话历史
    async def delete(
            self,
            thread_id: UUID,
            user_id: int,
    ) -> None:
        async with self.session.begin():
            # 1.校验会话归属
            thread = await self.repository.find_owned(thread_id, user_id)
            if thread is None:
                raise ChatThreadNotFoundError

            # 2.删除checkpointer中的会话状态
            await self.agent.checkpointer.adelete_thread(str(thread_id))

            # 3.删除会话元数据
            await self.repository.delete(thread)


