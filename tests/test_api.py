#!/usr/bin/env python3
"""测试智谱 AI API 连接"""
import os
from dotenv import load_dotenv
from openai import OpenAI

# 加载环境变量
load_dotenv()

# 获取配置
api_key = os.getenv("ZHIPU_API_KEY")
base_url = os.getenv("ZHIPU_API_BASE")
model = os.getenv("ZHIPU_MODEL", "glm-4-flash")

print(f"API 配置:")
print(f"  Base URL: {base_url}")
print(f"  Model: {model}")
print(f"  API Key: {api_key[:20]}...{api_key[-10:]}\n")

# 初始化客户端
client = OpenAI(
    api_key=api_key,
    base_url=base_url
)

# 测试模型
print("=" * 50)
print("测试模型连接...")
print("=" * 50)

try:
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "你是一个助手"},
            {"role": "user", "content": "请用一句话介绍你自己"}
        ],
        temperature=0.7,
    )

    print("\n✅ 连接成功!")
    print(f"模型: {response.model}")
    print(f"回复: {response.choices[0].message.content}")
    print(f"Usage: {response.usage}")

except Exception as e:
    print(f"\n❌ 连接失败: {e}")
    print("\n提示: 请检查 .env 文件中的配置")
