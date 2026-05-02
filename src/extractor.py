"""核心提取逻辑"""
import logging
from typing import Dict, Any, Optional

from src.config import Config
from src.models.schemas import Entity, Relation, ExtractionResult
from src.llm.zhipu_client import ZhipuClient
from src.llm.prompts import EXTRACT_SYSTEM_PROMPT, build_extract_prompt
from src.graph.neo4j_client import Neo4jClient

logger = logging.getLogger(__name__)


class RelationshipExtractor:
    """实体与关系提取器"""

    def __init__(self, auto_save: bool = True):
        """
        初始化提取器

        Args:
            auto_save: 是否自动保存到 Neo4j
        """
        # 验证配置
        Config.validate()

        self.llm_client = ZhipuClient()
        self.neo4j_client = Neo4jClient() if auto_save else None
        self.auto_save = auto_save

        logger.info("RelationshipExtractor 初始化完成")

    def extract(
        self,
        text: str,
        save: Optional[bool] = None,
        temperature: Optional[float] = None
    ) -> ExtractionResult:
        """
        从文本中提取实体和关系

        Args:
            text: 待提取的文本
            save: 是否保存到数据库（默认使用初始化时的 auto_save）
            temperature: LLM 温度参数

        Returns:
            ExtractionResult: 提取结果
        """
        logger.info(f"开始提取文本，长度: {len(text)} 字符")

        # 调用 LLM 提取
        messages = [
            {"role": "system", "content": EXTRACT_SYSTEM_PROMPT},
            {"role": "user", "content": build_extract_prompt(text)}
        ]

        response = self.llm_client.chat(
            messages=messages,
            temperature=temperature,
            response_format="json"
        )

        if not response.success:
            logger.error(f"LLM 调用失败: {response.error}")
            return ExtractionResult(raw_text=text)

        # 解析 JSON 响应
        try:
            data = self.llm_client.extract_json(response.content)
        except Exception as e:
            logger.error(f"JSON 解析失败: {e}")
            logger.debug(f"原始内容: {response.content}")
            return ExtractionResult(raw_text=text)

        # 构建结果对象
        entities = [Entity(**item) for item in data.get("entities", [])]
        relations = [Relation(**item) for item in data.get("relations", [])]

        result = ExtractionResult(
            entities=entities,
            relations=relations,
            raw_text=text
        )

        logger.info(f"提取完成: {len(entities)} 个实体, {len(relations)} 个关系")

        # 保存到数据库
        should_save = save if save is not None else self.auto_save
        if should_save and self.neo4j_client:
            try:
                stats = self.neo4j_client.save_extraction_result(result)
                logger.info(f"已保存到 Neo4j: {stats}")
            except Exception as e:
                logger.error(f"保存到 Neo4j 失败: {e}")

        return result

    def extract_batch(
        self,
        texts: list[str],
        save: Optional[bool] = None,
        temperature: Optional[float] = None
    ) -> list[ExtractionResult]:
        """
        批量提取

        Args:
            texts: 文本列表
            save: 是否保存到数据库
            temperature: LLM 温度参数

        Returns:
            提取结果列表
        """
        results = []
        for i, text in enumerate(texts, 1):
            logger.info(f"处理 {i}/{len(texts)}")
            result = self.extract(text, save=save, temperature=temperature)
            results.append(result)

        return results

    def get_statistics(self) -> Dict[str, int]:
        """获取图数据库统计信息"""
        if not self.neo4j_client:
            return {"entity_count": 0, "relation_count": 0}
        return self.neo4j_client.get_statistics()

    def get_all_entities(self) -> list[Dict[str, Any]]:
        """获取所有实体"""
        if not self.neo4j_client:
            return []
        return self.neo4j_client.get_all_entities()

    def get_all_relations(self) -> list[Dict[str, Any]]:
        """获取所有关系"""
        if not self.neo4j_client:
            return []
        return self.neo4j_client.get_all_relations()

    def close(self):
        """关闭连接"""
        if self.neo4j_client:
            self.neo4j_client.close()
        logger.info("提取器已关闭")
