#!/usr/bin/env python3
"""检查思考模式的原始响应"""
import sys
import os
import json
sys.path.insert(0, os.getcwd())

from src.llm.zhipu_client import ZhipuClient


def test_raw_response():
    """测试思考模式的原始响应"""
    print("=" * 70)
    print("检查思考模式完整响应")
    print("=" * 70)

    client = ZhipuClient()

    # 简单测试文本
    text = "马云是阿里巴巴的创始人"

    print(f"\n测试文本: {text}")

    # 测试 1: 禁用思考，使用 JSON 格式
    print("\n" + "=" * 70)
    print("【测试 1：禁用思考 + JSON 格式】")
    print("=" * 70)

    response1 = client.chat(
        messages=[
            {"role": "system", "content": "你是一个实体关系提取助手。请从文本中提取实体和关系，输出JSON格式。"},
            {"role": "user", "content": f"文本：{text}\n\n输出JSON格式：{{\"entities\": [...], \"relations\": [...]}}"}
        ],
        thinking={"type": "disabled"},
        response_format="json"
    )

    print(f"\n✅ 成功: {response1.success}")
    print(f"模型: {response1.model}")
    print(f"思考内容: {'有 (' + str(len(response1.reasoning_content)) + ' 字符)' if response1.reasoning_content else '无'}")
    print(f"响应内容:\n{response1.content}")
    print(f"\n尝试解析 JSON:")
    try:
        data = json.loads(response1.content)
        print(f"✅ JSON 解析成功: {json.dumps(data, ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"❌ JSON 解析失败: {e}")

    # 测试 2: 启用思考，使用 JSON 格式
    print("\n" + "=" * 70)
    print("【测试 2：启用思考 + JSON 格式】")
    print("=" * 70)

    response2 = client.chat(
        messages=[
            {"role": "system", "content": "你是一个实体关系提取助手。请从文本中提取实体和关系，输出JSON格式。"},
            {"role": "user", "content": f"文本：{text}\n\n输出JSON格式：{{\"entities\": [...], \"relations\": [...]}}"}
        ],
        thinking={"type": "enabled"},
        response_format="json"
    )

    print(f"\n✅ 成功: {response2.success}")
    print(f"模型: {response2.model}")
    print(f"思考内容: {'有 (' + str(len(response2.reasoning_content)) + ' 字符)' if response2.reasoning_content else '无'}")
    if response2.reasoning_content:
        print(f"\n思考内容:\n{response2.reasoning_content}")
    print(f"\n响应内容:\n{response2.content}")
    print(f"\n尝试解析 JSON:")
    try:
        data = json.loads(response2.content)
        print(f"✅ JSON 解析成功: {json.dumps(data, ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"❌ JSON 解析失败: {e}")

    # 测试 3: 启用思考，不使用 JSON 格式
    print("\n" + "=" * 70)
    print("【测试 3：启用思考 + 纯文本格式】")
    print("=" * 70)

    response3 = client.chat(
        messages=[
            {"role": "system", "content": "你是一个实体关系提取助手。请从文本中提取实体和关系。"},
            {"role": "user", "content": f"文本：{text}\n\n请输出JSON格式结果"}
        ],
        thinking={"type": "enabled"}
    )

    print(f"\n✅ 成功: {response3.success}")
    print(f"模型: {response3.model}")
    print(f"思考内容: {'有 (' + str(len(response3.reasoning_content)) + ' 字符)' if response3.reasoning_content else '无'}")
    if response3.reasoning_content:
        print(f"\n思考内容:\n{response3.reasoning_content}")
    print(f"\n响应内容:\n{response3.content}")

    # 检查响应的原始结构
    print("\n" + "=" * 70)
    print("【分析总结】")
    print("=" * 70)

    print("\n关键发现:")
    print(f"1. 禁用思考 + JSON: JSON 内容 = '{response1.content[:50]}...'")
    print(f"2. 启用思考 + JSON: JSON 内容 = '{response2.content[:50]}...'")
    print(f"3. 启用思考 + 文本: 响应包含完整输出")


if __name__ == "__main__":
    test_raw_response()
