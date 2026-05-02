#!/usr/bin/env python3
"""异步批量提取示例"""
import asyncio
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.extractor import RelationshipExtractor


async def main():
    """主函数"""
    print("=" * 60)
    print("异步批量提取示例")
    print("=" * 60)

    # 初始化提取器
    extractor = RelationshipExtractor(auto_save=True)

    try:
        # 示例文本列表
        texts = [
            "马云是阿里巴巴集团的创始人，阿里巴巴总部位于杭州。",
            "张勇是阿里巴巴集团的现任CEO，于2019年接任。",
            "腾讯总部位于深圳，由马化腾创立于1998年。",
            "百度是李彦宏创立的搜索引擎公司，总部位于北京。",
            "字节跳动是全球最大的独角兽企业之一，旗下拥有抖音等产品。"
        ]

        print(f"\n待处理文本数: {len(texts)}")
        print("并发数: 5")
        print("\n开始异步处理...\n")

        start_time = time.time()

        # 异步批量提取
        results = await extractor.extract_batch_async(
            texts=texts,
            concurrency=5
        )

        duration = time.time() - start_time

        # 打印结果
        print("\n" + "=" * 60)
        print("提取结果")
        print("=" * 60)

        for i, result in enumerate(results, 1):
            print(f"\n[{i}] 文本: {result.raw_text[:50]}...")
            print(f"    实体数: {len(result.entities)}")
            print(f"    关系数: {len(result.relations)}")

            if result.entities:
                print(f"    实体: {', '.join([e.name for e in result.entities[:3]])}")

        print("\n" + "=" * 60)
        print("性能统计")
        print("=" * 60)
        print(f"总耗时: {duration:.2f} 秒")
        print(f"平均每个: {duration/len(texts):.2f} 秒")
        print(f"吞吐量: {len(texts)/duration:.2f} 个/秒")

        # 查看数据库统计
        stats = extractor.get_statistics()
        print(f"\n数据库统计:")
        print(f"  实体总数: {stats['entity_count']}")
        print(f"  关系总数: {stats['relation_count']}")

    finally:
        extractor.close()


if __name__ == "__main__":
    # 运行异步主函数
    asyncio.run(main())
