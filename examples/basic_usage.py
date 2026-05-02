#!/usr/bin/env python3
"""基本使用示例"""
import logging
from src.extractor import RelationshipExtractor

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """主函数"""
    # 初始化提取器（会自动连接 Neo4j）
    extractor = RelationshipExtractor(auto_save=True)

    try:
        # 示例文本
        text = """
        马云是阿里巴巴集团的创始人，阿里巴巴总部位于杭州。
        1999年，马云带领团队在杭州创立了阿里巴巴。
        张勇是阿里巴巴集团的现任CEO，于2019年接任。
        """

        print("=" * 60)
        print("实体与关系提取示例")
        print("=" * 60)
        print(f"\n输入文本:\n{text}\n")
        print("-" * 60)

        # 提取实体和关系
        result = extractor.extract(text)

        # 打印结果
        print(f"\n提取的实体 ({len(result.entities)} 个):")
        for entity in result.entities:
            print(f"  - {entity.name} ({entity.type})")

        print(f"\n提取的关系 ({len(result.relations)} 个):")
        for relation in result.relations:
            print(f"  - {relation.from_entity} --[{relation.type}]--> {relation.to_entity}")

        # 查看数据库统计
        stats = extractor.get_statistics()
        print(f"\n数据库统计:")
        print(f"  - 实体总数: {stats['entity_count']}")
        print(f"  - 关系总数: {stats['relation_count']}")

        # 查询所有实体
        print(f"\n数据库中的所有实体:")
        entities = extractor.get_all_entities()
        for e in entities[:10]:  # 只显示前10个
            print(f"  - {e['e']['name']} ({e['e']['type']})")

        # 查询所有关系
        print(f"\n数据库中的所有关系:")
        relations = extractor.get_all_relations()
        for r in relations[:10]:  # 只显示前10个
            print(f"  - {r['from_name']} --[{r['relation_type']}]--> {r['to_name']}")

    finally:
        # 关闭连接
        extractor.close()


if __name__ == "__main__":
    main()
