# Relationship Extractor

基于大模型的实体与关系提取工具，通过自然语言处理技术从文本中自动抽取实体及其关系，并构建知识图谱。

## 项目简介

本项目旨在利用大语言模型（LLM）的强大推理能力，从非结构化文本中自动识别实体及其语义关系，并将结果存储到 Neo4j 图数据库中，形成可视化的知识图谱。

## 功能特性

- [x] 文本实体识别与抽取
- [x] 实体关系类型推断
- [x] 知识图谱自动构建
- [x] Neo4j 图数据库存储
- [x] LLM 调用日志记录
- [x] 数据库操作日志记录
- [x] 完整的日志查询系统
- [x] **异步批量处理** - 支持高并发异步提取
- [x] **深度思考模式** - 启用 LLM 推理能力提升准确性
- [ ] 支持多种文本格式输入
- [ ] 提取结果可视化展示
- [ ] 批量文本处理
- [ ] 结果导出功能（JSON/CSV）
- [ ] REST API 接口服务

## 技术栈

- **大语言模型**: [智谱 AI](https://open.bigmodel.cn/) (GLM-4.5/4.6/4.7/5/5.1)
- **LLM SDK**: OpenAI SDK (兼容智谱 API)
- **图数据库**: Neo4j
- **日志数据库**: SQLite
- **编程语言**: Python 3.10+
- **主要依赖**:
  - `openai` - OpenAI SDK (智谱 AI 兼容)
  - `neo4j` - Neo4j 驱动
  - `python-dotenv` - 环境变量管理
  - `pydantic` - 数据验证

## 项目结构

```
relationship-extractor/
├── README.md
├── requirements.txt          # Python 依赖
├── .env.example             # 环境变量示例
├── .gitignore               # Git 忽略配置
├── src/
│   ├── config.py            # 全局配置
│   ├── extractor.py         # 核心提取逻辑
│   ├── models/              # 数据模型
│   │   ├── schemas.py       # 业务数据模型
│   │   └── log_schemas.py   # 日志数据模型
│   ├── llm/                 # LLM 调用层
│   │   ├── zhipu_client.py  # 智谱客户端封装
│   │   └── prompts.py       # 提示词模板
│   ├── graph/               # 数据库层
│   │   └── neo4j_client.py  # Neo4j 客户端封装
│   └── logger/              # 日志系统
│       └── log_storage.py   # SQLite 日志存储
├── data/                    # 数据目录
│   ├── input/               # 输入文本
│   └── output/              # 输出结果
├── logs/                    # 日志数据库目录
│   └── app.db               # SQLite 日志数据库
├── tests/                   # 测试文件
│   ├── test_api.py          # API 测试
│   ├── test_models.py       # 模型检测
│   ├── test_neo4j.py        # Neo4j 测试
│   ├── test_logs.py         # 日志查询工具
│   ├── test_thinking*.py    # 深度思考测试
│   └── debug_*.py           # 调试脚本
└── examples/                # 使用示例
    ├── basic_usage.py       # 基本使用
    ├── async_example.py     # 异步调用示例
    └── performance_comparison.py  # 性能对比测试
```

## 快速开始

### 1. 环境准备

确保已安装以下环境：
- Python 3.10 或更高版本
- Neo4j 数据库（Docker 或本地安装）

### 2. 安装 Neo4j

使用 Docker 快速启动：

```bash
docker pull neo4j:5.15
docker run -d \
  --name neo4j \
  -p 7474:7474 \
  -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/your_password \
  -e NEO4J_PLUGINS='["apoc"]' \
  neo4j:5.15
```

访问 Neo4j Browser: http://localhost:7474

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

复制 `.env.example` 为 `.env` 并填写配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
# 智谱 AI 配置
ZHIPU_API_KEY=your_api_key_here

# Neo4j 配置
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password_here
```

### 5. 运行示例

```python
from src.extractor import RelationshipExtractor

# 初始化提取器
extractor = RelationshipExtractor()

# 提取文本中的实体和关系
text = "马云是阿里巴巴集团的创始人，阿里巴巴总部位于杭州。"
result = extractor.extract(text)

# 结果自动保存到 Neo4j
print(result)
# 输出: {
#   "entities": [
#     {"name": "马云", "type": "Person"},
#     {"name": "阿里巴巴集团", "type": "Organization"},
#     {"name": "杭州", "type": "Location"}
#   ],
#   "relations": [
#     {"from": "马云", "to": "阿里巴巴集团", "type": "创始人"},
#     {"from": "阿里巴巴集团", "to": "杭州", "type": "总部位于"}
#   ]
# }
```

### 6. 异步批量处理

对于大量文本的处理，可以使用异步批量提取来提升性能：

```python
import asyncio
from src.extractor import RelationshipExtractor

async def batch_extract():
    # 异步批量提取
    extractor = RelationshipExtractor(auto_save=False)

    texts = [
        "马云是阿里巴巴的创始人",
        "华为推出自主研发的MetaERP系统",
        "金蝶软件是国内领先的企业管理软件供应商"
    ]

    # 并发提取（默认并发数为5）
    results = await extractor.extract_batch_async(texts, concurrency=3)

    for i, result in enumerate(results, 1):
        print(f"文本 {i}: {len(result.entities)} 个实体, {len(result.relations)} 个关系")

    extractor.close()

# 运行异步任务
asyncio.run(batch_extract())
```

**性能对比**（测试10条文本）：
- 同步处理：~58秒
- 异步处理（并发5）：~15秒
- **提速 3.9 倍**

### 7. 深度思考模式

启用深度思考模式可以提升复杂文本的提取准确性：

```python
from src.extractor import RelationshipExtractor

# 方式1：在 .env 中全局启用
# ENABLE_THINKING=true

# 方式2：代码中指定
extractor = RelationshipExtractor(auto_save=False)

# 启用深度思考
result = extractor.extract(
    "华为在2024年推出MetaERP系统，旨在替代原有Oracle系统，实现企业软件自主化。",
    enable_thinking=True
)

print(f"实体数: {len(result.entities)}")
print(f"关系数: {len(result.relations)}")

extractor.close()
```

**深度思考效果**：
- ✅ 更准确地识别隐含关系
- ✅ 提取更多实体和关系
- ⚠️ 响应时间增加约 50-100%
- ⚠️ Token 消耗增加约 30-50%

### 8. 查看知识图谱

访问 Neo4j Browser 执行查询：

```cypher
// 查看所有节点和关系
MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 100

// 查找特定实体的关系网络
MATCH (n {name: "马云"})-[r]-(m) RETURN n, r, m
```

### 9. 查看操作日志

项目自动记录所有 LLM 调用和 Neo4j 操作到 SQLite 日志数据库：

```bash
# 查看日志统计
python tests/test_logs.py --stats

# 查看 LLM 调用日志（最近 10 条）
python tests/test_logs.py --llm

# 查看 Neo4j 操作日志（最近 10 条）
python tests/test_logs.py --neo4j

# 清理 30 天前的旧日志
python tests/test_logs.py --clear 30
```

**日志内容**：
- **LLM 日志**: 请求/响应内容、Token 消耗、耗时、模型版本、**深度思考内容**（如果启用）
- **Neo4j 日志**: Cypher 查询、参数、影响行数、耗时

日志数据库位置：`logs/app.db`（SQLite 格式）

## 配置说明

### 智谱 AI 配置

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `ZHIPU_API_KEY` | 智谱 AI API 密钥 | - |
| `ZHIPU_API_BASE` | 智谱 API 地址 | `https://open.bigmodel.cn/api/coding/paas/v4` |
| `ZHIPU_MODEL` | 使用的模型名称 | `glm-4.5-air` |
| `LLM_TEMPERATURE` | LLM 温度参数 | `0.7` |
| `LLM_MAX_TOKENS` | LLM 最大 token 数 | `2000` |

**可用模型**: `glm-4.5`, `glm-4.5-air`, `glm-4.6`, `glm-4.7`, `glm-5`, `glm-5-turbo`, `glm-5.1`

### 深度思考配置

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `ENABLE_THINKING` | 是否启用深度思考模式 | `false` |
| `THINKING_TYPE` | 思考模式类型 (enabled/disabled/auto) | `auto` |

**注意**: 启用深度思考后会提高复杂文本的提取准确性，但会增加响应时间和 Token 消耗。

### Neo4j 配置

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `NEO4J_URI` | Neo4j 连接地址 | `bolt://localhost:7687` |
| `NEO4J_USER` | Neo4j 用户名 | `neo4j` |
| `NEO4J_PASSWORD` | Neo4j 密码 | - |

### 日志配置

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `LOG_DB_PATH` | 日志数据库路径 | `logs/app.db` |
| `ENABLE_LLM_LOGGING` | 启用 LLM 日志 | `true` |
| `ENABLE_NEO4J_LOGGING` | 启用 Neo4j 日志 | `true` |
| `LOG_RETENTION_DAYS` | 日志保留天数 | `30` |

### 应用配置

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `LOG_LEVEL` | 日志级别 | `INFO` |

## 开发计划

- [x] 项目初始化
- [x] 实现智谱 AI 接口封装
- [x] 实现 Neo4j 连接与操作封装
- [x] 设计实体与关系提取提示词
- [x] 实现核心提取逻辑
- [x] 实现日志系统（LLM + Neo4j）
- [x] 添加日志查询工具
- [x] **实现异步批量处理**
- [x] **集成深度思考模式**
- [ ] 添加单元测试
- [ ] 支持批量文本处理
- [ ] 添加结果导出功能（JSON/CSV）
- [ ] 开发 REST API 接口
- [ ] 添加 Web 可视化界面

## 贡献指南

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 作者

**ppw2004** - [GitHub](https://github.com/ppw2004)

## 联系方式

如有问题或建议，欢迎通过 Issue 联系。
