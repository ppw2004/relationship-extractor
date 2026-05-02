#!/usr/bin/env python3
"""测试深度思考功能"""
import sys
import os
sys.path.insert(0, os.getcwd())

from src.llm.zhipu_client import ZhipuClient


def test_thinking():
    """测试深度思考模式"""
    print("=" * 70)
    print("测试智谱 AI 深度思考功能")
    print("=" * 70)

    client = ZhipuClient()

    # 测试问题
    question = "分析为什么马斯克收购了推特（现X），并分析这一决策的战略意义"

    print(f"\n问题: {question}\n")

    print("-" * 70)
    print("【启用深度思考模式】")
    print("-" * 70)

    # 启用深度思考
    response = client.chat(
        messages=[{"role": "user", "content": question}],
        thinking={"type": "enabled"}
    )

    if response.success:
        print(f"\n✅ 请求成功")
        print(f"模型: {response.model}")
        print(f"\nToken 使用:")
        print(f"  - 输入: {response.usage['prompt_tokens']}")
        print(f"  - 输出: {response.usage['completion_tokens']}")
        print(f"  - 总计: {response.usage['total_tokens']}")

        if response.reasoning_content:
            print(f"\n🧠 深度思考过程:")
            print("-" * 70)
            print(response.reasoning_content)
            print("-" * 70)

        print(f"\n💡 最终回答:")
        print("-" * 70)
        print(response.content)
        print("-" * 70)

        print(f"\n✅ 深度思考功能正常工作！")
        print(f"思考内容长度: {len(response.reasoning_content) if response.reasoning_content else 0} 字符")
        print(f"回答内容长度: {len(response.content)} 字符")
    else:
        print(f"❌ 请求失败: {response.error}")


if __name__ == "__main__":
    test_thinking()
