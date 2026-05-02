#!/usr/bin/env python3
"""同步 vs 异步性能对比"""
import asyncio
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.extractor import RelationshipExtractor


def sync_extract(texts):
    """同步提取"""
    extractor = RelationshipExtractor(auto_save=False)  # 不保存，只测试性能
    try:
        start = time.time()
        results = extractor.extract_batch(texts)
        duration = time.time() - start
        return duration, len(results)
    finally:
        extractor.close()


async def async_extract(texts):
    """异步提取"""
    extractor = RelationshipExtractor(auto_save=False)  # 不保存，只测试性能
    try:
        start = time.time()
        results = await extractor.extract_batch_async(texts, concurrency=5)
        duration = time.time() - start
        return duration, len(results)
    finally:
        extractor.close()


def main():
    """主函数"""
    print("=" * 70)
    print("同步 vs 异步性能对比测试")
    print("=" * 70)

    # 准备测试文本
    texts = [
        "马云是阿里巴巴集团的创始人，阿里巴巴总部位于杭州。",
        "张勇是阿里巴巴集团的现任CEO，于2019年接任。",
        "腾讯总部位于深圳，由马化腾创立于1998年。",
        "百度是李彦宏创立的搜索引擎公司，总部位于北京。",
        "字节跳动是全球最大的独角兽企业之一，旗下拥有抖音等产品。",
        "京东是中国最大的电商平台之一，由刘强东创立。",
        "美团是王兴创立的生活服务电商平台，总部位于北京。",
        "华为是全球领先的ICT基础设施提供商，由任正非创立。",
        "小米是雷军创立的智能手机公司，总部位于北京。",
        "滴滴是程维创立的出行平台，总部位于北京。"
    ]

    print(f"\n测试配置:")
    print(f"  文本数量: {len(texts)}")
    print(f"  并发数: 5 (异步模式)")
    print(f"  保存到数据库: 否（纯性能测试）")

    # 同步测试
    print("\n" + "=" * 70)
    print("【同步模式】")
    print("=" * 70)
    sync_duration, sync_count = sync_extract(texts)
    print(f"耗时: {sync_duration:.2f} 秒")
    print(f"处理: {sync_count} 个文本")
    print(f"平均: {sync_duration/sync_count:.2f} 秒/个")

    # 异步测试
    print("\n" + "=" * 70)
    print("【异步模式】")
    print("=" * 70)
    async_duration, async_count = asyncio.run(async_extract(texts))
    print(f"耗时: {async_duration:.2f} 秒")
    print(f"处理: {async_count} 个文本")
    print(f"平均: {async_duration/async_count:.2f} 秒/个")

    # 对比结果
    print("\n" + "=" * 70)
    print("【性能对比】")
    print("=" * 70)
    speedup = sync_duration / async_duration
    time_saved = sync_duration - async_duration
    efficiency = (time_saved / sync_duration) * 100

    print(f"同步耗时: {sync_duration:.2f} 秒")
    print(f"异步耗时: {async_duration:.2f} 秒")
    print(f"节省时间: {time_saved:.2f} 秒")
    print(f"提升倍数: {speedup:.2f}x")
    print(f"效率提升: {efficiency:.1f}%")

    if speedup > 1:
        print(f"\n✅ 异步模式快了 {speedup:.2f} 倍！")
    else:
        print(f"\n⚠️  异步模式未显示明显优势（可能是网络延迟限制）")


if __name__ == "__main__":
    main()
