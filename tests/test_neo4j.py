#!/usr/bin/env python3
"""测试 Neo4j 连接"""
from src.graph.neo4j_client import Neo4jClient
from src.config import Config

def test_neo4j():
    """测试 Neo4j 连接和基本操作"""
    print("测试 Neo4j 连接...")
    print(f"URI: {Config.NEO4J_URI}")
    print(f"User: {Config.NEO4J_USER}\n")

    client = Neo4jClient()

    # 获取统计信息
    stats = client.get_statistics()
    print(f"数据库统计:")
    print(f"  实体数: {stats['entity_count']}")
    print(f"  关系数: {stats['relation_count']}")

    # 测试查询
    entities = client.get_all_entities()
    print(f"\n实体列表:")
    for e in entities[:5]:
        print(f"  - {e['e']['name']} ({e['e']['type']})")

    relations = client.get_all_relations()
    print(f"\n关系列表:")
    for r in relations[:5]:
        print(f"  - {r['from_name']} --[{r['relation_type']}]--> {r['to_name']}")

    client.close()
    print("\n✅ Neo4j 连接测试完成")

if __name__ == "__main__":
    test_neo4j()
