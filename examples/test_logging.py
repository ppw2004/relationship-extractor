#!/usr/bin/env python3
"""测试日志系统"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.extractor import RelationshipExtractor


def main():
    """测试日志功能"""
    print("=" * 60)
    print("测试日志系统")
    print("=" * 60)

    # 初始化提取器（会自动记录日志）
    extractor = RelationshipExtractor(auto_save=True)

    try:
        # 测试文本
        text = "马云是阿里巴巴集团的创始人。"

        print(f"\n提取文本: {text}")
        print("\n执行提取...")

        # 执行提取（会记录 LLM 和 Neo4j 日志）
        result = extractor.extract(text)

        print(f"\n提取完成:")
        print(f"  实体: {len(result.entities)} 个")
        print(f"  关系: {len(result.relations)} 个")

    finally:
        extractor.close()

    # 查看日志统计
    from src.logger.log_storage import LogStorage
    from src.config import Config

    print("\n" + "=" * 60)
    print("日志统计")
    print("=" * 60)

    storage = LogStorage(Config.LOG_DB_PATH)
    stats = storage.get_statistics()

    print(f"\nLLM 调用:")
    print(f"  总次数: {stats['llm']['total']}")
    print(f"  成功: {stats['llm']['success']}")
    print(f"  失败: {stats['llm']['failed']}")
    print(f"  Token 消耗: {stats['llm']['total_tokens']:,}")

    print(f"\nNeo4j 操作:")
    print(f"  总次数: {stats['neo4j']['total']}")
    print(f"  成功: {stats['neo4j']['success']}")
    print(f"  失败: {stats['neo4j']['failed']}")

    print("\n✅ 日志系统测试完成")


if __name__ == "__main__":
    main()
