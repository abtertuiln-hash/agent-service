from pydantic import BaseModel,Field,field_validator
from uuid import UUID
from datetime import datetime
from langgraph.graph.state import CompiledStateGraph
from typing import Any, Literal


class ChatThreadCreate(BaseModel):
    """创建聊天线程请求模型"""

    title: str = Field(default="新会话", min_length=1, max_length=200)

    @field_validator("title", mode="before")
    @classmethod
    def strip_title(cls, value: str) -> str:
        return value.strip()

class ChatThreadResponse(BaseModel):
    """创建聊天线程响应模型"""
    id:UUID
    title: str
    created_at:datetime
    updated_at:datetime

    # 设置数据模型的配置信息
    model_config = {'from_attributes': True}


class ChatMessageResponse(BaseModel):
    """历史消息"""
    
    role: Literal["user", "assistant"]
    content: str


class ChatHistoryResponse(BaseModel):
    """会话历史响应"""

    thread_id: UUID
    messages: list[ChatMessageResponse]