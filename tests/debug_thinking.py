#!/usr/bin/env python3
"""调试思考模式"""
import sys
import os
sys.path.insert(0, os.getcwd())

from src.llm.zhipu_client import ZhipuClient

client = ZhipuClient()

# 简单文本
text = "马云是阿里巴巴的创始人"

print("测试：启用思考模式")
print("=" * 50)

response = client.chat(
    messages=[
        {"role": "system", "content": "你是实体关系提取助手。从文本中提取实体和关系，输出JSON格式。"},
        {"role": "user", "content": f"文本：{text}\n\n请输出JSON格式，包含entities（实体）和relations（关系）"}
    ],
    thinking={"type": "enabled"}
)

print(f"\n成功: {response.success}")
print(f"模型: {response.model}")
print(f"思考内容: {response.reasoning_content[:100] if response.reasoning_content else '无'}...")
print(f"\n原始响应内容:")
print(response.content)
print(f"\n原始响应长度: {len(response.content)} 字符")

# 测试解析
try:
    data = client.extract_json(response.content)
    print(f"\n✅ 解析成功:")
    import json
    print(json.dumps(data, ensure_ascii=False, indent=2))
except Exception as e:
    print(f"\n❌ 解析失败: {e}")
    print(f"错误类型: {type(e).__name__}")
