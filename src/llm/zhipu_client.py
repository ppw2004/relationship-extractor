"""智谱 AI 客户端封装"""
from openai import OpenAI, AsyncOpenAI
from typing import List, Dict, Any, Optional
import json
import time
import asyncio

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
        thinking: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> LLMResponse:
        """
        发送聊天请求

        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大 token 数
            response_format: 响应格式 (text/json)
            thinking: 深度思考配置，如 {"type": "enabled"}
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
            # 注意：thinking 参数需要通过 extra_body 传递
            if thinking:
                response = self.client.chat.completions.create(
                    model=request_params["model"],
                    messages=request_params["messages"],
                    temperature=request_params["temperature"],
                    max_tokens=request_params["max_tokens"],
                    timeout=request_params["timeout"],
                    extra_body={"thinking": thinking}
                )
            else:
                response = self.client.chat.completions.create(**request_params)

            # 计算耗时
            duration_ms = (time.time() - start_time) * 1000

            # 解析响应（提取推理内容）
            message_obj = response.choices[0].message
            reasoning = getattr(message_obj, 'reasoning_content', None)

            llm_response = LLMResponse(
                content=message_obj.content,
                model=response.model,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                reasoning_content=reasoning,
                success=True
            )

            # 记录响应日志
            if self.enable_logging and self.log_storage:
                self.log_storage.save_llm_log(LLMLogEntry(
                    log_type=LLMLogType.CHAT_RESPONSE,
                    model=self.model,
                    request_messages=json.dumps(messages, ensure_ascii=False),
                    response_content=message_obj.content,
                    reasoning_content=reasoning,
                    response_model=response.model,
                    thinking_enabled=(thinking is not None),
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
        从响应内容中提取 JSON（简化版：只做基本提取和最小字段映射）

        Args:
            content: 响应内容

        Returns:
            解析后的 JSON 对象

        Raises:
            ValueError: 无法解析 JSON
        """
        # 提取 JSON 内容
        data = self._extract_json_content(content)

        # 最小字段映射（不改变类型值）
        self._minimize_field_mapping(data)

        return data

    def _extract_json_content(self, content: str) -> Dict[str, Any]:
        """从内容中提取 JSON"""
        try:
            # 尝试直接解析
            return json.loads(content)
        except json.JSONDecodeError:
            # 尝试提取 JSON 代码块
            if "```json" in content:
                start = content.find("```json") + 7
                end = content.find("```", start)
                if end > start:
                    return json.loads(content[start:end].strip())
            elif "```" in content:
                start = content.find("```") + 3
                end = content.find("```", start)
                if end > start:
                    return json.loads(content[start:end].strip())

            raise ValueError(f"无法解析 JSON: {content[:200]}...")

    def _minimize_field_mapping(self, data: Dict[str, Any]) -> None:
        """
        最小字段映射（只做结构兼容，不改变类型值）

        原则：
        - 保留模型返回的原始类型（"组织"、"公司"、"人名"等）
        - 只做基本的字段名映射
        - 后续分析时再统一类型
        """
        # 归一化实体：text → name
        if "entities" in data:
            for entity in data["entities"]:
                if "text" in entity and "name" not in entity:
                    entity["name"] = entity.pop("text")

        # 归一化关系：subject/predicate/object → from/type/to
        if "relations" in data:
            for relation in data["relations"]:
                # 处理 subject → from
                if "subject" in relation and "from" not in relation:
                    relation["from"] = relation.pop("subject")

                # 处理 predicate → type
                if "predicate" in relation and "type" not in relation:
                    relation["type"] = relation.pop("predicate")

                # 处理 object → to
                if "object" in relation and "to" not in relation:
                    relation["to"] = relation.pop("object")

                # 处理其他可能的变体
                if "source" in relation and "from" not in relation:
                    relation["from"] = relation.pop("source")
                if "target" in relation and "to" not in relation:
                    relation["to"] = relation.pop("target")
                if "relation" in relation and "type" not in relation:
                    relation["type"] = relation.pop("relation")

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


class AsyncZhipuClient:
    """智谱 AI 异步客户端"""

    def __init__(self, enable_logging: bool = None):
        """
        初始化异步客户端

        Args:
            enable_logging: 是否启用日志，默认从配置读取
        """
        self.client = AsyncOpenAI(
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

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """
        异步发送聊天请求

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

            # 异步发送请求
            response = await self.client.chat.completions.create(**request_params)

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

    async def close(self):
        """关闭异步客户端"""
        await self.client.close()

    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()

