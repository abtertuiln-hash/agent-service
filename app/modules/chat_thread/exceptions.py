from app.core.exceptions import ApplicationError

class ChatThreadNotFoundError(ApplicationError):
    """会话不存在或不属于当前用户"""
    status_code = 400
    code = "CHAT_THREAD_NOT_FOUND"
    message = "会话不存在或不属于当前用户"