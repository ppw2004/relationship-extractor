#!/usr/bin/env python3
"""测试智谱 AI 可用模型"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.llm.zhipu_client import ZhipuClient
from src.config import Config


def main():
    """主函数"""
    print("=" * 60)
    print("智谱 AI 模型检测")
    print("=" * 60)
    print(f"API Base: {Config.ZHIPU_API_BASE}")
    print(f"当前配置模型: {Config.ZHIPU_MODEL}\n")

    client = ZhipuClient()

    # 1. 获取模型列表
    print("-" * 60)
    print("1. 获取可用模型列表")
    print("-" * 60)

    models = client.list_models()
    print(f"\n找到 {len(models)} 个模型:\n")
    for i, model in enumerate(models, 1):
        current = " (当前)" if model == Config.ZHIPU_MODEL else ""
        print(f"  {i}. {model}{current}")

    # 2. 测试模型可用性
    print("\n" + "-" * 60)
    print("2. 测试模型可用性")
    print("-" * 60)

    results = []
    for model in models:
        print(f"\n测试 {model}...")
        result = client.test_model(model)
        results.append(result)

        if result["available"]:
            print(f"  ✅ 可用")
            print(f"  实际模型: {result['response_model']}")
            print(f"  Token 用量: {result['usage']}")
        else:
            print(f"  ❌ 不可用")
            print(f"  错误: {result['error']}")

    # 3. 汇总统计
    print("\n" + "=" * 60)
    print("汇总统计")
    print("=" * 60)

    available = [r for r in results if r["available"]]
    unavailable = [r for r in results if not r["available"]]

    print(f"\n可用模型: {len(available)}/{len(results)}")
    for r in available:
        print(f"  ✅ {r['model_id']}")

    if unavailable:
        print(f"\n不可用模型: {len(unavailable)}/{len(results)}")
        for r in unavailable:
            print(f"  ❌ {r['model_id']}: {r['error'][:50]}...")


if __name__ == "__main__":
    main()
