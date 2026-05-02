"""Neo4j 客户端封装"""
from neo4j import GraphDatabase, Driver
from typing import List, Dict, Any, Optional
import logging

from src.config import Config
from src.models.schemas import Entity, Relation, ExtractionResult

logger = logging.getLogger(__name__)


class Neo4jClient:
    """Neo4j 客户端"""

    def __init__(self):
        """初始化客户端"""
        self._driver: Optional[Driver] = None
        self._connect()

    def _connect(self):
        """建立数据库连接"""
        try:
            self._driver = GraphDatabase.driver(
                Config.NEO4J_URI,
                auth=(Config.NEO4J_USER, Config.NEO4J_PASSWORD),
                max_connection_lifetime=Config.NEO4J_MAX_CONNECTION_LIFETIME,
                max_transaction_retry_time=Config.NEO4J_MAX_TRANSACTION_RETRY_TIME,
                connection_acquisition_timeout=Config.NEO4J_CONNECTION_ACQUISITION_TIMEOUT
            )
            # 测试连接
            self._driver.verify_connectivity()
            logger.info("Neo4j 连接成功")
        except Exception as e:
            logger.error(f"Neo4j 连接失败: {e}")
            raise

    def close(self):
        """关闭连接"""
        if self._driver:
            self._driver.close()
            logger.info("Neo4j 连接已关闭")

    def execute_query(self, query: str, parameters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        执行 Cypher 查询

        Args:
            query: Cypher 查询语句
            parameters: 查询参数

        Returns:
            查询结果列表
        """
        try:
            with self._driver.session() as session:
                result = session.run(query, parameters or {})
                return [record.data() for record in result]
        except Exception as e:
            logger.error(f"查询执行失败: {e}")
            raise

    def create_entity(self, entity: Entity) -> Dict[str, Any]:
        """
        创建实体节点

        Args:
            entity: 实体对象

        Returns:
            创建的节点信息
        """
        query = """
        MERGE (e:Entity {name: $name})
        ON CREATE SET e.type = $type, e.created_at = datetime()
        ON MATCH SET e.type = $type, e.updated_at = datetime()
        RETURN e
        """

        properties = entity.properties or {}
        parameters = {
            "name": entity.name,
            "type": entity.type,
            **properties
        }

        # 如果有额外属性，动态添加到 SET 子句
        if properties:
            query = query.replace(
                "ON CREATE SET e.type = $type, e.created_at = datetime()",
                f"ON CREATE SET e.type = $type, e.created_at = datetime(){', ' + ', '.join(f'e.{k} = ${k}' for k in properties.keys()) if properties else ''}"
            )
            query = query.replace(
                "ON MATCH SET e.type = $type, e.updated_at = datetime()",
                f"ON MATCH SET e.type = $type, e.updated_at = datetime(){', ' + ', '.join(f'e.{k} = ${k}' for k in properties.keys()) if properties else ''}"
            )

        result = self.execute_query(query, parameters)
        return result[0] if result else {}

    def create_relation(self, relation: Relation) -> Dict[str, Any]:
        """
        创建关系

        Args:
            relation: 关系对象

        Returns:
            创建的关系信息
        """
        query = """
        MATCH (from:Entity {name: $from_name})
        MATCH (to:Entity {name: $to_name})
        MERGE (from)-[r:RELATES_TO {type: $rel_type}]->(to)
        ON CREATE SET r.created_at = datetime()
        ON MATCH SET r.updated_at = datetime()
        RETURN r
        """

        parameters = {
            "from_name": relation.from_entity,
            "to_name": relation.to_entity,
            "rel_type": relation.type
        }

        result = self.execute_query(query, parameters)
        return result[0] if result else {}

    def save_extraction_result(self, result: ExtractionResult) -> Dict[str, int]:
        """
        保存提取结果到图数据库

        Args:
            result: 提取结果对象

        Returns:
            保存统计信息
        """
        stats = {"entities": 0, "relations": 0}

        # 创建实体
        for entity in result.entities:
            try:
                self.create_entity(entity)
                stats["entities"] += 1
            except Exception as e:
                logger.warning(f"创建实体失败 {entity.name}: {e}")

        # 创建关系
        for relation in result.relations:
            try:
                self.create_relation(relation)
                stats["relations"] += 1
            except Exception as e:
                logger.warning(f"创建关系失败 {relation.from_entity}->{relation.to_entity}: {e}")

        logger.info(f"保存完成: {stats['entities']} 个实体, {stats['relations']} 个关系")
        return stats

    def get_all_entities(self) -> List[Dict[str, Any]]:
        """获取所有实体"""
        query = "MATCH (e:Entity) RETURN e ORDER BY e.name"
        return self.execute_query(query)

    def get_all_relations(self) -> List[Dict[str, Any]]:
        """获取所有关系"""
        query = """
        MATCH (from:Entity)-[r:RELATES_TO]->(to:Entity)
        RETURN from.name as from_name, from.type as from_type,
               r.type as relation_type, to.name as to_name, to.type as to_type
        ORDER BY from_name, to_name
        """
        return self.execute_query(query)

    def clear_all(self) -> int:
        """清空所有数据（谨慎使用）"""
        query = "MATCH (n) DETACH DELETE n"
        result = self.execute_query(query)
        # 返回删除的节点数
        return len(result)

    def get_entity_network(self, entity_name: str, depth: int = 1) -> List[Dict[str, Any]]:
        """
        获取实体的关系网络

        Args:
            entity_name: 实体名称
            depth: 关系深度

        Returns:
            关系网络数据
        """
        query = f"""
        MATCH path = (e:Entity {{name: $name}})-[r*1..{depth}]-(related)
        RETURN path
        """
        return self.execute_query(query, {"name": entity_name})

    def get_statistics(self) -> Dict[str, int]:
        """获取图数据库统计信息"""
        query = """
        MATCH (e:Entity) WITH count(e) as entity_count
        MATCH ()-[r:RELATES_TO]->() WITH entity_count, count(r) as relation_count
        RETURN entity_count, relation_count
        """
        result = self.execute_query(query)
        return result[0] if result else {"entity_count": 0, "relation_count": 0}
