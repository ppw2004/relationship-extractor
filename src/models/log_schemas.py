"""日志数据模型"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class LogLevel(str, Enum):
    """日志级别"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LLMLogType(str, Enum):
    """LLM 日志类型"""
    CHAT_REQUEST = "chat_request"
    CHAT_RESPONSE = "chat_response"
    CHAT_ERROR = "chat_error"


class DBLogType(str, Enum):
    """数据库日志类型"""
    QUERY = "query"
    EXECUTE = "execute"
    ERROR = "error"


class LLMLogEntry(BaseModel):
    """LLM 调用日志"""
    id: Optional[int] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    log_type: LLMLogType
    model: str
    request_messages: Optional[str] = None  # JSON 字符串
    response_content: Optional[str] = None
    reasoning_content: Optional[str] = None  # 深度思考内容
    response_model: Optional[str] = None
    thinking_enabled: Optional[bool] = None  # 是否启用思考
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    duration_ms: Optional[float] = None  # 耗时（毫秒）
    success: bool = True
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "log_type": self.log_type.value,
            "model": self.model,
            "request_messages": self.request_messages,
            "response_content": self.response_content,
            "reasoning_content": self.reasoning_content,
            "response_model": self.response_model,
            "thinking_enabled": self.thinking_enabled,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "duration_ms": self.duration_ms,
            "success": self.success,
            "error_message": self.error_message
        }


class Neo4jLogEntry(BaseModel):
    """Neo4j 操作日志"""
    id: Optional[int] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    log_type: DBLogType
    query: Optional[str] = None  # Cypher 语句
    parameters: Optional[str] = None  # JSON 字符串
    result_count: Optional[int] = None  # 影响行数
    duration_ms: Optional[float] = None  # 耗时（毫秒）
    success: bool = True
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "log_type": self.log_type.value,
            "query": self.query,
            "parameters": self.parameters,
            "result_count": self.result_count,
            "duration_ms": self.duration_ms,
            "success": self.success,
            "error_message": self.error_message
        }


class SystemLogEntry(BaseModel):
    """系统日志"""
    id: Optional[int] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    level: LogLevel
    module: str  # 模块名称
    message: str
    extra_data: Optional[str] = None  # JSON 字符串

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "level": self.level.value,
            "module": self.module,
            "message": self.message,
            "extra_data": self.extra_data
        }
