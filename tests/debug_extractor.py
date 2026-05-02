#!/usr/bin/env python3
"""调试提取器"""
import sys
import os
sys.path.insert(0, os.getcwd())

from src.llm.zhipu_client import ZhipuClient
from src.llm.prompts import EXTRACT_SYSTEM_PROMPT, build_extract_prompt

text = "马云是阿里巴巴的创始人"

print("=" * 70)
print("调试提取器")
print("=" * 70)

client = ZhipuClient()

# 测试 1: 禁用思考
print("\n【测试 1：禁用思考 + JSON 格式】")
print("-" * 70)

response = client.chat(
    messages=[
        {"role": "system", "content": EXTRACT_SYSTEM_PROMPT},
        {"role": "user", "content": build_extract_prompt(text)}
    ],
    response_format="json",
    thinking=None
)

print(f"成功: {response.success}")
print(f"内容长度: {len(response.content) if response.content else 0}")
print(f"内容: {response.content[:200] if response.content else '(空)'}...")

try:
    data = client.extract_json(response.content)
    print(f"\n✅ JSON 解析成功:")
    import json
    print(json.dumps(data, ensure_ascii=False, indent=2))
except Exception as e:
    print(f"\n❌ JSON 解析失败: {e}")

# 测试 2: 启用思考
print("\n\n【测试 2：启用思考 + 纯文本】")
print("-" * 70)

response2 = client.chat(
    messages=[
        {"role": "system", "content": EXTRACT_SYSTEM_PROMPT},
        {"role": "user", "content": build_extract_prompt(text)}
    ],
    response_format=None,
    thinking={"type": "enabled"}
)

print(f"成功: {response2.success}")
print(f"思考内容: {'有 (' + str(len(response2.reasoning_content)) + ' 字符)' if response2.reasoning_content else '无'}")
print(f"内容长度: {len(response2.content) if response2.content else 0}")
print(f"内容: {response2.content[:200] if response2.content else '(空)'}...")

try:
    data2 = client.extract_json(response2.content)
    print(f"\n✅ JSON 解析成功:")
    import json
    print(json.dumps(data2, ensure_ascii=False, indent=2))
except Exception as e:
    print(f"\n❌ JSON 解析失败: {e}")

print("\n✅ 调试完成！")
