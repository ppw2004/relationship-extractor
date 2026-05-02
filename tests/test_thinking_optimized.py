#!/usr/bin/env python3
"""优化版深度思考测试 - 对比测试"""
import sys
import os
import time
sys.path.insert(0, os.getcwd())

from src.extractor import RelationshipExtractor


def test_thinking_comparison():
    """对比测试：启用 vs 禁用深度思考"""
    print("=" * 70)
    print("深度思考模式对比测试")
    print("=" * 70)

    # 测试文本 - 需要推理的复杂文本
    text = """
    华为在2024年推出了自主研发的ERP系统名为MetaERP，该系统主要用于替代原来使用的Oracle系统，
    可以更好地支持公司的业务发展和数据安全。华为的这一举措被认为是对企业软件自主化的重要里程碑。
    与此同时，金蝶软件作为国内领先的企业管理软件供应商，也在积极推进云原生架构的转型，
    旨在为中小企业提供更灵活、更高效的数字化解决方案。
    """

    print(f"\n测试文本: {text[:100]}...")
    print("\n" + "=" * 70)

    # 测试 1: 禁用深度思考
    print("\n【测试 1：禁用深度思考】")
    print("-" * 70)

    extractor_no_thinking = RelationshipExtractor(auto_save=False)

    start_time = time.time()
    result_no_thinking = extractor_no_thinking.extract(
        text,
        enable_thinking=False
    )
    duration_no_thinking = time.time() - start_time

    print(f"\n耗时: {duration_no_thinking:.2f} 秒")
    print(f"实体数: {len(result_no_thinking.entities)}")
    print(f"关系数: {len(result_no_thinking.relations)}")
    print(f"思考内容: {'有' if result_no_thinking.entities[0].properties.get('reasoning') else '无'}")

    if result_no_thinking.entities:
        print("\n提取的实体:")
        for e in result_no_thinking.entities[:5]:
            print(f"  - {e.name} ({e.type})")

    if result_no_thinking.relations:
        print("\n提取的关系:")
        for r in result_no_thinking.relations[:3]:
            print(f"  - {r.from_entity} --[{r.type}]--> {r.to_entity}")

    extractor_no_thinking.close()

    # 测试 2: 启用深度思考
    print("\n" + "=" * 70)
    print("\n【测试 2：启用深度思考】")
    print("-" * 70)

    extractor_with_thinking = RelationshipExtractor(auto_save=False)

    start_time = time.time()
    result_with_thinking = extractor_with_thinking.extract(
        text,
        enable_thinking=True
    )
    duration_with_thinking = time.time() - start_time

    print(f"\n耗时: {duration_with_thinking:.2f} 秒")
    print(f"实体数: {len(result_with_thinking.entities)}")
    print(f"关系数: {len(result_with_thinking.relations)}")

    if result_with_thinking.entities:
        print("\n提取的实体:")
        for e in result_with_thinking.entities[:5]:
            print(f"  - {e.name} ({e.type})")

    if result_with_thinking.relations:
        print("\n提取的关系:")
        for r in result_with_thinking.relations[:3]:
            print(f"  - {r.from_entity} --[{r.type}]--> {r.to_entity}")

    extractor_with_thinking.close()

    # 对比结果
    print("\n" + "=" * 70)
    print("【性能对比】")
    print("=" * 70)

    time_diff = duration_with_thinking - duration_no_thinking
    entity_diff = len(result_with_thinking.entities) - len(result_no_thinking.entities)
    relation_diff = len(result_with_thinking.relations) - len(result_no_thinking.relations)

    print(f"\n禁用思考: {duration_no_thinking:.2f}s, {len(result_no_thinking.entities)} 实体, {len(result_no_thinking.relations)} 关系")
    print(f"启用思考: {duration_with_thinking:.2f}s, {len(result_with_thinking.entities)} 实体, {len(result_with_thinking.relations)} 关系")
    print(f"\n时间差异: {time_diff:+.2f} 秒 ({time_diff/duration_no_thinking*100:+.1f}%)")
    print(f"实体差异: {entity_diff:+d}")
    print(f"关系差异: {relation_diff:+d}")

    # 查看日志中的思考内容
    print("\n" + "=" * 70)
    print("【检查日志记录】")
    print("=" * 70)

    from src.logger.log_storage import LogStorage
    from src.config import Config

    storage = LogStorage(Config.LOG_DB_PATH)
    logs = storage.get_llm_logs(limit=5)

    print(f"\n最近 {len(logs)} 条日志:")
    for i, log in enumerate(logs, 1):
        print(f"\n[{i}] {log['timestamp']}")
        print(f"  模型: {log['model']}")
        print(f"  思考启用: {'是' if log.get('thinking_enabled') else '否'}")
        print(f"  Tokens: {log['total_tokens']}")
        if log.get('reasoning_content'):
            reasoning_preview = log['reasoning_content'][:100] + "..." if len(log['reasoning_content']) > 100 else log['reasoning_content']
            print(f"  思考内容: {reasoning_preview}")

    print("\n✅ 测试完成！")


if __name__ == "__main__":
    test_thinking_comparison()
