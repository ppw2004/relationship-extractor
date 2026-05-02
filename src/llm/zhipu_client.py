"""智谱 AI 客户端封装"""
from openai import OpenAI
from typing import List, Dict, Any, Optional
import json
import time

from src.config import Config
from src.models.schemas import LLMResponse
from src.models.log_schemas import LLMLogEntry, LLMLogType
from src.logger.log_storage import LogStorage


class ZhipuClient:
    """智谱 AI 客户端"""

    def __init__(self, enable_logging: bool = None):
        """
        初始化客户端

        Args:
            enable_logging: 是否启用日志，默认从配置读取
        """
        self.client = OpenAI(
            api_key=Config.ZHIPU_API_KEY,
            base_url=Config.ZHIPU_API_BASE
        )
        self.model = Config.ZHIPU_MODEL
        self.temperature = Config.LLM_TEMPERATURE
        self.max_tokens = Config.LLM_MAX_TOKENS
        self.timeout = Config.LLM_TIMEOUT

        # 初始化日志存储
        if enable_logging is None:
            enable_logging = Config.ENABLE_LLM_LOGGING
        self.enable_logging = enable_logging
        self.log_storage = LogStorage(Config.LOG_DB_PATH) if enable_logging else None

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """
        发送聊天请求

        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大 token 数
            response_format: 响应格式 (text/json)
            **kwargs: 其他参数

        Returns:
            LLMResponse: 响应结果
        """
        start_time = time.time()
        actual_temperature = temperature or self.temperature
        actual_max_tokens = max_tokens or self.max_tokens

        # 记录请求日志
        if self.enable_logging and self.log_storage:
            self.log_storage.save_llm_log(LLMLogEntry(
                log_type=LLMLogType.CHAT_REQUEST,
                model=self.model,
                request_messages=json.dumps(messages, ensure_ascii=False),
                temperature=actual_temperature,
                max_tokens=actual_max_tokens
            ))

        try:
            # 构建请求参数
            request_params = {
                "model": self.model,
                "messages": messages,
                "temperature": actual_temperature,
                "max_tokens": actual_max_tokens,
                "timeout": self.timeout,
                **kwargs
            }

            # 如果指定了响应格式为 JSON
            if response_format == "json":
                request_params["response_format"] = {"type": "json_object"}

            # 发送请求
            response = self.client.chat.completions.create(**request_params)

            # 计算耗时
            duration_ms = (time.time() - start_time) * 1000

            # 解析响应
            llm_response = LLMResponse(
                content=response.choices[0].message.content,
                model=response.model,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                success=True
            )

            # 记录响应日志
            if self.enable_logging and self.log_storage:
                self.log_storage.save_llm_log(LLMLogEntry(
                    log_type=LLMLogType.CHAT_RESPONSE,
                    model=self.model,
                    request_messages=json.dumps(messages, ensure_ascii=False),
                    response_content=response.choices[0].message.content,
                    response_model=response.model,
                    prompt_tokens=response.usage.prompt_tokens,
                    completion_tokens=response.usage.completion_tokens,
                    total_tokens=response.usage.total_tokens,
                    temperature=actual_temperature,
                    max_tokens=actual_max_tokens,
                    duration_ms=duration_ms,
                    success=True
                ))

            return llm_response

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000

            # 记录错误日志
            if self.enable_logging and self.log_storage:
                self.log_storage.save_llm_log(LLMLogEntry(
                    log_type=LLMLogType.CHAT_ERROR,
                    model=self.model,
                    request_messages=json.dumps(messages, ensure_ascii=False),
                    temperature=actual_temperature,
                    max_tokens=actual_max_tokens,
                    duration_ms=duration_ms,
                    success=False,
                    error_message=str(e)
                ))

            return LLMResponse(
                content="",
                model=self.model,
                success=False,
                error=str(e)
            )

    def extract_json(self, content: str) -> Dict[str, Any]:
        """
        从响应内容中提取 JSON

        Args:
            content: 响应内容

        Returns:
            解析后的 JSON 对象
        """
        try:
            # 尝试直接解析
            return json.loads(content)
        except json.JSONDecodeError:
            # 尝试提取 JSON 代码块
            if "```json" in content:
                start = content.find("```json") + 7
                end = content.find("```", start)
                return json.loads(content[start:end].strip())
            elif "```" in content:
                start = content.find("```") + 3
                end = content.find("```", start)
                return json.loads(content[start:end].strip())
            else:
                raise ValueError(f"无法解析 JSON: {content}")

    def list_models(self) -> List[str]:
        """
        获取可用模型列表

        Returns:
            模型 ID 列表
        """
        try:
            models_response = self.client.models.list()
            return [model.id for model in models_response.data]
        except Exception as e:
            print(f"获取模型列表失败: {e}")
            # 返回已知的智谱模型列表
            return [
                "glm-4-flash",
                "glm-4-plus",
                "glm-4-air",
                "glm-4",
                "glm-3-turbo"
            ]

    def test_model(self, model_id: str) -> Dict[str, Any]:
        """
        测试指定模型是否可用

        Args:
            model_id: 模型 ID

        Returns:
            测试结果
        """
        test_messages = [
            {"role": "user", "content": "你好"}
        ]

        try:
            response = self.client.chat.completions.create(
                model=model_id,
                messages=test_messages,
                max_tokens=10,
                timeout=10
            )

            return {
                "model_id": model_id,
                "available": True,
                "response_model": response.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
        except Exception as e:
            return {
                "model_id": model_id,
                "available": False,
                "error": str(e)
            }
