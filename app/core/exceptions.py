class ApplicationError(Exception):
    """应用业务异常基类"""
    status_code: int = 500
    code: str = "APPLICATION_ERROR"
    message: str = "服务器内部错误"

