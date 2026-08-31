from uuid import UUID

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """基础对话请求"""

    thread_id: UUID
    message: str = Field(min_length=1)